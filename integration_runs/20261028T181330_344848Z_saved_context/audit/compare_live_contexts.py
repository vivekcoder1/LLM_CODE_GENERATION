"""Compare frozen generation inputs with a later completed live retrieval.

Offline only: reads two completed manifests and their saved context artifacts.
No credentials, model clients, graph drivers, simulation execution or database
calls. The live graph integrity comparison is strictly before/after within the
live retrieval; no old snapshot element IDs are compared to restored databases.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path


INPUT_HASHES = ("task_hash", "code_context_hash", "domain_context_hash", "api_resolution_hash")
TEXT_FILES = {"task.md": "task_hash", "code_context.md": "code_context_hash", "domain_context.md": "domain_context_hash"}
CORE_STATS = ("code_nodes", "domain_nodes", "resolved_api_links", "unresolved_api_links",
              "seed_count", "raw_relations", "filtered_relations", "context_chars")
DOMAINS = {"burgers2d", "heat_flow", "julia_set", "reaction_diffusion"}
LIMITATIONS = [
    "The generated scripts used frozen retrieval inputs. This later check does not retroactively make those generations a live-retrieval experiment.",
    "Matching hashes establish identical recorded task/code/domain/API-resolution inputs for these arms, not general equivalence of database contents.",
    "Graph integrity compares element-ID sets and counts only before/after the new live retrieval. Properties are not hashed, and old-versus-restored database IDs are not compared.",
    "This script performs no API calls, graph queries, generations, executions or credential reads.",
]


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_hash(value):
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=True))


def file_hash(path):
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def child(root, path):
    path = Path(path)
    path = path.resolve() if path.is_absolute() else (root / path).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Artifact lies outside the selected experiment: {path}")
    return path


def load_complete_manifest(path):
    path = Path(path).resolve()
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict) or not manifest.get("completed_utc"):
        raise ValueError(f"Incomplete manifest; completed_utc is required: {path}")
    reports = manifest.get("reports")
    if not isinstance(reports, dict) or not reports:
        raise ValueError(f"Reports have not been recorded yet: {path}")
    for value in reports.values():
        if not child(path.parent, value).is_file():
            raise ValueError(f"A recorded report is missing: {value}")
    expected = {(domain, variant) for domain in DOMAINS for variant in ("code_only", "combined")}
    arms = {}
    for record in manifest.get("runs", []):
        if record.get("variant") not in {"code_only", "combined"}:
            continue
        key = record.get("domain"), record.get("variant")
        if key in arms:
            raise ValueError(f"Duplicate arm in manifest: {key}")
        arms[key] = record
    if arms.keys() != expected:
        raise ValueError(f"Expected exactly eight paired domain/variant records; got {sorted(arms)}")
    return path, manifest, arms


def inspect_arm(root, record):
    directory = child(root, record["run_dir"])
    metadata = record.get("metadata", {})
    result = {"run_id": record.get("run_id"), "file_checks": [], "blueprints": {}}
    for filename, field in TEXT_FILES.items():
        path = child(root, directory / filename)
        actual = digest(path.read_text(encoding="utf-8-sig")) if path.is_file() else None
        expected = metadata.get(field)
        result["file_checks"].append({"file": str(path), "metadata_field": field,
                                     "expected": expected, "actual": actual,
                                     "matches": bool(expected and actual and expected == actual)})
    resolution = record.get("api_resolution")
    embedded = canonical_hash(resolution) if isinstance(resolution, list) else None
    path = directory / "api_resolution.json"
    if path.is_file():
        persisted = json.loads(child(root, path).read_text(encoding="utf-8-sig"))
    else:
        path = child(root, directory / "retrieval_metadata.json")
        persisted = json.loads(path.read_text(encoding="utf-8-sig")).get("api_resolution") if path.is_file() else None
    actual = canonical_hash(persisted) if isinstance(persisted, list) else None
    expected = metadata.get("api_resolution_hash")
    result["file_checks"].append({"file": str(path), "metadata_field": "api_resolution_hash",
                                 "expected": expected, "actual": actual, "manifest_value_hash": embedded,
                                 "matches": bool(expected and actual and expected == actual == embedded)})
    result["all_input_files_match_metadata"] = all(item["matches"] for item in result["file_checks"])
    plan = record.get("plan", {})
    for name, filename, expected in (
        ("base", "blueprint.json", plan.get("base_sha256")),
        ("effective", "effective_blueprint.json", plan.get("effective_sha256") or record.get("source_record", {}).get("plan", {}).get("effective_sha256")),
    ):
        path = child(root, directory / filename)
        value = json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else None
        actual = canonical_hash(value) if value is not None else None
        result["blueprints"][name] = {"path": str(path), "actual_hash": actual,
                                      "recorded_canonical_hash": expected,
                                      "recorded_hash_matches": actual == expected if actual and expected else None}
    path = child(root, directory / "context.md")
    text = path.read_text(encoding="utf-8-sig") if path.is_file() else None
    expected_chars = record.get("context", {}).get("context_chars")
    result["full_context"] = {"path": str(path), "actual_hash": digest(text) if text is not None else None,
                              "actual_characters": len(text) if text is not None else None,
                              "recorded_characters": expected_chars,
                              "recorded_characters_match": len(text) == expected_chars if text is not None and expected_chars is not None else None}
    return result


def live_integrity(manifest):
    integrity = manifest.get("graph_integrity", {})
    before, after = integrity.get("before", {}), integrity.get("after", {})
    rows = []
    for role in sorted(before.keys() | after.keys()):
        a, b = before.get(role, {}), after.get(role, {})
        available = a.get("status") == b.get("status") == "available"
        keys = ("nodes_count", "relationships_count", "nodes_id_sha256", "relationships_id_sha256")
        unchanged = all(a.get(key) == b.get(key) and a.get(key) is not None for key in keys) if available else None
        rows.append({"role": role, "before_status": a.get("status"), "after_status": b.get("status"),
                     "unchanged_topology_ids": unchanged,
                     "recorded_comparison": integrity.get("comparison", {}).get(role),
                     **{"before_" + key: a.get(key) for key in keys},
                     **{"after_" + key: b.get(key) for key in keys},
                     "scope": "within_new_live_retrieval_only; properties_not_hashed"})
    return rows


def compare(saved_manifest, live_manifest):
    saved_path, saved, saved_arms = load_complete_manifest(saved_manifest)
    live_path, live, live_arms = load_complete_manifest(live_manifest)
    rows, details = [], []
    for key in sorted(saved_arms):
        old, new = saved_arms[key], live_arms[key]
        old_check, new_check = inspect_arm(saved_path.parent, old), inspect_arm(live_path.parent, new)
        matches = {field + "_equal": old.get("metadata", {}).get(field) == new.get("metadata", {}).get(field)
                   if old.get("metadata", {}).get(field) and new.get("metadata", {}).get(field) else None
                   for field in INPUT_HASHES}
        stat_changes = {field: {"used": old.get("context", {}).get(field), "live": new.get("context", {}).get(field)}
                        for field in CORE_STATS if old.get("context", {}).get(field) != new.get("context", {}).get(field)}
        blueprint_matches = {name + "_blueprint_equal": old_check["blueprints"][name]["actual_hash"] == new_check["blueprints"][name]["actual_hash"]
                             if old_check["blueprints"][name]["actual_hash"] and new_check["blueprints"][name]["actual_hash"] else None
                             for name in ("base", "effective")}
        inputs_match = (all(value is True for value in matches.values())
                        and old_check["all_input_files_match_metadata"] and new_check["all_input_files_match_metadata"])
        rows.append({"domain": key[0], "variant": key[1], "used_run_id": old.get("run_id"), "live_run_id": new.get("run_id"),
                     "used_context_origin": old.get("context_origin", "not_recorded"),
                     "live_retrieval_status": new.get("retrieval_status"),
                     **matches, "used_files_verified": old_check["all_input_files_match_metadata"],
                     "live_files_verified": new_check["all_input_files_match_metadata"],
                     "generation_input_contexts_equal": inputs_match, **blueprint_matches,
                     "full_context_text_equal": old_check["full_context"]["actual_hash"] == new_check["full_context"]["actual_hash"]
                     if old_check["full_context"]["actual_hash"] and new_check["full_context"]["actual_hash"] else None,
                     "core_statistics_equal": not stat_changes,
                     "used_context_chars": old.get("context", {}).get("context_chars"),
                     "live_context_chars": new.get("context", {}).get("context_chars"),
                     "changed_statistics": stat_changes})
        details.append({"domain": key[0], "variant": key[1], "used": old_check, "live": new_check})
    order = "unknown"
    try:
        order = ("live_retrieval_started_after_generation_completed"
                 if datetime.fromisoformat(live["created_utc"]) >= datetime.fromisoformat(saved["completed_utc"])
                 else "live_retrieval_started_before_generation_completed")
    except (KeyError, TypeError, ValueError):
        pass
    return {"schema_version": 1, "purpose": "Post-generation comparison of used frozen inputs with a later live retrieval",
            "chronology": {"generation_completed_utc": saved.get("completed_utc"), "live_created_utc": live.get("created_utc"),
                           "live_completed_utc": live.get("completed_utc"), "order": order},
            "sources": {"used_manifest": {"path": str(saved_path), "sha256": file_hash(saved_path)},
                        "live_manifest": {"path": str(live_path), "sha256": file_hash(live_path)}},
            "summary": {"paired_arms": len(rows), "matching_input_contexts": sum(row["generation_input_contexts_equal"] for row in rows),
                        "matching_full_context_texts": sum(row["full_context_text_equal"] is True for row in rows),
                        "matching_core_statistics": sum(row["core_statistics_equal"] for row in rows)},
            "comparison": rows, "file_verification": details, "live_graph_integrity": live_integrity(live), "limitations": LIMITATIONS}


def cell(value):
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)


def table(rows, fields):
    def value(item):
        return cell(item).replace("|", "\\|").replace("\n", "<br>")
    return "\n".join(["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |",
                      *["| " + " | ".join(value(row.get(field)) for field in fields) + " |" for row in rows]])


def write_comparison(saved_manifest, live_manifest, output_dir):
    output = Path(output_dir).resolve()
    paths = {suffix: output / ("live_context_comparison." + suffix) for suffix in ("csv", "json", "md")}
    if any(path.exists() for path in paths.values()):
        raise FileExistsError("Comparison outputs already exist; select a new output directory")
    report = compare(saved_manifest, live_manifest)
    output.mkdir(parents=True, exist_ok=True)
    fields = list(report["comparison"][0])
    with paths["csv"].open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: cell(row.get(key)) for key in fields} for row in report["comparison"])
    with paths["json"].open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    summary = report["summary"]
    pieces = ["# Later live-context verification", report["purpose"],
              f"**{summary['matching_input_contexts']}/{summary['paired_arms']} arms** have matching task, public-code, domain-prior and API-resolution hashes, verified against their saved artifacts.",
              "This check happened after the fresh saved-context experiment. It does not change which context source was actually used for generation.",
              "## Paired context checks", table(report["comparison"],
                  ["domain", "variant", "task_hash_equal", "code_context_hash_equal", "domain_context_hash_equal", "api_resolution_hash_equal", "used_files_verified", "live_files_verified", "generation_input_contexts_equal", "core_statistics_equal"]),
              "## New live retrieval: before/after graph topology", table(report["live_graph_integrity"],
                  ["role", "before_nodes_count", "after_nodes_count", "before_relationships_count", "after_relationships_count", "unchanged_topology_ids", "recorded_comparison"]),
              "The table above compares each newly queried database with itself before/after this live retrieval. It does not compare old or restored-database element IDs. Property values were not hashed.",
              "## Chronology", "```json\n" + json.dumps(report["chronology"], indent=2) + "\n```",
              "## Limitations", *["- " + item for item in LIMITATIONS],
              "## Inputs", "```json\n" + json.dumps(report["sources"], indent=2) + "\n```",
              "Full file checks and before/after topology hashes are in [JSON](live_context_comparison.json); paired values are in [CSV](live_context_comparison.csv)."]
    with paths["md"].open("x", encoding="utf-8") as handle:
        handle.write("\n\n".join(pieces) + "\n")
    return report, paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved-manifest", type=Path, required=True)
    parser.add_argument("--live-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args(argv)
    report, paths = write_comparison(args.saved_manifest, args.live_manifest, args.output_dir)
    print(json.dumps(report["summary"], sort_keys=True))
    print("Report:", paths["md"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
