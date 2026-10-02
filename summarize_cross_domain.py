from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_REPORT = ROOT / "optimization_runs" / "cross_domain_execution.json"


def summarize(report: dict[str, Any]) -> list[dict[str, Any]]:
    domains = report.get("domains", [])
    summaries = []
    for result in report.get("results", []):
        domain_rows = {row["domain"]: row for row in result.get("domains", [])}
        successful = sum(
            row.get("execution", {}).get("execution_ok", False)
            for row in domain_rows.values()
        )
        tested = len(domain_rows)
        summaries.append(
            {
                "config_id": result.get("config_id", ""),
                "config": result.get("config", {}),
                "successful_domains": successful,
                "tested_domains": tested,
                "execution_rate": successful / tested if tested else 0.0,
                "domain_status": {
                    domain: "PASS"
                    if domain_rows.get(domain, {}).get("execution", {}).get("execution_ok", False)
                    else "FAIL"
                    for domain in domains
                },
            }
        )
    summaries.sort(
        key=lambda row: (row["successful_domains"], row["execution_rate"]),
        reverse=True,
    )
    return summaries


def write_csv(summaries: list[dict[str, Any]], domains: list[str], path: Path) -> None:
    parameter_names = list(summaries[0]["config"]) if summaries else []
    fields = [
        "rank",
        "config_id",
        *parameter_names,
        "successful_domains",
        "tested_domains",
        "execution_rate",
        *domains,
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for rank, summary in enumerate(summaries, start=1):
            writer.writerow(
                {
                    "rank": rank,
                    "config_id": summary["config_id"],
                    **summary["config"],
                    "successful_domains": summary["successful_domains"],
                    "tested_domains": summary["tested_domains"],
                    "execution_rate": round(summary["execution_rate"], 4),
                    **summary["domain_status"],
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize an existing cross-domain execution report without rerunning anything."
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    domains = report.get("domains", [])
    summaries = summarize(report)
    csv_path = args.csv or args.report.with_name("cross_domain_execution_summary.csv")
    write_csv(summaries, domains, csv_path)

    print(f"Execution rates from {args.report}")
    print("rank  execution  config_id    " + " ".join(f"{domain[:8]:8}" for domain in domains))
    for rank, summary in enumerate(summaries, start=1):
        markers = " ".join(
            f"{summary['domain_status'].get(domain, 'N/A'):8}" for domain in domains
        )
        rate = 100 * summary["execution_rate"]
        print(
            f"{rank:>4}  {summary['successful_domains']}/{summary['tested_domains']} "
            f"({rate:>5.1f}%)  {summary['config_id']}  {markers}"
        )
    print(f"Wrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
