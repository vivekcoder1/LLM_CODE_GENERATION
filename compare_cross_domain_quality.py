from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

from compare_physics import align_trajectories
from compute_l2_errors import compute_metrics, load_np

ROOT = Path(__file__).resolve().parent
DEFAULT_REPORT = ROOT / "optimization_runs" / "cross_domain_execution.json"
DEFAULT_OUTPUT = ROOT / "optimization_runs" / "cross_domain_quality_ranking.csv"

DOMAIN_TRAJECTORY_PAIRS = {
    "burgers2d": [("burgers2d_velocity_trj.npy", "burgers2d_ground_truth_trj.npy")],
    "heat_flow": [("heat_flow_temperature_trj.npy", "heat_flow_ground_truth_trj.npy")],
    "julia_set": [("julia_set_domain_trj.npy", "julia_set_ground_truth_trj.npy")],
    "reaction_diffusion": [
        ("reaction_diffusion_u_trj.npy", "reaction_diffusion_ground_truth_u_trj.npy"),
        ("reaction_diffusion_v_trj.npy", "reaction_diffusion_ground_truth_v_trj.npy"),
    ],
}


def compute_domain_quality(config_dir: Path, domain: str) -> dict[str, Any] | None:
    pairs = DOMAIN_TRAJECTORY_PAIRS.get(domain)
    if not pairs:
        return None

    values: list[dict[str, float]] = []

    for generated_name, ground_truth_name in pairs:
        generated_path = config_dir / generated_name
        ground_truth_path = ROOT / f"test_{domain}" / ground_truth_name

        if not generated_path.exists() or not ground_truth_path.exists():
            return None

        try:
            generated, ground_truth = align_trajectories(
                load_np(str(generated_path)),
                load_np(str(ground_truth_path)),
            )
            metrics = compute_metrics(generated, ground_truth)
            reference_rms = float(np.sqrt(np.mean(np.square(ground_truth))))
            relative_rmse = metrics["rmse"] / max(reference_rms, 1e-12)
            values.append(
                {
                    "relative_rmse": float(relative_rmse),
                    "mean_l2": float(metrics["mean_l2"]),
                    "rmse": float(metrics["rmse"]),
                    "physics_score": 1.0 / (1.0 + relative_rmse),
                }
            )
        except Exception:
            return None

    if not values:
        return None

    return {
        "domain": domain,
        "mean_relative_rmse": float(np.mean([v["relative_rmse"] for v in values])),
        "worst_relative_rmse": float(np.max([v["relative_rmse"] for v in values])),
        "mean_l2": float(np.mean([v["mean_l2"] for v in values])),
        "rmse": float(np.mean([v["rmse"] for v in values])),
        "physics_score": float(np.mean([v["physics_score"] for v in values])),
    }


def summarize_report(report: dict[str, Any], experiment_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in report.get("results", []):
        config_id = result.get("config_id")
        config = result.get("config", {})
        domain_rows = {row["domain"]: row for row in result.get("domains", [])}

        successful_domains = [
            domain
            for domain, row in domain_rows.items()
            if row.get("execution", {}).get("execution_ok", False)
        ]

        quality = []
        domain_scores: dict[str, dict[str, Any]] = {}
        for domain in successful_domains:
            config_dir = experiment_dir / "cross_domain" / config_id / domain
            q = compute_domain_quality(config_dir, domain)
            if q is not None:
                quality.append(q)
                domain_scores[domain] = q

            unmeasured_domains = [domain for domain in successful_domains if domain not in domain_scores]
        avg_physics = float(np.mean([item["physics_score"] for item in quality])) if quality else 0.0
        mean_relative_rmse = float(np.mean([item["mean_relative_rmse"] for item in quality])) if quality else 0.0
        worst_relative_rmse = float(np.max([item["worst_relative_rmse"] for item in quality])) if quality else 0.0

        rows.append(
            {
                "config_id": config_id,
                "config": config,
                "successful_domains": len(successful_domains),
                "tested_domains": len(domain_rows),
                "avg_physics_score": avg_physics,
                "mean_relative_rmse": mean_relative_rmse,
                "worst_relative_rmse": worst_relative_rmse,
                "measured_domains": sorted(domain_scores),
                "unmeasured_domains": sorted(unmeasured_domains),
                "quality_domains": sorted(domain_scores),
                "domain_quality": domain_scores,
            }
        )

    rows.sort(
        key=lambda item: (
            item["successful_domains"],
            item["avg_physics_score"],
            -item["mean_relative_rmse"],
        ),
        reverse=True,
    )
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    parameter_names = list(rows[0]["config"].keys()) if rows and rows[0].get("config") else []
    domain_names = sorted({domain for row in rows for domain in row.get("quality_domains", [])})
    fieldnames = [
        "rank",
        "config_id",
        *parameter_names,
        "successful_domains",
        "tested_domains",
        "avg_physics_score",
        "mean_relative_rmse",
        "worst_relative_rmse",
        "measured_domains",
        "unmeasured_domains",
        "quality_domains",
        *[f"{domain}_physics" for domain in domain_names],
        *[f"{domain}_rmse" for domain in domain_names],
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for rank, row in enumerate(rows, start=1):
            record: dict[str, Any] = {
                "rank": rank,
                "config_id": row["config_id"],
                **row["config"],
                "successful_domains": row["successful_domains"],
                "tested_domains": row["tested_domains"],
                "avg_physics_score": round(row["avg_physics_score"], 6),
                "mean_relative_rmse": round(row["mean_relative_rmse"], 6),
                "worst_relative_rmse": round(row["worst_relative_rmse"], 6),
                "measured_domains": ";".join(row["measured_domains"]),
                "unmeasured_domains": ";".join(row["unmeasured_domains"]),
                "quality_domains": ";".join(row["quality_domains"]),
            }
            for domain in domain_names:
                domain_quality = row["domain_quality"].get(domain)
                record[f"{domain}_physics"] = round(domain_quality["physics_score"], 6) if domain_quality else ""
                record[f"{domain}_rmse"] = round(domain_quality["mean_relative_rmse"], 6) if domain_quality else ""
            writer.writerow(record)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare the numeric quality of the working test domains across all sampled configs."
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    rows = summarize_report(report, args.report.parent)
    write_csv(rows, args.output)

    print(f"Loaded {args.report} and ranked {len(rows)} configs by working-domain quality.")
    print("rank  success  avg_physics  mean_rel_rmse  config_id")
    for rank, row in enumerate(rows, start=1):
        print(
            f"{rank:>4}  {row['successful_domains']:>7}  {row['avg_physics_score']:>11.4f}  "
            f"{row['mean_relative_rmse']:>13.4f}  {row['config_id']}"
        )
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())