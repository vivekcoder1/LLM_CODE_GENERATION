"""Expand a completed experiment into provenance-labelled diagnostic tables.

This is an offline audit: no API/database calls, simulation execution, output
renaming, or numerical task scores. Local domain recipes are explicitly labelled
as a local snapshot, independently of any live graph used by the experiment.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

import numpy as np

try:
    from .combined_evaluation import REQUESTED_OUTPUTS
    from .domain_retrieval import DomainKnowledgeRetriever
except ImportError:
    from combined_evaluation import REQUESTED_OUTPUTS
    from domain_retrieval import DomainKnowledgeRetriever


HERE = Path(__file__).resolve().parent
LOCAL_PRIOR = "local_domain_graph_snapshot_not_live_query"
LIMITATIONS = [
    "API resolution records describe the completed run's metadata joins; no live graph was queried by this audit.",
    "Domain recipe tables come from the explicitly selected local graph snapshot. They do not prove that the live domain graph had identical content.",
    "Artifact diagnostics describe only manifest-reported files inside each isolated run directory. Recorded hashes are checked when available.",
    "Wrong-name arrays remain diagnostic observations. No file is renamed, substituted into a requested output, or awarded a task-contract score.",
    "Finite-only ranges omit NaN/infinite entries; a finite range does not establish stability, correctness, or agreement with a reference.",
    "First nonfinite frame is zero-based on the run's declared generated_time_axis (default 0). Scalar arrays have no frame axis.",
    "For complex arrays, finite min/max are magnitudes, as labelled. Empty and nonnumeric arrays have no numerical range.",
    "Historical-script reruns do not measure generation improvements from combined retrieval. This audit makes no causal improvement claim.",
    "API documentation retention matches only literal Import Path fields in code_context.md for the same resolved hints. It excludes unresolved hints from the matchable denominator and does not count resolution metadata in the combined prompt.",
]


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _number(value):
    if isinstance(value, (int, np.integer, bool, np.bool_)):
        return int(value)
    converted = float(value)
    # Extremely wide floating types may exceed JSON/native float range. Keep
    # their finite decimal representation rather than serializing Infinity.
    return converted if math.isfinite(converted) else str(value)


def diagnose_array(path: str | Path, *, time_axis: int = 0, chunk_elements: int = 1_000_000) -> dict[str, Any]:
    """Inspect numeric NPY data with bounded chunk memory and pickle disabled."""
    if not isinstance(chunk_elements, int) or chunk_elements < 1:
        raise ValueError("chunk_elements must be a positive integer")
    result = {"array_status": "unreadable", "shape": None, "dtype": None, "element_count": None,
              "finite_count": None, "nonfinite_count": None, "first_nonfinite_frame": None,
              "finite_min": None, "finite_max": None, "range_basis": "real_values",
              "range_omitted_count": 0, "frame_axis": None, "frame_count": None, "error": ""}
    array = None
    try:
        array = np.load(Path(path), mmap_mode="r", allow_pickle=False)
        if not isinstance(array, np.ndarray):
            raise ValueError("Expected a single NPY array")
        result.update(shape=list(array.shape), dtype=str(array.dtype), element_count=int(array.size))
        if array.dtype.kind not in "biufc":
            result.update(array_status="nonnumeric", error="Only boolean/integer/float/complex arrays have finite diagnostics")
            return result
        if array.ndim:
            if not isinstance(time_axis, int) or not -array.ndim <= time_axis < array.ndim:
                raise ValueError("generated_time_axis is invalid for this array")
            time_axis %= array.ndim
            result.update(frame_axis=time_axis, frame_count=int(array.shape[time_axis]))
        result.update(finite_count=0, nonfinite_count=0)
        if array.size == 0:
            result["array_status"] = "empty"
            return result
        is_complex = array.dtype.kind == "c"
        if is_complex:
            result["range_basis"] = "complex_magnitudes"
        order = "F" if array.flags.f_contiguous and not array.flags.c_contiguous else "C"
        flat = array.ravel(order="K")
        stride = (math.prod(array.shape[:time_axis]) if order == "F" else math.prod(array.shape[time_axis + 1:])) if array.ndim else None
        minimum = maximum = None
        for offset in range(0, int(array.size), chunk_elements):
            chunk = flat[offset:offset + chunk_elements]
            finite = np.isfinite(chunk)
            count = int(np.count_nonzero(finite))
            result["finite_count"] += count
            result["nonfinite_count"] += int(chunk.size) - count
            if count:
                with np.errstate(over="ignore", invalid="ignore"):
                    values = np.abs(chunk[finite]) if is_complex else chunk[finite]
                if is_complex:
                    finite_ranges = np.isfinite(values)
                    result["range_omitted_count"] += int(values.size) - int(np.count_nonzero(finite_ranges))
                    values = values[finite_ranges]
                if values.size:
                    low, high = values.min(), values.max()
                    minimum = low if minimum is None or low < minimum else minimum
                    maximum = high if maximum is None or high > maximum else maximum
            if count != chunk.size and array.ndim:
                bad = np.flatnonzero(~finite) + offset
                frame = int(((bad // stride) % array.shape[time_axis]).min())
                previous = result["first_nonfinite_frame"]
                result["first_nonfinite_frame"] = frame if previous is None else min(previous, frame)
        result.update(array_status="nonfinite" if result["nonfinite_count"] else "finite",
                      finite_min=_number(minimum) if minimum is not None else None,
                      finite_max=_number(maximum) if maximum is not None else None)
    except Exception as exc:
        result.update(array_status="unreadable", error=str(exc))
    finally:
        if isinstance(array, np.memmap):
            array._mmap.close()
        elif array is not None and hasattr(array, "close"):
            array.close()
    return result


def _evidence(item):
    provenance = item.get("provenance", {})
    return {key: provenance.get(key) for key in ("source_path", "source_lines", "source_sha256", "evidence_kind", "review_status")}


def _mapping_class(item):
    quality, status = item.get("quality", ""), item.get("status", "")
    if "ambiguous" in str(quality) or status == "ambiguous":
        return "ambiguous"
    if "unavailable" in str(quality) or status == "unavailable":
        return "unavailable"
    if quality == "exact_alias" and status == "resolved" and item.get("code_id") is not None:
        return "exact_alias"
    if quality == "legacy_file_name_candidate" and status == "resolved_candidate" and item.get("code_id") is not None:
        return "legacy_candidate"
    return "unresolved"


def _api_tables(runs):
    rows, summaries = [], []
    for run in runs:
        mappings = run.get("api_resolution", [])
        valid = isinstance(mappings, list) and all(isinstance(item, dict) for item in mappings)
        counts = Counter()
        if valid:
            for item in mappings:
                category = _mapping_class(item)
                counts[category] += 1
                rows.append({"run_id": run.get("run_id"), "domain": run.get("domain"), "variant": run.get("variant"),
                             "evidence_origin": "completed_run_manifest", "mapping_class": category,
                             "quality": item.get("quality"), "status": item.get("status"),
                             "observed_call": item.get("observed_call"), "qualified_name": item.get("qualified_name"),
                             "code_id": item.get("code_id"), "code_import_path": item.get("code_import_path"),
                             "candidate_count": item.get("candidate_count"), "definition_path": item.get("definition_path"),
                             "namespace_caveat": item.get("namespace_caveat"),
                             "resolved_for_retrieval": category in {"exact_alias", "legacy_candidate"}})
        summaries.append({"run_id": run.get("run_id"), "domain": run.get("domain"), "variant": run.get("variant"),
                          "retrieval_status": run.get("retrieval_status", "not_requested"),
                          "domain_status": run.get("domain_status", "not_requested"),
                          "mapping_records_status": "available" if valid else "aggregate_or_invalid_format",
                          "mapping_count": len(mappings) if valid else None,
                          **{key + "_count": counts[key] if valid else None for key in ("exact_alias", "legacy_candidate", "ambiguous", "unavailable", "unresolved")},
                          **{key: run.get("context", {}).get(key) for key in ("code_nodes", "domain_nodes", "seed_count", "raw_relations", "filtered_relations", "context_chars")}})
    return rows, summaries


def _api_documentation_tables(runs, experiment_root: Path):
    rows, summaries = [], []
    cache = {}

    def endpoints(run):
        if run is None:
            return set(), "paired_code_only_arm_missing"
        key = run.get("run_id", str(id(run)))
        if key in cache:
            return cache[key]
        directory = Path(run.get("run_dir", "")).resolve()
        path = (directory / "code_context.md").resolve()
        if not directory.is_relative_to(experiment_root) or not path.is_relative_to(directory):
            return set(), "outside_isolated_run"
        if not path.is_file():
            return set(), "code_context_missing"
        text = path.read_text(encoding="utf-8-sig")
        expected_hash = run.get("metadata", {}).get("code_context_hash")
        if expected_hash and hashlib.sha256(text.encode("utf-8")).hexdigest() != expected_hash:
            return set(), "code_context_changed_since_manifest"
        values = set(re.findall(r"^\*\*Import Path:\*\*\s*`([^`\r\n]+)`\s*$", text, flags=re.M))
        cache[key] = (values, "available")
        return cache[key]

    for combined in (run for run in runs if run.get("variant") == "combined"):
        paired = [run for run in runs if run.get("variant") == "code_only"
                  and all(run.get(key) == combined.get(key) for key in ("domain", "replicate", "config_id"))]
        baseline = paired[0] if len(paired) == 1 else None
        combined_paths, combined_status = endpoints(combined)
        baseline_paths, baseline_status = endpoints(baseline)
        if len(paired) > 1:
            baseline_status = "paired_code_only_arm_ambiguous"
        mappings = combined.get("api_resolution", [])
        mappings = mappings if isinstance(mappings, list) else []
        start = len(rows)
        for item in mappings:
            if not isinstance(item, dict):
                continue
            matchable = _mapping_class(item) in {"exact_alias", "legacy_candidate"} and bool(item.get("code_import_path"))
            endpoint = item.get("code_import_path")
            rows.append({"run_id": combined.get("run_id"), "paired_code_only_run_id": baseline.get("run_id") if baseline else None,
                "domain": combined.get("domain"), "replicate": combined.get("replicate"), "observed_call": item.get("observed_call"),
                "mapping_quality": item.get("quality"), "mapping_status": item.get("status"), "code_id": item.get("code_id"),
                "code_import_path": endpoint, "matchable_resolved_binding": matchable,
                "combined_documented": endpoint in combined_paths if matchable and combined_status == "available" else None,
                "code_only_documented": endpoint in baseline_paths if matchable and baseline_status == "available" else None,
                "combined_document_status": combined_status, "code_only_document_status": baseline_status,
                "evidence_origin": "literal_import_path_fields_in_code_context_only"})
        current = rows[start:]
        denominator = sum(row["matchable_resolved_binding"] for row in current)
        summaries.append({"domain": combined.get("domain"), "replicate": combined.get("replicate"),
            "combined_run_id": combined.get("run_id"), "code_only_run_id": baseline.get("run_id") if baseline else None,
            "total_bindings": len(current), "matchable_resolved_bindings": denominator,
            "excluded_unresolved_bindings": len(current) - denominator,
            "combined_documented_count": sum(row["combined_documented"] is True for row in current) if combined_status == "available" else None,
            "code_only_documented_count": sum(row["code_only_documented"] is True for row in current) if baseline_status == "available" else None,
            "combined_document_status": combined_status, "code_only_document_status": baseline_status})
    return rows, summaries


def _prior_tables(graph, domains):
    tables = {key: [] for key in ("domain_prior_summary", "domain_fields", "domain_parameters", "domain_helpers",
                                 "domain_update_steps", "domain_dependencies", "domain_outputs", "domain_api_coverage", "domain_guidance")}
    retriever = DomainKnowledgeRetriever(graph=graph)
    for domain in domains:
        bundle = retriever.get_domain_context(domain)
        knowledge = bundle.get("knowledge", {})
        references = knowledge.get("references", [])
        tables["domain_prior_summary"].append({"domain": domain, "evidence_origin": LOCAL_PRIOR, "status": bundle["status"],
            **bundle["statistics"], "fields": sum(len(ref["fields"]) for ref in references),
            "parameters": sum(len(ref["parameters"]) for ref in references), "helpers": sum(len(ref["helpers"]) for ref in references),
            "outputs": sum(len(ref["outputs"]) for ref in references), "context_chars": len(bundle["context"]),
            "omitted_optional_guidance": bundle["context_budget"]["omitted_guidance_sections"]})
        for reference in references:
            base = {"domain": domain, "reference_id": reference["id"], "evidence_origin": LOCAL_PRIOR}
            for name, fields in (("fields", ("name", "variable", "role", "representation", "expression")),
                                 ("parameters", ("name", "expression", "reference_value", "parameter_kind")),
                                 ("helpers", ("name", "arguments", "local_expressions", "return_expressions")),
                                 ("outputs", ("name", "variable", "axis_order", "initial_frame", "save_status", "artifact_observations")),
                                 ("guidance", ("name", "text", "condition"))):
                for item in reference[name]:
                    tables["domain_" + name].append({**base, **{field: item.get(field) for field in fields}, **_evidence(item),
                                                    **({"reference_only_not_task_output_contract": True} if name == "outputs" else {})})
            for step in reference["ordered_steps"]:
                tables["domain_update_steps"].append({**base, "step_id": step["id"], "order": step["order"],
                    "name": step["name"], "expression": step["expression"], "reads": step["reads"], "writes": step["writes"], **_evidence(step)})
                for relationship, key in (("READS", "reads"), ("WRITES", "writes"), ("USES_PARAMETER", "parameters"), ("USES_HELPER", "helpers")):
                    for dependency in step[key]:
                        tables["domain_dependencies"].append({**base, "step_order": step["order"], "step_name": step["name"],
                            "relationship": relationship, "target": dependency.get("name"), "target_kind": dependency.get("kind"),
                            "variable": dependency.get("variable"), "state_version": dependency.get("state_version"), **_evidence(dependency)})
        for status, items in (("verified_local_static_definition", knowledge.get("verified_api_hints", [])),
                              ("unresolved_candidate_only", knowledge.get("unresolved_api_candidates", []))):
            for item in items:
                tables["domain_api_coverage"].append({"domain": domain, "evidence_origin": LOCAL_PRIOR, "verification_class": status,
                    "observed_call": item.get("observed_call", item.get("public_name")), "qualified_name": item.get("qualified_name"),
                    "configured_aliases": item.get("configured_aliases"), "component_type": item.get("component_type"),
                    "definition_path": item.get("definition_path"), "reason": item.get("reason"), **_evidence(item)})
    return tables


def _artifact_rows(runs, experiment_root: Path, chunk_elements: int):
    rows = []
    for run in runs:
        directory = Path(run.get("run_dir", "")).resolve()
        declared = {}
        for item in run.get("observed_artifacts", []):
            if isinstance(item, dict) and item.get("path"):
                declared[str(Path(item["path"]).resolve())] = {**item, "observation_source": "manifest_observed_artifacts"}
        for component, path in run.get("artifacts", {}).items():
            if path:
                declared.setdefault(str(Path(path).resolve()), {"path": path, "observation_source": "manifest_contract_artifacts", "component": component})
        expected = REQUESTED_OUTPUTS.get(run.get("domain"), {})
        for path_text, item in sorted(declared.items()):
            path = Path(path_text)
            if path.suffix.lower() != ".npy":
                continue
            matching = [component for component, filename in expected.items() if filename == path.name]
            row = {"run_id": run.get("run_id"), "domain": run.get("domain"), "variant": run.get("variant"),
                "artifact_provenance": run.get("artifact_provenance", "unknown"), "execution_status": run.get("execution", {}).get("status"),
                "observation_source": item["observation_source"], "path": str(path), "filename": path.name,
                "contract_name_match": bool(matching), "task_component": matching[0] if matching else None,
                "scoring_policy": "diagnostic_only_not_a_score", "recorded_sha256": item.get("sha256"),
                "actual_sha256": None, "hash_status": "not_recorded", "array_status": "not_read"}
            if not directory.is_relative_to(experiment_root) or not path.is_relative_to(directory):
                row.update(array_status="outside_isolated_run", error="Refusing to inspect a file outside the experiment/run directory")
            elif not path.is_file():
                row.update(array_status="missing", error="Manifest-reported artifact does not exist")
            else:
                row["actual_sha256"] = _hash(path)
                if item.get("sha256") and item["sha256"] != row["actual_sha256"]:
                    row.update(array_status="changed_since_manifest", hash_status="mismatch", error="Recorded artifact hash does not match current file")
                else:
                    row["hash_status"] = "matched" if item.get("sha256") else "not_recorded"
                    row.update(diagnose_array(path, time_axis=run.get("alignment", {}).get("generated_time_axis", 0), chunk_elements=chunk_elements))
            rows.append(row)
    return rows


def build_audit(manifest: dict[str, Any], graph: dict[str, Any], *, experiment_root: Path,
                chunk_elements: int = 1_000_000) -> dict[str, Any]:
    """Construct audit data only after the runner marks its manifest complete."""
    if not manifest.get("completed_utc"):
        raise ValueError("The experiment manifest is incomplete; wait for completed_utc")
    if not isinstance(chunk_elements, int) or chunk_elements < 1:
        raise ValueError("chunk_elements must be a positive integer")
    runs = manifest.get("runs", [])
    if not isinstance(runs, list) or not all(isinstance(run, dict) for run in runs):
        raise ValueError("Manifest runs must be a list of records")
    domains = sorted({run.get("domain") for run in runs if isinstance(run.get("domain"), str)})
    api_rows, api_summary = _api_tables(runs)
    documentation, documentation_summary = _api_documentation_tables(runs, Path(experiment_root).resolve())
    tables = {"api_resolution": api_rows, "api_resolution_summary": api_summary, **_prior_tables(graph, domains),
              "api_documentation_retention": documentation, "api_documentation_summary": documentation_summary,
              "artifact_diagnostics": _artifact_rows(runs, Path(experiment_root).resolve(), chunk_elements)}
    return {"schema_version": 1, "audit_created_utc": datetime.now(timezone.utc).isoformat(),
            "experiment_completed_utc": manifest["completed_utc"], "experiment_mode": manifest.get("mode"),
            "local_graph_declared_sha256": graph.get("graph_sha256"), "limitations": LIMITATIONS, "tables": tables}


def _cell(value):
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False, allow_nan=False) if isinstance(value, (dict, list)) else str(value)


def _markdown_table(rows, fields):
    def cell(value):
        return _cell(value).replace("|", "\\|").replace("\n", "<br>")
    return "\n".join(["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |",
                      *["| " + " | ".join(cell(row.get(field)) for field in fields) + " |" for row in rows]])


def write_audit(manifest_path: str | Path, output_dir: str | Path, *,
                domain_graph_path: str | Path = HERE / "domain_knowledge_graph.json",
                chunk_elements: int = 1_000_000) -> dict[str, Path]:
    """Create new CSV/Markdown/JSON reports without overwriting any directory."""
    manifest_path, graph_path, output = Path(manifest_path).resolve(), Path(domain_graph_path).resolve(), Path(output_dir).resolve()
    if output.exists():
        raise FileExistsError(f"Audit output directory already exists: {output}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if not manifest.get("completed_utc"):
        raise ValueError("The experiment manifest is incomplete; wait for completed_utc")
    if any(output.is_relative_to(Path(run["run_dir"]).resolve()) for run in manifest.get("runs", []) if run.get("run_dir")):
        raise ValueError("Audit reports must be outside simulation run directories")
    graph = json.loads(graph_path.read_text(encoding="utf-8-sig"))
    audit = build_audit(manifest, graph, experiment_root=manifest_path.parent, chunk_elements=chunk_elements)
    audit["sources"] = {"manifest": {"path": str(manifest_path), "sha256": _hash(manifest_path)},
                        "local_domain_snapshot": {"path": str(graph_path), "sha256": _hash(graph_path), "evidence_origin": LOCAL_PRIOR}}
    output.mkdir(parents=True, exist_ok=False)
    paths = {}
    for name, rows in audit["tables"].items():
        path = output / (name + ".csv")
        fields = list(dict.fromkeys(key for row in rows for key in row)) or ["status"]
        with path.open("x", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows({key: _cell(row.get(key)) for key in fields} for row in rows)
        paths[name] = path
    paths["json"] = output / "audit.json"
    paths["json"].write_text(json.dumps(audit, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    pieces = ["# Detailed integration experiment audit", "API mappings come from the completed run. Recipe tables describe the selected local snapshot; they are not a fresh live-graph inspection.",
              "## API resolution by retrieval arm", _markdown_table(audit["tables"]["api_resolution_summary"],
                ["domain", "variant", "retrieval_status", "mapping_count", "exact_alias_count", "legacy_candidate_count", "ambiguous_count", "unresolved_count", "unavailable_count"]),
              "## Local domain-prior coverage", _markdown_table(audit["tables"]["domain_prior_summary"],
                ["domain", "status", "nodes", "edges", "fields", "parameters", "helpers", "ordered_steps", "outputs", "verified_apis", "api_candidates"]),
              "## API documentation retention for the same resolved hints", _markdown_table(audit["tables"]["api_documentation_summary"],
                ["domain", "total_bindings", "matchable_resolved_bindings", "excluded_unresolved_bindings", "code_only_documented_count", "combined_documented_count"]),
              "## Observed output diagnostics", _markdown_table(audit["tables"]["artifact_diagnostics"],
                ["domain", "variant", "filename", "contract_name_match", "array_status", "shape", "dtype", "finite_count", "nonfinite_count", "first_nonfinite_frame", "finite_min", "finite_max"]),
              "## Data tables", *[f"- [{name}.csv]({path.name}) ({len(audit['tables'][name])} rows)" for name, path in paths.items() if name in audit["tables"]],
              "## Limitations", *["- " + limitation for limitation in LIMITATIONS],
              "## Source hashes", "```json\n" + json.dumps(audit["sources"], indent=2) + "\n```"]
    paths["markdown"] = output / "audit_report.md"
    paths["markdown"].write_text("\n\n".join(pieces) + "\n", encoding="utf-8")
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True, help="A new audit directory")
    parser.add_argument("--domain-graph", type=Path, default=HERE / "domain_knowledge_graph.json")
    parser.add_argument("--chunk-elements", type=int, default=1_000_000)
    args = parser.parse_args(argv)
    paths = write_audit(args.manifest, args.output_dir, domain_graph_path=args.domain_graph, chunk_elements=args.chunk_elements)
    print(f"Audit: {paths['markdown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
