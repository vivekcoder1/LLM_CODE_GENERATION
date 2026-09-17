"""Token-efficient overnight search for PhiFlow RAG retrieval parameters.

Default mode performs retrieval-only trials and makes no Claude generation calls.
Use --generate-top N to generate code only for the best N configurations per task.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import random
import re
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
TASKS = ["heat_flow", "burgers2d", "julia_set", "lid_driven_cavity", "reaction_diffusion", "smoke_plume", "structural_mechanics", "wake_flow"]
PARAMETER_GRID = {
    "top_k": [12, 18, 24, 32, 48],
    "min_score": [0.05, 0.10, 0.15, 0.20, 0.25],
    "method_min_score": [0.20, 0.30, 0.40, 0.50],
    "max_methods_per_class": [1, 2, 3, 5],
    "public_boost": [0.00, 0.10, 0.20, 0.30],
    "private_penalty": [0.00, 0.10, 0.15, 0.25],
    "max_nodes": [8, 12, 18, 24, 32],
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
    # Favor relevant, usable context while mildly penalizing bloated prompts.
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260916)
    parser.add_argument("--top-per-task", type=int, default=5)
    parser.add_argument("--generate-top", type=int, default=0, help="Claude generations per task; default 0")
    parser.add_argument("--generation-max-tokens", type=int, default=6000)
    parser.add_argument("--tasks", nargs="+", choices=TASKS, default=TASKS)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "optimization_runs")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = args.output_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    Pipeline = load_pipeline_class()
    pipeline = Pipeline()
    all_rows = []

    try:
        for domain in args.tasks:
            task_path = ROOT / "test" / f"{domain}.md"
            task = task_path.read_text(encoding="utf-8")
            task_hash = hashlib.sha1(task.encode("utf-8")).hexdigest()[:12]
            blueprint_path = cache_dir / f"{domain}_{task_hash}_blueprint.json"
            if blueprint_path.exists():
                blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
            else:
                blueprint = pipeline.generate_search_blueprint(task)
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
                    filtered = pipeline.filter_subgraph(task, raw, **{key: config[key] for key in ("top_k", "min_score", "method_min_score", "max_methods_per_class", "public_boost", "private_penalty")})
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