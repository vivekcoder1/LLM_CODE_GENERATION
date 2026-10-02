from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOMAINS = ["burgers2d", "heat_flow", "julia_set", "lid_driven_cavity", "reaction_diffusion", "smoke_plume"]

REQUIREMENTS = {
    "burgers2d": [
        ("diffuse.implicit", r"\bdiffuse\.implicit\s*\("),
        ("advect.semi_lagrangian", r"\badvect\.semi_lagrangian\s*\("),
        ("CenteredGrid", r"\bCenteredGrid\s*\("),
    ],
    "heat_flow": [
        ("diffuse.implicit", r"\bdiffuse\.implicit\s*\("),
        ("CenteredGrid", r"\bCenteredGrid\s*\("),
    ],
    "julia_set": [
        ("CenteredGrid", r"\bCenteredGrid\s*\("),
        ("correct equation", r"\bz\s*(?:\*\*|\^\s*\{?2\}?)\s*2?\s*\+\s*c"),
        ("correct escape criterion", r"(?:abs\s*\([^)]*\)|\|[^|]+\|)\s*(?:<|<=)\s*2|(?:abs|mag_sq|magnitude)[^\n<>=]*[<]?[=]?\s*4"),
    ],
    "lid_driven_cavity": [
        ("advect.semi_lagrangian", r"\badvect\.semi_lagrangian\s*\("),
        ("diffuse.explicit", r"\bdiffuse\.explicit\s*\("),
        ("fluid.make_incompressible", r"\bfluid\.make_incompressible\s*\("),
        ("StaggeredGrid", r"\bStaggeredGrid\s*\("),
    ],
    "reaction_diffusion": [
        ("field.laplace x2", r"\bfield\.laplace\s*\(", 2),
        ("CenteredGrid x3", r"\bCenteredGrid\s*\(", 3),
    ],
    "smoke_plume": [
        ("advect.mac_cormack", r"\badvect\.mac_cormack\s*\("),
        ("resample", r"\bresample\s*\("),
        ("semi_lagrangian", r"\bsemi_lagrangian\s*\("),
        ("fluid.make_incompressible", r"\bfluid\.make_incompressible\s*\("),
        ("StaggeredGrid", r"\bStaggeredGrid\s*\("),
        ("CenteredGrid", r"\bCenteredGrid\s*\("),
    ],
}


def audit_file(path: Path, domain: str) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    results = []
    for requirement in REQUIREMENTS[domain]:
        name, pattern, *minimum = requirement
        count = len(re.findall(pattern, text, flags=re.IGNORECASE))
        required = minimum[0] if minimum else 1
        matched_slots = min(count, required)
        results.append({
            "requirement": name,
            "count": count,
            "required": required,
            "matched_slots": matched_slots,
            "pass": count >= required,
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit KG-generated scripts against expected domain key functions.")
    parser.add_argument("--root", type=Path, default=ROOT / "optimization_runs/pruned_cross_domain/cross_domain")
    parser.add_argument("--one-shot-root", type=Path, default=ROOT)
    parser.add_argument("--csv", type=Path, default=ROOT / "optimization_runs/pruned_cross_domain/key_function_audit.csv")
    args = parser.parse_args()

    config_dirs = sorted(path for path in args.root.iterdir() if path.is_dir())
    rows = []
    total_requirements = sum(
        sum(item[2] if len(item) > 2 else 1 for item in items)
        for items in REQUIREMENTS.values()
    )
    print("source/config_id  total  domain scores")
    one_shot_results = []
    for domain in DOMAINS:
        script = args.one_shot_root / f"test_{domain}" / "generated_code.py"
        checks = audit_file(script, domain) if script.exists() else []
        passed = sum(check["matched_slots"] for check in checks)
        required = sum(check["required"] for check in checks)
        one_shot_results.extend({"source": "one_shot", "config_id": "one_shot", "domain": domain, **check} for check in checks)
        print(f"one_shot          {passed:>2}/{required}  {domain[:6]}={passed}/{required}")
    rows.extend(one_shot_results)

    for config_dir in config_dirs:
        config_results = []
        domain_scores = []
        for domain in DOMAINS:
            script = config_dir / domain / f"generated_{domain}_simulation.py"
            checks = audit_file(script, domain) if script.exists() else []
            passed = sum(check["matched_slots"] for check in checks)
            required = sum(check["required"] for check in checks)
            domain_scores.append(f"{domain[:6]}={passed}/{required}")
            config_results.extend({"source": "kg", "config_id": config_dir.name, "domain": domain, **check} for check in checks)
        passed_total = sum(row["matched_slots"] for row in config_results)
        print(f"{config_dir.name}  {passed_total:>2}/{total_requirements}  " + " ".join(domain_scores))
        rows.extend(config_results)

    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "config_id", "domain", "requirement", "count", "required", "matched_slots", "pass"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())