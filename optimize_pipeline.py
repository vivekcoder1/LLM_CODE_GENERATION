
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
TASKS = ["heat_flow", "burgers2d", "julia_set", "lid_driven_cavity", "reaction_diffusion", "smoke_plume", "structural_mechanics", "wake_flow"]
CROSS_DOMAIN_TASKS = [task for task in TASKS if task != "structural_mechanics"]
PARAMETER_GRID = {
    "top_k": [12, 32],
    "min_score": [0.15, 0.20],
    "method_min_score": [0.30, 0.50],
    "max_methods_per_class": [2, 5],
    "max_nodes": [12],
    "fulltext_limit": [3, 5, 8],
    "description_limit": [3, 5, 8],
    "function_limit": [2, 4, 6],
    "class_limit": [2, 4, 6],
}


def load_pipeline_class():
    spec = importlib.util.spec_from_file_location("llm_querying", ROOT / "llm-querying.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load llm-querying.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.E2ERagPipeline


def task_terms(text: str) -> set[str]:
    stopwords = {"about", "after", "also", "and", "are", "from", "into", "that", "the", "their", "this", "using", "with", "which", "will"}
    return {word.lower() for word in re.findall(r"[A-Za-z][A-Za-z0-9_]{3,}", text) if word.lower() not in stopwords}


def config_id(config: dict[str, Any]) -> str:
    encoded = json.dumps(config, sort_keys=True).encode("utf-8")
    return hashlib.sha1(encoded).hexdigest()[:12]


def stable_domain_seed(domain: str) -> int:
    return int(hashlib.sha1(domain.encode("utf-8")).hexdigest()[:8], 16)


def sample_configs(trials: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    configs = []
    seen = set()
    while len(configs) < trials:
        config = {name: rng.choice(values) for name, values in PARAMETER_GRID.items()}
        config["class_limit"] = config["function_limit"]
        key = config_id(config)
        if key not in seen:
            seen.add(key)
            configs.append(config)
    return configs


def retrieval_score(context: str, task: str, config: dict[str, Any]) -> dict[str, float]:
    terms = task_terms(task)
    lower_context = context.lower()
    coverage = sum(term in lower_context for term in terms) / max(len(terms), 1)
    chars = len(context)
    size_score = min(chars / 12000.0, 1.0)
    compactness = max(0.0, 1.0 - max(chars - 16000, 0) / 16000.0)
    public_api_count = context.count("**Import Path:**")
    api_score = min(public_api_count / 12.0, 1.0)
    # Favor relevant, usable context while  penalizing bloated prompts.
    score = 0.55 * coverage + 0.25 * api_score + 0.20 * compactness
    return {
        "retrieval_score": round(score, 6),
        "task_term_coverage": round(coverage, 6),
        "context_chars": chars,
        "context_tokens_approx": round(chars / 4),
        "public_api_count": public_api_count,
        "size_score": round(size_score, 6),
        "compactness": round(compactness, 6),
    }


def execute_script(script_path: Path, timeout: int) -> dict[str, Any]:
    script_path = script_path.resolve()
    start = time.perf_counter()
    try:
        compile(script_path.read_text(encoding="utf-8"), str(script_path), "exec")
    except SyntaxError as exc:
        return {"syntax_ok": False, "execution_ok": False, "error": f"{exc.msg} at line {exc.lineno}"}

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "syntax_ok": True,
            "execution_ok": result.returncode == 0,
            "exit_code": result.returncode,
            "duration_s": round(time.perf_counter() - start, 3),
            "stderr_tail": result.stderr[-1000:],
        }
    except subprocess.TimeoutExpired:
        return {"syntax_ok": True, "execution_ok": False, "timeout": True, "duration_s": round(time.perf_counter() - start, 3)}


def run_cross_domain_execution(args: argparse.Namespace, pipeline: Any, cache_dir: Path) -> int:
    """Generate and execute every shared configuration across the seven selected domains."""
    configs = sample_configs(args.trials, args.seed)
    rows = []
    try:
        for domain in CROSS_DOMAIN_TASKS:
            task = (ROOT / "test" / f"{domain}.md").read_text(encoding="utf-8")
            task_hash = hashlib.sha1(task.encode("utf-8")).hexdigest()[:12]
            blueprint_path = cache_dir / f"{domain}_{task_hash}_blueprint.json"
            blueprint = json.loads(blueprint_path.read_text(encoding="utf-8")) if blueprint_path.exists() else {}
            if not any(blueprint.get(key) for key in ("semantic_queries", "target_classes", "target_functions")):
                blueprint = pipeline.generate_search_blueprint(task)
            if not any(blueprint.get(key) for key in ("semantic_queries", "target_classes", "target_functions")):
                print(f"{domain}: skipped because the search blueprint is empty")
                continue
            blueprint_path.write_text(json.dumps(blueprint, indent=2), encoding="utf-8")

            for config in configs:
                config_key = config_id(config)
                result_path = cache_dir / f"{domain}_{config_key}.json"
                if result_path.exists():
                    retrieval = json.loads(result_path.read_text(encoding="utf-8"))
                else:
                    seed_ids = pipeline.find_seed_nodes(blueprint, **{key: config[key] for key in ("fulltext_limit", "description_limit", "function_limit", "class_limit")})
                    raw = pipeline.traverse_subgraph(seed_ids)
                    filtered = pipeline.filter_subgraph(task, raw, **{key: config[key] for key in ("top_k", "min_score", "method_min_score", "max_methods_per_class")})
                    context = pipeline.serialize_subgraph(filtered, max_nodes=config["max_nodes"])
                    retrieval = {"domain": domain, "config_id": config_key, "config": config, "seed_count": len(seed_ids), "raw_count": len(raw), "filtered_count": len(filtered), "metrics": retrieval_score(context, task, config)}
                    (cache_dir / f"{domain}_{config_key}.md").write_text(context, encoding="utf-8")
                    result_path.write_text(json.dumps(retrieval, indent=2), encoding="utf-8")

                candidate_dir = args.output_dir / "cross_domain" / config_key / domain
                candidate_dir.mkdir(parents=True, exist_ok=True)
                script_path = candidate_dir / f"generated_{domain}_simulation.py"
                context_path = cache_dir / f"{domain}_{config_key}.md"
                if not script_path.exists():
                    code = pipeline.generate_grounded_code(task, context_path.read_text(encoding="utf-8"), max_tokens=args.generation_max_tokens)
                    script_path.write_text(code, encoding="utf-8")
                execution = execute_script(script_path, args.execution_timeout)
                rows.append({"domain": domain, "config_id": config_key, "config": config, "retrieval_score": retrieval["metrics"]["retrieval_score"], "execution": execution})
                print(f"{domain} / {config_key}: execution={execution['execution_ok']}")
    finally:
        pipeline.close()

    summary = []
    for config in configs:
        config_key = config_id(config)
        domain_rows = [row for row in rows if row["config_id"] == config_key]
        successful = sum(row["execution"].get("execution_ok", False) for row in domain_rows)
        summary.append({"config_id": config_key, "config": config, "successful_domains": successful, "tested_domains": len(domain_rows), "domains": domain_rows})
    summary.sort(key=lambda row: (row["successful_domains"], row["tested_domains"]), reverse=True)
    report_path = args.output_dir / "cross_domain_execution.json"
    report_path.write_text(json.dumps({"domains": CROSS_DOMAIN_TASKS, "trials": args.trials, "results": summary}, indent=2), encoding="utf-8")
    csv_path = args.output_dir / "cross_domain_execution_summary.csv"
    fields = [
        "rank", "config_id", *PARAMETER_GRID.keys(), "successful_domains", "tested_domains", "execution_rate",
        *CROSS_DOMAIN_TASKS,
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for rank, result in enumerate(summary, start=1):
            domain_status = {
                row["domain"]: "PASS" if row["execution"].get("execution_ok", False) else "FAIL"
                for row in result["domains"]
            }
            tested = result["tested_domains"]
            success = result["successful_domains"]
            writer.writerow({
                "rank": rank,
                "config_id": result["config_id"],
                **result["config"],
                "successful_domains": success,
                "tested_domains": tested,
                "execution_rate": round(success / tested, 4) if tested else 0.0,
                **domain_status,
            })

    print("\nCross-domain execution ranking:")
    print("rank  execution  config_id    " + " ".join(f"{domain[:8]:8}" for domain in CROSS_DOMAIN_TASKS))
    for rank, result in enumerate(summary, start=1):
        tested = result["tested_domains"]
        success = result["successful_domains"]
        statuses = {row["domain"]: row["execution"].get("execution_ok", False) for row in result["domains"]}
        markers = " ".join(f"{'PASS' if statuses.get(domain, False) else 'FAIL':8}" for domain in CROSS_DOMAIN_TASKS)
        rate = 100 * success / tested if tested else 0.0
        print(f"{rank:>4}  {success}/{tested} ({rate:>5.1f}%)  {result['config_id']}  {markers}")
    print(f"Wrote {report_path}")
    print(f"Wrote {csv_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260916)
    parser.add_argument("--top-per-task", type=int, default=5)
    parser.add_argument("--generate-top", type=int, default=0, help="Claude generations per task; default 0")
    parser.add_argument("--generation-max-tokens", type=int, default=20000)
    parser.add_argument("--cross-domain-execution", action="store_true", help="Test every shared configuration across all non-structural domains")
    parser.add_argument("--execution-timeout", type=int, default=120)
    parser.add_argument("--tasks", nargs="+", choices=TASKS, default=TASKS)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "optimization_runs")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = args.output_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    Pipeline = load_pipeline_class()
    pipeline = Pipeline()
    if args.cross_domain_execution:
        return run_cross_domain_execution(args, pipeline, cache_dir)
    all_rows = []

    try:
        for domain in args.tasks:
            task_path = ROOT / "test" / f"{domain}.md"
            task = task_path.read_text(encoding="utf-8")
            task_hash = hashlib.sha1(task.encode("utf-8")).hexdigest()[:12]
            blueprint_path = cache_dir / f"{domain}_{task_hash}_blueprint.json"
            if blueprint_path.exists():
                blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
                if not any(blueprint.get(key) for key in ("semantic_queries", "target_classes", "target_functions")):
                    blueprint = pipeline.generate_search_blueprint(task)
            else:
                blueprint = pipeline.generate_search_blueprint(task)

            if any(blueprint.get(key) for key in ("semantic_queries", "target_classes", "target_functions")):
                blueprint_path.write_text(json.dumps(blueprint, indent=2), encoding="utf-8")

            if not any(blueprint.get(key) for key in ("semantic_queries", "target_classes", "target_functions")):
                print(f"{domain}: skipped because the search blueprint is empty")
                all_rows.append({"domain": domain, "status": "empty_blueprint"})
                continue

            domain_rows = []
            for config in sample_configs(args.trials, args.seed + stable_domain_seed(domain) % 10000):
                result_path = cache_dir / f"{domain}_{config_id(config)}.json"
                if result_path.exists():
                    row = json.loads(result_path.read_text(encoding="utf-8"))
                else:
                    seed_ids = pipeline.find_seed_nodes(blueprint, **{key: config[key] for key in ("fulltext_limit", "description_limit", "function_limit", "class_limit")})
                    raw = pipeline.traverse_subgraph(seed_ids)
                    filtered = pipeline.filter_subgraph(task, raw, **{key: config[key] for key in ("top_k", "min_score", "method_min_score", "max_methods_per_class")})
                    context = pipeline.serialize_subgraph(filtered, max_nodes=config["max_nodes"])
                    row = {"domain": domain, "config_id": config_id(config), "config": config, "seed_count": len(seed_ids), "raw_count": len(raw), "filtered_count": len(filtered), "metrics": retrieval_score(context, task, config)}
                    (cache_dir / f"{domain}_{config_id(config)}.md").write_text(context, encoding="utf-8")
                    result_path.write_text(json.dumps(row, indent=2), encoding="utf-8")
                domain_rows.append(row)

            domain_rows.sort(key=lambda row: row["metrics"]["retrieval_score"], reverse=True)
            selected = domain_rows[:args.top_per_task]
            for rank, row in enumerate(selected, start=1):
                row["rank"] = rank
                row["generation_requested"] = rank <= args.generate_top
                if rank <= args.generate_top:
                    candidate_dir = args.output_dir / domain / f"rank_{rank}_{row['config_id']}"
                    candidate_dir.mkdir(parents=True, exist_ok=True)
                    context_path = cache_dir / f"{domain}_{row['config_id']}.md"
                    context = context_path.read_text(encoding="utf-8")
                    code = pipeline.generate_grounded_code(task, context, max_tokens=args.generation_max_tokens)
                    (candidate_dir / f"generated_{domain}_simulation.py").write_text(code, encoding="utf-8")
                    shutil.copy2(context_path, candidate_dir / "retrieved_context.md")
                all_rows.append(row)
            print(f"{domain}: best retrieval score={selected[0]['metrics']['retrieval_score']:.4f}; selected {len(selected)}")
    finally:
        pipeline.close()

    report_path = args.output_dir / "optimization_results.json"
    report_path.write_text(json.dumps({"trials_per_task": args.trials, "top_per_task": args.top_per_task, "generate_top": args.generate_top, "generation_max_tokens": args.generation_max_tokens, "results": all_rows}, indent=2), encoding="utf-8")
    csv_path = args.output_dir / "optimization_results.csv"
    fields = ["domain", "status", "rank", "config_id", "retrieval_score", "task_term_coverage", "context_chars", "context_tokens_approx", "seed_count", "raw_count", "filtered_count", "generation_requested"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({field: row.get(field, row.get("metrics", {}).get(field, "")) for field in fields})
    print(f"Wrote {report_path} and {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())