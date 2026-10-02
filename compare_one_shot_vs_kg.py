from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from compare_physics import align_trajectories
from compute_l2_errors import compute_metrics, load_np

ROOT = Path(__file__).resolve().parent
DOMAINS = ["heat_flow", "burgers2d", "julia_set", "lid_driven_cavity", "reaction_diffusion", "smoke_plume", "wake_flow"]

TRAJECTORIES = {
    "heat_flow": [("heat_flow_temperature_trj.npy", "heat_flow_ground_truth_trj.npy")],
    "burgers2d": [("burgers2d_velocity_trj.npy", "burgers2d_ground_truth_trj.npy")],
    "julia_set": [("julia_set_domain_trj_nocon.npy", "julia_set_ground_truth_trj.npy")],
    "reaction_diffusion": [
        ("reaction_diffusion_u_trj.npy", "reaction_diffusion_ground_truth_u_trj.npy"),
        ("reaction_diffusion_v_trj.npy", "reaction_diffusion_ground_truth_v_trj.npy"),
    ],
}

KG_TRAJECTORIES = {
    **TRAJECTORIES,
    "julia_set": [("julia_set_domain_trj.npy", "julia_set_ground_truth_trj.npy")],
}


def run_script(script_path: Path, output_dir: Path, timeout: int) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        compile(script_path.read_text(encoding="utf-8"), str(script_path), "exec")
    except SyntaxError as exc:
        return {"syntax_ok": False, "execution_ok": False, "error": f"{exc.msg} at line {exc.lineno}"}

    try:
        result = subprocess.run(
            [sys.executable, str(script_path.resolve())],
            cwd=output_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "syntax_ok": True,
            "execution_ok": result.returncode == 0,
            "exit_code": result.returncode,
            "duration_s": round(time.perf_counter() - start, 3),
            "stderr_tail": result.stderr[-500:],
        }
    except subprocess.TimeoutExpired:
        return {"syntax_ok": True, "execution_ok": False, "timeout": True, "duration_s": round(time.perf_counter() - start, 3)}


def measure(output_dir: Path, domain: str, trajectories: dict[str, list[tuple[str, str]]] = TRAJECTORIES) -> dict[str, Any]:
    values = []
    statuses = []
    for generated_name, ground_truth_name in trajectories.get(domain, []):
        generated_path = output_dir / generated_name
        ground_truth_path = ROOT / f"test_{domain}" / ground_truth_name
        if not generated_path.exists() or not ground_truth_path.exists():
            statuses.append("artifact_missing")
            continue
        try:
            generated, ground_truth = align_trajectories(load_np(str(generated_path)), load_np(str(ground_truth_path)))
            metrics = compute_metrics(generated, ground_truth)
            reference_rms = float(np.sqrt(np.mean(np.square(ground_truth))))
            relative_rmse = metrics["rmse"] / max(reference_rms, 1e-12)
            values.append({
                "relative_rmse": relative_rmse,
                "mean_l2": metrics["mean_l2"],
                "physics_score": 1.0 / (1.0 + relative_rmse),
            })
            statuses.append("measured")
        except Exception as exc:
            statuses.append(f"comparison_error: {exc}")

    return {
        "measured_components": sum(status == "measured" for status in statuses),
        "component_count": len(statuses),
        "statuses": statuses,
        "mean_relative_rmse": float(np.mean([v["relative_rmse"] for v in values])) if values else None,
        "mean_l2": float(np.mean([v["mean_l2"] for v in values])) if values else None,
        "physics_score": float(np.mean([v["physics_score"] for v in values])) if values else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare one-shot generated_code.py against KG-generated configurations.")
    parser.add_argument("--report", type=Path, default=ROOT / "optimization_runs/pruned_cross_domain/cross_domain_execution.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "optimization_runs/one_shot_comparison")
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    one_shot_results = {}
    for domain in DOMAINS:
        output_dir = args.output_dir / domain
        output_dir.mkdir(parents=True, exist_ok=True)
        run = run_script(ROOT / f"test_{domain}" / "generated_code.py", output_dir, args.timeout)
        one_shot_results[domain] = {"run": run, "quality": measure(output_dir, domain)}
        print(f"one-shot {domain}: execution={run.get('execution_ok', False)} measured={one_shot_results[domain]['quality']['measured_components']}/{one_shot_results[domain]['quality']['component_count']}")

    report = json.loads(args.report.read_text(encoding="utf-8"))
    rows = []
    for result in report.get("results", []):
        config_id = result["config_id"]
        config_dir = args.report.parent / "cross_domain" / config_id
        for domain in DOMAINS:
            kg_row = next(row for row in result["domains"] if row["domain"] == domain)
            kg_quality = measure(config_dir / domain, domain, KG_TRAJECTORIES)
            rows.append({
                "config_id": config_id,
                "domain": domain,
                "one_shot_execution": one_shot_results[domain]["run"].get("execution_ok", False),
                "kg_execution": kg_row["execution"].get("execution_ok", False),
                "one_shot_physics_score": one_shot_results[domain]["quality"]["physics_score"],
                "kg_physics_score": kg_quality["physics_score"],
                "one_shot_relative_rmse": one_shot_results[domain]["quality"]["mean_relative_rmse"],
                "kg_relative_rmse": kg_quality["mean_relative_rmse"],
                "one_shot_measured": f"{one_shot_results[domain]['quality']['measured_components']}/{one_shot_results[domain]['quality']['component_count']}",
                "kg_measured": f"{kg_quality['measured_components']}/{kg_quality['component_count']}",
            })

    csv_path = args.csv or args.report.parent / "one_shot_vs_kg.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {csv_path}")
    print("domain                 one-shot  KG configs  one-shot RMSE  KG RMSE")
    for domain in DOMAINS:
        domain_rows = [row for row in rows if row["domain"] == domain]
        one = domain_rows[0]
        kg_values = [row["kg_relative_rmse"] for row in domain_rows if row["kg_relative_rmse"] is not None]
        kg_rmse = float(np.mean(kg_values)) if kg_values else None
        print(f"{domain:22} {str(one['one_shot_execution']):8}  {sum(row['kg_execution'] for row in domain_rows)}/{len(domain_rows):<10} {str(one['one_shot_relative_rmse']):14} {str(kg_rmse)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())