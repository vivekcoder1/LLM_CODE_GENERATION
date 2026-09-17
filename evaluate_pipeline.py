"""Evaluate generated PhiFlow scripts and their retrieved contexts in one report.

This evaluator deliberately separates observable criteria:
syntax, execution, output artifacts, context size/ordering, API evidence coverage,
and numerical agreement where a ground-truth trajectory is available.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import re
import string
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from compare_physics import align_trajectories
from compute_l2_errors import compute_metrics, load_np


DOMAINS = [
    "burgers2d",
    "heat_flow",
    "julia_set",
    "lid_driven_cavity",
    "reaction_diffusion",
    "smoke_plume",
    "structural_mechanics",
    "wake_flow",
]

TRAJECTORY_PAIRS = {
    "burgers2d": [("main", "burgers2d_trj.npy", "burgers2d_ground_truth.npy")],
    "heat_flow": [("main", "heat_flow_trj.npy", "heat_flow_ground_truth.npy")],
    "julia_set": [("main", "julia_set_domain_trj.npy", "julia_set_ground_truth_trj.npy")],
    "reaction_diffusion": [
        ("u", "reaction_diffusion_u_trj.npy", "reaction_diffusion_ground_truth_u_trj.npy"),
        ("v", "reaction_diffusion_v_trj.npy", "reaction_diffusion_ground_truth_v_trj.npy"),
    ],
}


def explicit_imports(script_path: Path) -> list[str]:
    tree = ast.parse(script_path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            names.extend(alias.asname or alias.name for alias in node.names if alias.name != "*")
        elif isinstance(node, ast.Import):
            names.extend(alias.asname or alias.name.split(".")[0] for alias in node.names)
    return sorted(set(names))


STOPWORDS = {
    "about", "after", "also", "and", "are", "from", "into", "that", "the", "their",
    "there", "these", "this", "using", "with", "within", "which", "will", "would",
}


def context_metrics(context_path: Path, symbols: list[str], task_path: Path) -> dict[str, Any]:
    text = context_path.read_text(encoding="utf-8") if context_path.exists() else ""
    task_text = task_path.read_text(encoding="utf-8") if task_path.exists() else ""
    task_terms = {
        token.lower().strip(string.punctuation)
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_]{3,}", task_text)
        if token.lower() not in STOPWORDS
    }
    context_lower = text.lower()
    covered_task_terms = [term for term in task_terms if term in context_lower]
    positions = {}
    for symbol in symbols:
        match = re.search(rf"(?<![A-Za-z0-9_]){re.escape(symbol)}(?![A-Za-z0-9_])", text)
        if match:
            positions[symbol] = round(match.start() / max(len(text), 1), 4)

    covered = [symbol for symbol in symbols if symbol in positions]
    middle = [symbol for symbol, position in positions.items() if 1 / 3 <= position <= 2 / 3]
    return {
        "context_exists": context_path.exists(),
        "context_chars": len(text),
        "context_tokens_approx": round(len(text) / 4),
        "context_sections": len(re.findall(r"^#{2,3} ", text, flags=re.MULTILINE)),
        "context_import_paths": len(re.findall(r"\*\*Import Path:\*\*", text)),
        "task_term_count": len(task_terms),
        "task_term_coverage": round(len(covered_task_terms) / len(task_terms), 4) if task_terms else None,
        "explicit_import_count": len(symbols),
        "explicit_import_coverage": round(len(covered) / len(symbols), 4) if symbols else None,
        "evidence_positions": positions,
        "evidence_in_middle_fraction": round(len(middle) / len(covered), 4) if covered else None,
    }


def run_script(script_path: Path, timeout: int) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        compile(script_path.read_text(encoding="utf-8"), str(script_path), "exec")
        syntax_ok = True
        syntax_error = ""
    except SyntaxError as exc:
        syntax_ok = False
        syntax_error = f"{exc.msg} at line {exc.lineno}"

    if not syntax_ok:
        return {"syntax_ok": False, "syntax_error": syntax_error, "execution_ok": False, "duration_s": 0.0}

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
            "syntax_error": "",
            "execution_ok": result.returncode == 0,
            "exit_code": result.returncode,
            "duration_s": round(time.perf_counter() - start, 3),
            "stderr_tail": result.stderr[-500:],
        }
    except subprocess.TimeoutExpired:
        return {
            "syntax_ok": True,
            "syntax_error": "",
            "execution_ok": False,
            "timeout": True,
            "duration_s": round(time.perf_counter() - start, 3),
            "stderr_tail": "timeout",
        }


def numerical_metrics(domain_dir: Path, pair: tuple[str, str, str]) -> dict[str, Any]:
    label, generated_name, ground_truth_name = pair
    generated_path = domain_dir / generated_name
    ground_truth_path = domain_dir / ground_truth_name
    result: dict[str, Any] = {
        "label": label,
        "generated_exists": generated_path.exists(),
        "ground_truth_exists": ground_truth_path.exists(),
    }
    if not generated_path.exists() or not ground_truth_path.exists():
        result["status"] = "reference_unavailable" if not ground_truth_path.exists() else "generated_artifact_missing"
        return result

    try:
        generated, ground_truth = align_trajectories(load_np(str(generated_path)), load_np(str(ground_truth_path)))
        metrics = compute_metrics(generated, ground_truth)
        reference_rms = float(np.sqrt(np.mean(np.square(ground_truth))))
        relative_rmse = metrics["rmse"] / max(reference_rms, 1e-12)
        result.update(
            {
                "status": "measured",
                "shape": list(generated.shape),
                "mean_l2": metrics["mean_l2"],
                "max_l2": metrics["max_l2"],
                "rmse": metrics["rmse"],
                "relative_rmse": relative_rmse,
                "physics_score": 1.0 / (1.0 + relative_rmse),
            }
        )
    except Exception as exc:
        result.update({"status": "comparison_error", "error": str(exc), "physics_score": 0.0})
    return result


def aggregate_score(run: dict[str, Any], context: dict[str, Any], numerical: list[dict[str, Any]]) -> float:
    components = [(0.25, float(run.get("execution_ok", False))), (0.05, float(run.get("syntax_ok", False)))]
    context_score = 0.5 * float((context.get("context_chars", 0) >= 200))
    context_score += 0.5 * float(context.get("task_term_coverage") or 0.0)
    components.append((0.20, context_score))
    measured_or_failed = [item["physics_score"] for item in numerical if item.get("status") in ("measured", "comparison_error")]
    if measured_or_failed:
        components.append((0.50, float(np.mean(measured_or_failed))))
    total_weight = sum(weight for weight, _ in components)
    return round(100 * sum(weight * value for weight, value in components) / total_weight, 3)


def evaluate_domain(base_dir: Path, domain: str, timeout: int) -> dict[str, Any]:
    domain_dir = base_dir / f"test_{domain}"
    script_path = domain_dir / f"generated_{domain}_simulation.py"
    context_path = domain_dir / "retrieved_context.md"
    task_path = base_dir / "test" / f"{domain}.md"
    run = run_script(script_path, timeout) if script_path.exists() else {"syntax_ok": False, "execution_ok": False, "missing_script": True}
    symbols = explicit_imports(script_path) if script_path.exists() else []
    context = context_metrics(context_path, symbols, task_path)
    numerical = [numerical_metrics(domain_dir, pair) for pair in TRAJECTORY_PAIRS.get(domain, [])]
    return {
        "domain": domain,
        "script": str(script_path),
        "context": context,
        "run": run,
        "numerical": numerical,
        "objective_score_coverage": 1.0 if any(item.get("status") in ("measured", "comparison_error") for item in numerical) else 0.5,
        "objective_score": aggregate_score(run, context, numerical),
    }


def write_csv(results: list[dict[str, Any]], path: Path) -> None:
    rows = []
    for result in results:
        measured = [item for item in result["numerical"] if item.get("status") == "measured"]
        rows.append(
            {
                "domain": result["domain"],
                "objective_score": result["objective_score"],
                "objective_score_coverage": result["objective_score_coverage"],
                "syntax_ok": result["run"].get("syntax_ok", False),
                "execution_ok": result["run"].get("execution_ok", False),
                "duration_s": result["run"].get("duration_s", ""),
                "context_chars": result["context"].get("context_chars", 0),
                "context_tokens_approx": result["context"].get("context_tokens_approx", 0),
                "import_coverage": result["context"].get("explicit_import_coverage", ""),
                "relative_rmse": round(float(np.mean([item["relative_rmse"] for item in measured])), 6) if measured else "",
                "physics_score": round(float(np.mean([item["physics_score"] for item in measured])), 6) if measured else "",
                "reference_status": ";".join(item.get("status", "") for item in result["numerical"]) or "not_applicable",
            }
        )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["domain"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate generated PhiFlow pipeline outputs.")
    parser.add_argument("--base-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--domains", nargs="+", choices=DOMAINS, default=DOMAINS)
    parser.add_argument("--json", type=Path, default=Path("evaluation_report.json"))
    parser.add_argument("--csv", type=Path, default=Path("evaluation_report.csv"))
    args = parser.parse_args()

    results = [evaluate_domain(args.base_dir, domain, args.timeout) for domain in args.domains]
    report = {
        "criteria": {
            "syntax": "generated script parses as Python",
            "execution": "generated script exits successfully within timeout",
            "context": "context size, sections, import-path count, and explicit-import evidence coverage",
            "position": "fraction of cited import evidence occurring in the middle third of context",
            "physics": "reference-relative RMSE and bounded score 1 / (1 + relative RMSE), when ground truth exists",
            "objective_score": "weighted observable score; physics component is omitted when no reference exists",
        },
        "research_basis": [
            "Liu et al., Lost in the Middle, arXiv:2307.03172",
            "Es et al., Ragas, arXiv:2309.15217",
            "Saad-Falcon et al., ARES, arXiv:2311.09476",
        ],
        "results": results,
    }
    args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_csv(results, args.csv)

    for result in results:
        run = result["run"]
        context = result["context"]
        print(
            f"{result['domain']:22} score={result['objective_score']:6.2f} "
            f"syntax={run.get('syntax_ok', False)} execution={run.get('execution_ok', False)} "
            f"context={context.get('context_tokens_approx', 0)} tokens"
        )
    print(f"Wrote {args.json} and {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())