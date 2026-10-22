"""Offline, provenance-aware reports for code-only versus combined KG experiments.

No database/LLM calls and no simulation execution occur here. Existing reports and
reference arrays are read only. The experiment runner owns isolated run folders.

Run record schema (additional fields are retained in JSON)::

    {"run_id": "...", "variant": "code_only" | "combined", "domain": "heat_flow",
     "config_id": "...", "run_dir": "/absolute/isolated/run",
     "generation": {"status": "generated" | "blocked" | "failed", "error": "..."},
     "execution": {"status": "passed" | "failed" | "blocked" | "not_run",
                   "execution_ok": True, "duration_s": 2.5, "error": "..."},
     "artifact_provenance": "fresh" | "existing_outputs_rerun" | "cached" |
                            "not_generated",
     "artifacts": {"main": "/absolute/isolated/run/heat_flow_temperature_trj.npy"},
     "context": {"code_nodes": 12, "domain_nodes": 20, "resolved_api_links": 4,
                 "unresolved_api_links": 1, "context_chars": 10000},
     "metadata": {"model": "...", "seed": None, "temperature": 0,
                  "task_hash": "...", "code_context_hash": "...",
                  "domain_context_hash": "..."},
     "alignment": {"generated_time_axis": 0, "reference_time_axis": 0,
                   "generated_includes_initial": True,
                   "reference_includes_initial": True,
                   "same_initial_conditions": False,
                   "initial_conditions_evidence": "...",
                   "operator_matches_reference": False,
                   "operator_evidence": "..."}}

``fresh`` means outputs from a newly generated script; ``existing_outputs_rerun``
means outputs freshly written by an existing script in an isolated run directory.
Cached arrays are never numerical evidence for a new run. Arrays must have exactly
the requested filename and live under run_dir. No implicit transpose, interpolation,
truncation or broadcasting is allowed. The only permitted frame alignment is an
explicitly declared included-versus-excluded initial frame, with a one-frame gap.

RMSE is the conventional elementwise sqrt(mean(abs(generated-reference)**2)).
It deliberately does not reuse compute_l2_errors.compute_metrics, whose historical
``rmse`` aggregates spatial L2 norms and uses a different normalization. Unavailable
scores are null/blank, never zero. No combined "objective" or physics score is used.
The Burgers reference uses unseeded Noise while the task asks for Gaussian initial
data; heat's task specifies x-only diffusion while its reference calls the library's
multidimensional implicit diffusion. These discrepancies remain explicit caveats.

Public API: evaluate_run(record, project_root), build_report(records, ...), and
write_reports(records, output_dir, ...). write_reports refuses to overwrite files.
The CLI consumes a runner JSON manifest with a ``runs`` (or ``results``) list.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUESTED_OUTPUTS = {
    "burgers2d": {"main": "burgers2d_velocity_trj.npy"},
    "heat_flow": {"main": "heat_flow_temperature_trj.npy"},
    "julia_set": {"main": "julia_set_domain_trj.npy"},
    "reaction_diffusion": {
        "u": "reaction_diffusion_u_trj.npy", "v": "reaction_diffusion_v_trj.npy",
    },
    "lid_driven_cavity": {"main": "lid_driven_cavity_velocity_trj.npy"},
    "smoke_plume": {
        "smoke": "smoke_plume_smoke_trj.npy", "pressure": "smoke_plume_pressure_trj.npy",
    },
    "wake_flow": {"main": "wake_flow_velocity_trj.npy"},
    "structural_mechanics": {},
}
REFERENCE_SPECS = {
    "burgers2d": {"main": {
        "paths": ["test_burgers2d/burgers2d_ground_truth.npy",
                  "test_burgers2d/burgers2d_ground_truth_trj.npy"],
        "shape": (101, 64, 64, 2), "source": "test_burgers2d/burgers2d_ground_truth.py",
    }},
    "heat_flow": {"main": {
        "paths": ["test_heat_flow/heat_flow_ground_truth.npy",
                  "test_heat_flow/heat_flow_ground_truth_trj.npy"],
        "shape": (101, 100, 50), "source": "test_heat_flow/heat_flow_ground_truth.py",
    }},
    "julia_set": {"main": {
        "paths": ["test_julia_set/julia_set_ground_truth_trj.npy"],
        "shape": (100, 256, 256), "source": "test_julia_set/julia_set_ground_truth.py",
    }},
    "reaction_diffusion": {
        component: {
            "paths": [f"test_reaction_diffusion/reaction_diffusion_ground_truth_{component}_trj.npy"],
            "shape": (101, 100, 100),
            "source": "test_reaction_diffusion/reaction_diffusion_ground_truth.py",
        } for component in ("u", "v")
    },
}
METADATA_FIELDS = (
    "model", "seed", "temperature", "max_tokens", "task_hash", "code_context_hash", "domain_context_hash",
)
CONTEXT_FIELDS = (
    "code_nodes", "domain_nodes", "resolved_api_links", "unresolved_api_links", "context_chars",
)
FRESH_PROVENANCE = {"fresh", "fresh_generation", "existing_outputs_rerun"}
REPORT_FILES = {
    "json": "combined_evaluation.json", "csv": "combined_evaluation.csv",
    "markdown": "combined_evaluation.md", "numerical": "numerical_comparisons.csv",
    "retrieval": "retrieval_coverage.csv", "tests": "test_outcomes.csv",
    "paired": "paired_comparisons.csv", "history": "historical_inventory.csv",
    "historical_rows": "historical_rows.csv",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_numeric(path: Path) -> np.ndarray:
    """Load numeric, finite NPY data. Pickle loading is never enabled."""
    value = np.load(path, allow_pickle=False)
    if not isinstance(value, np.ndarray):
        if hasattr(value, "close"):
            value.close()
        raise ValueError("expected a single NPY array")
    if not np.issubdtype(value.dtype, np.number) or value.size == 0 or value.ndim == 0:
        raise ValueError(f"expected nonempty numeric trajectory, got dtype={value.dtype}, shape={value.shape}")
    if not np.isfinite(value).all():
        raise ValueError(f"trajectory contains {int((~np.isfinite(value)).sum())} NaN/infinite values")
    return value


def compare_trajectories(
    generated_path: Path, reference_path: Path, *, expected_shape: tuple[int, ...] | None = None,
    alignment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Measure finite, semantically aligned arrays; return explicit failure statuses."""
    alignment = alignment or {}
    result: dict[str, Any] = {"status": "comparison_error", "rmse": None, "relative_rmse": None}
    try:
        generated = _load_numeric(Path(generated_path))
        reference = _load_numeric(Path(reference_path))
        result.update(generated_shape=list(generated.shape), reference_shape=list(reference.shape))
        actions = []
        for label, axis in (("generated", alignment.get("generated_time_axis", 0)),
                            ("reference", alignment.get("reference_time_axis", 0))):
            if not isinstance(axis, int):
                raise ValueError(f"{label}_time_axis must be an integer")
            array = generated if label == "generated" else reference
            if axis >= array.ndim or axis < -array.ndim:
                raise ValueError(f"{label} time axis {axis} invalid for {array.shape}")
            if axis != 0:
                array = np.moveaxis(array, axis, 0)
                actions.append(f"move {label} time axis {axis} to axis 0 (explicit metadata)")
            if label == "generated":
                generated = array
            else:
                reference = array
        if expected_shape is not None and tuple(reference.shape) != tuple(expected_shape):
            raise ValueError(f"reference shape {reference.shape} does not match source profile {expected_shape}")
        gi = alignment.get("generated_includes_initial")
        ri = alignment.get("reference_includes_initial")
        if generated.shape == reference.shape and isinstance(gi, bool) and isinstance(ri, bool) and gi != ri:
            raise ValueError("equal trajectory lengths but conflicting initial-frame semantics; timestamps are not aligned")
        if generated.shape != reference.shape:
            if generated.shape[1:] != reference.shape[1:]:
                raise ValueError(f"spatial/component shape mismatch {generated.shape} vs {reference.shape}")
            if gi is True and ri is False and generated.shape[0] == reference.shape[0] + 1:
                generated = generated[1:]
                actions.append("drop generated initial frame (explicit metadata)")
            elif ri is True and gi is False and reference.shape[0] == generated.shape[0] + 1:
                reference = reference[1:]
                actions.append("drop reference initial frame (explicit metadata)")
            else:
                raise ValueError(f"time length mismatch {generated.shape} vs {reference.shape}; no declared initial-frame alignment")
        # float64/complex128 avoids integer overflow and preserves complex magnitudes.
        dtype = np.complex128 if np.iscomplexobj(generated) or np.iscomplexobj(reference) else np.float64
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            difference = generated.astype(dtype) - reference.astype(dtype)
            squared_error = np.square(np.abs(difference))
            rmse = float(np.sqrt(np.mean(squared_error)))
            reference_rms = float(np.sqrt(np.mean(np.square(np.abs(reference.astype(dtype))))))
            per_frame_l2 = np.sqrt(squared_error.reshape(generated.shape[0], -1).sum(axis=1))
            mean_l2 = float(per_frame_l2.mean())
        if not all(math.isfinite(value) for value in (rmse, reference_rms, mean_l2, float(per_frame_l2.max()))):
            raise ValueError("metric computation overflowed")
        relative_rmse = rmse / reference_rms if reference_rms > 0 else (0.0 if rmse == 0 else None)
        if relative_rmse is not None and not math.isfinite(relative_rmse):
            raise ValueError("relative RMSE overflowed")
        result.update(
            status="measured", shape=list(generated.shape), rmse=rmse,
            relative_rmse=relative_rmse, reference_rms=reference_rms,
            mean_l2=mean_l2, max_l2=float(per_frame_l2.max()),
            alignment_actions=actions,
        )
        if reference_rms == 0 and rmse > 0:
            result["normalization_note"] = "Relative RMSE undefined because reference RMS is zero."
    except (OSError, ValueError, TypeError, FloatingPointError) as exc:
        result["error"] = str(exc)
    return result


def _execution_status(record: dict[str, Any]) -> str:
    execution = record.get("execution", {})
    if execution.get("execution_ok") is True:
        return "passed"
    if execution.get("timeout"):
        return "timeout"
    return execution.get("status") or ("failed" if execution.get("execution_ok") is False else "not_run")


def _metadata(record: dict[str, Any]) -> dict[str, Any]:
    nested = record.get("metadata", {})
    return {**copy.deepcopy(nested), **{name: nested.get(name, record.get(name)) for name in METADATA_FIELDS}}


def _caveats(domain: str, record: dict[str, Any]) -> list[str]:
    alignment = record.get("alignment", {})
    caveats = list(record.get("comparison_caveats", []))
    if domain == "burgers2d" and not (
        alignment.get("same_initial_conditions") is True and alignment.get("initial_conditions_evidence")
    ):
        caveats.append(
            "Task initial data are Gaussian; ground-truth source uses unseeded Noise. "
            "A trajectory error measures discrepancy between these runs, not solver correctness. "
            "Matching a seed alone does not establish the same initial field."
        )
    if domain == "heat_flow" and not (
        alignment.get("operator_matches_reference") is True and alignment.get("operator_evidence")
    ):
        caveats.append(
            "Task PDE specifies x-only diffusion; ground-truth code calls multidimensional "
            "diffuse.implicit with spatial conductivity. Operator agreement is unverified."
        )
    return caveats


def evaluate_run(record: dict[str, Any], project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Enrich one runner measurement without executing code or modifying its files."""
    result = copy.deepcopy(record)
    domain = str(record["domain"])
    result["execution_status"] = _execution_status(record)
    result["metadata"] = _metadata(record)
    result["generation_status"] = record.get("generation", {}).get("status", "not_reported")
    provenance = record.get("artifact_provenance", "not_generated")
    result["artifact_provenance"] = provenance
    result["caveats"] = _caveats(domain, record)
    expected_outputs = REQUESTED_OUTPUTS.get(domain, {})
    specs = REFERENCE_SPECS.get(domain)
    numerical = []
    if not specs:
        numerical.append({
            "component": "", "status": "not_applicable", "rmse": None, "relative_rmse": None,
            "reason": "No supported ground-truth trajectory profile for this domain; no numerical score assigned.",
        })
    for component, spec in (specs or {}).items():
        reference = next((Path(project_root) / p for p in spec["paths"] if (Path(project_root) / p).is_file()), None)
        item: dict[str, Any] = {
            "component": component, "expected_output": expected_outputs[component],
            "reference_source": str(Path(project_root) / spec["source"]),
            "reference_path": str(reference) if reference else None,
            "expected_shape": list(spec["shape"]), "rmse": None, "relative_rmse": None,
            "caveats": list(result["caveats"]),
        }
        # Provenance/execution checks precede loading; stale arrays cannot be promoted.
        if result["execution_status"] != "passed":
            item.update(status="not_run", reason="No successful current-run execution; outputs are not scored.")
        elif provenance not in FRESH_PROVENANCE:
            item.update(status="not_current_run", reason="Cached/unprovenanced outputs are excluded from fresh measurements.")
        elif reference is None:
            item.update(status="reference_unavailable", reason="Supported source has no available reference array.")
        else:
            artifact = record.get("artifacts", {}).get(component)
            if not artifact:
                item.update(status="generated_artifact_missing", reason=f"Runner did not report {expected_outputs[component]}.")
            else:
                path = Path(artifact).resolve()
                run_dir = Path(record["run_dir"]).resolve() if record.get("run_dir") else None
                item["generated_path"] = str(path)
                if run_dir is None or not path.is_relative_to(run_dir):
                    item.update(status="not_current_run", reason="Artifact is outside the isolated run directory.")
                elif path.name != expected_outputs[component]:
                    item.update(status="artifact_name_mismatch", reason=f"Expected exactly {expected_outputs[component]}.")
                elif not path.is_file():
                    item.update(status="generated_artifact_missing", reason="Reported generated artifact does not exist.")
                else:
                    item.update(compare_trajectories(path, reference, expected_shape=spec["shape"], alignment=record.get("alignment")))
                    item["generated_sha256"] = sha256_file(path)
                    item["reference_sha256"] = sha256_file(reference)
                    source = Path(project_root) / spec["source"]
                    item["reference_source_sha256"] = sha256_file(source) if source.is_file() else None
                    if item["status"] == "measured" and item["caveats"]:
                        item["status"] = "measured_caveated"
        numerical.append(item)
    result["numerical"] = numerical
    result["numerical_status"] = ";".join(item["status"] for item in numerical)
    return result


def _flatten_run(record: dict[str, Any]) -> dict[str, Any]:
    execution = record.get("execution", {})
    generation = record.get("generation", {})
    return {
        "run_id": record.get("run_id", ""), "variant": record.get("variant", ""),
        "domain": record["domain"], "config_id": record.get("config_id", ""),
        "retrieval_status": record.get("retrieval_status", "not_requested"),
        "domain_status": record.get("domain_status", ""),
        "plan_source": record.get("plan", {}).get("plan_source", ""),
        "generation_source": record.get("generation_source", ""),
        "generation_status": record["generation_status"],
        "execution_status": record["execution_status"], "duration_s": execution.get("duration_s"),
        "artifact_provenance": record["artifact_provenance"],
        "numerical_status": record["numerical_status"],
        "reason": generation.get("error") or execution.get("error") or execution.get("stderr_tail") or record.get("reason") or generation.get("reason") or execution.get("reason", ""),
        **record["metadata"], **{key: record.get("context", {}).get(key) for key in CONTEXT_FIELDS},
        "run_dir": record.get("run_dir", ""), "caveats": " ".join(record["caveats"]),
    }


def _paired_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], dict[str, list[dict[str, Any]]]] = {}
    for record in records:
        key = (record["domain"], record.get("config_id", ""), record.get("replicate", 0))
        groups.setdefault(key, {}).setdefault(record.get("variant", ""), []).append(record)
    rows = []
    for (domain, config_id, replicate), variants in sorted(groups.items(), key=lambda item: str(item[0])):
        left = variants.get("code_only", [])
        right = variants.get("combined", [])
        row = {"domain": domain, "config_id": config_id, "replicate": replicate,
               "comparison_status": "unpaired", "execution_delta": None, "rmse_delta": None,
               "reason": "Requires exactly one code_only and one combined record per replicate."}
        if len(left) == len(right) == 1:
            code, combined = left[0], right[0]
            row.update(code_only_run_id=code.get("run_id"), combined_run_id=combined.get("run_id"),
                       code_only_execution=code["execution_status"], combined_execution=combined["execution_status"])
            # This compares the complete retrieval pipeline. Domain-guided code
            # retrieval is part of the treatment, so code-context hashes may
            # differ; both hashes remain visible for auditing.
            required = ("model", "task_hash", "temperature")
            row.update(code_only_code_context_hash=code["metadata"].get("code_context_hash"),
                       combined_code_context_hash=combined["metadata"].get("code_context_hash"))
            missing = [name for name in required if code["metadata"].get(name) is None or combined["metadata"].get(name) is None]
            mismatch = [name for name in (*required, "seed", "max_tokens") if code["metadata"].get(name) != combined["metadata"].get(name)]
            if any(item["artifact_provenance"] not in {"fresh", "fresh_generation"} for item in (code, combined)):
                row.update(comparison_status="not_fresh_generation", reason="No matched fresh generation outcomes; retrieval-only rows, existing-script reruns, and cached results do not measure context-conditioned generation.")
            elif missing:
                row.update(comparison_status="insufficient_control_metadata", reason="Missing matched controls: " + ", ".join(missing))
            elif mismatch:
                row.update(comparison_status="unmatched_controls", reason="Controls differ: " + ", ".join(mismatch))
            elif any(item["execution_status"] not in {"passed", "failed", "timeout"} for item in (code, combined)):
                row.update(comparison_status="not_executed", reason="Both variants require attempted current-run execution.")
            else:
                row.update(comparison_status="observed_pair", reason="Descriptive comparison of complete code-only versus domain-guided retrieval pipelines; no significance or general improvement claim.",
                           execution_delta=int(combined["execution_status"] == "passed") - int(code["execution_status"] == "passed"))
                # Domain scores are deliberately not averaged across components/caveats.
                a = {item["component"]: item for item in code["numerical"]}
                b = {item["component"]: item for item in combined["numerical"]}
                components = []
                for component in sorted(a.keys() & b.keys()):
                    if a[component]["status"] == b[component]["status"] == "measured" and a[component].get("reference_sha256") == b[component].get("reference_sha256"):
                        components.append({"component": component, "rmse_delta": b[component]["rmse"] - a[component]["rmse"]})
                row["component_rmse_deltas"] = components
                if len(components) == 1:
                    row["rmse_delta"] = components[0]["rmse_delta"]
                if code["metadata"].get("seed") is None:
                    row["reason"] += " Provider seed absent; stochastic generation is uncontrolled."
        rows.append(row)
    return rows


def _history(paths: Iterable[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inventory, rows = [], []
    for value in paths:
        path = Path(value).resolve()
        item: dict[str, Any] = {"path": str(path), "provenance": "historical_read_only", "status": "unavailable"}
        if path.is_file():
            item.update(status="available", sha256=sha256_file(path), bytes=path.stat().st_size)
            try:
                if path.suffix.lower() == ".csv":
                    with path.open(newline="", encoding="utf-8-sig") as handle:
                        content = list(csv.DictReader(handle))
                elif path.suffix.lower() == ".json":
                    parsed = json.loads(path.read_text(encoding="utf-8-sig"))
                    content = parsed if isinstance(parsed, list) else parsed.get("results", [])
                else:
                    content = []
                if not isinstance(content, list):
                    raise ValueError("historical results must be a list")
                item["rows"] = len(content)
                rows.extend({"source": str(path), "provenance": "historical_read_only", "row_index": i,
                             "data": record} for i, record in enumerate(content, start=1))
            except (OSError, ValueError, TypeError, AttributeError) as exc:
                item.update(status="read_error", error=str(exc))
        inventory.append(item)
    return inventory, rows


def build_report(
    records: Iterable[dict[str, Any]], *, project_root: Path = PROJECT_ROOT,
    tests: Iterable[dict[str, Any]] = (), graph_summary: dict[str, Any] | None = None,
    historical_paths: Iterable[Path] = (),
) -> dict[str, Any]:
    """Build a deterministic report. Fresh measurements and history stay separate."""
    enriched = [evaluate_run(record, project_root) for record in records]
    enriched.sort(key=lambda row: (row.get("config_id", ""), row["domain"], row.get("variant", ""), row.get("run_id", "")))
    history_inventory, historical_rows = _history(historical_paths)
    return {
        "schema_version": 1,
        "criteria": {
            "freshness": "Current-run artifacts inside an isolated run_dir with explicit fresh provenance and successful execution.",
            "rmse": "sqrt(mean(abs(generated - reference)**2)), over all aligned elements; lower is less discrepancy.",
            "relative_rmse": "RMSE / RMS(reference); null if reference RMS is zero and error is nonzero.",
            "l2": "Euclidean L2 per time frame; mean_l2 and max_l2 summarize frame norms.",
            "unmeasured": "Null/blank; never substituted with zero and never ranked.",
            "caveats": "measured_caveated quantifies discrepancy but is excluded from paired numerical deltas.",
            "historical": "Existing files copied as labeled historical rows, without regeneration, normalization or new-run attribution.",
        },
        "runs": enriched, "paired_comparisons": _paired_rows(enriched),
        "test_outcomes": list(tests), "graph_summary": graph_summary or {},
        "historical_inventory": history_inventory, "historical_rows": historical_rows,
        "limitations": [
            "Fresh generation outcomes require real LLM calls; offline graph/retrieval checks do not establish generation improvement.",
            "Execution success is separate from numerical agreement and physical validity.",
            "Reference hashes identify the exact stored arrays; references were not regenerated by this report.",
            "Historical RMSE/objective/physics-score formulas differ from this report and are not directly comparable.",
            "One paired sample per domain is descriptive evidence and cannot establish statistical superiority.",
        ],
    }


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str, allow_nan=False)
    return str(value)


def _table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    def escape(value: Any) -> str:
        return _cell(value).replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    lines.extend("| " + " | ".join(escape(row.get(key)) for key in columns) + " |" for row in rows)
    if not rows:
        lines.append("| " + " | ".join(["No measurements supplied"] + [""] * (len(columns) - 1)) + " |")
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    """Detailed human-readable tables; no rankings or synthetic science scores."""
    runs = [_flatten_run(record) for record in report["runs"]]
    current = [row for row in runs if row.get("generation_source") != "historical_script_rerun"]
    reruns = [row for row in runs if row.get("generation_source") == "historical_script_rerun"]
    numerical = [{"run_id": run.get("run_id"), "variant": run.get("variant"), "domain": run["domain"], **item}
                 for run in report["runs"] for item in run["numerical"]]
    sections = [
        "# Combined knowledge graph experiment report",
        "Fresh runs, graph/retrieval checks, and historical outcomes have separate provenance. "
        "Blank numerical values mean unmeasured. No overall quality ranking is assigned.",
        "## Generation and execution outcomes",
        _table(current, ["run_id", "domain", "variant", "retrieval_status", "domain_status", "plan_source", "generation_status", "execution_status", "duration_s", "artifact_provenance", "numerical_status", "reason"]),
        "## Historical script reruns (fresh execution of existing code)",
        "These scripts were generated earlier. Their new execution outcomes do not measure either retrieval arm's generation quality.",
        _table(reruns, ["run_id", "domain", "variant", "generation_source", "execution_status", "duration_s", "artifact_provenance", "numerical_status", "reason"]),
        "## Generation controls and reproducibility",
        _table(runs, ["run_id", "config_id", *METADATA_FIELDS]),
        "## Numerical discrepancy measurements",
        "RMSE is elementwise; mean/max L2 are per-frame norms. These values use different normalization "
        "from historical compute_l2_errors.py reports. Caveated measurements do not establish solver correctness.",
        _table(numerical, ["run_id", "domain", "variant", "component", "status", "shape", "rmse", "relative_rmse", "mean_l2", "max_l2", "reason", "error"]),
        "## Numerical provenance and interpretation",
        _table(numerical, ["run_id", "component", "expected_output", "generated_path", "generated_sha256", "reference_path", "reference_sha256", "reference_source_sha256", "alignment_actions", "caveats"]),
        "## Paired code-only versus combined observations",
        "Deltas are combined minus code_only. Only matched fresh-generation controls receive descriptive execution deltas; "
        "only uncaveated measurements against the same hashed reference receive component RMSE deltas.",
        _table(report["paired_comparisons"], ["domain", "config_id", "replicate", "comparison_status", "code_only_execution", "combined_execution", "execution_delta", "component_rmse_deltas", "reason"]),
        "## Graph construction and retrieval coverage",
        _table([{"measure": key, "value": value} for key, value in sorted(report["graph_summary"].items())], ["measure", "value"]),
        _table(current, ["run_id", "domain", "variant", "retrieval_status", "domain_status", "plan_source", *CONTEXT_FIELDS]),
        "## Automated test outcomes",
        _table(report["test_outcomes"], ["name", "status", "tests", "failures", "errors", "skipped", "duration_s", "details"]),
        "## Historical files (read only; not new generation results)",
        "Historical objective/physics scores and RMSE retain their original definitions. They are not "
        "combined with fresh metrics. CSV exports contain every supplied historical row; previews below show at most 20 per source.",
        _table(report["historical_inventory"], ["path", "status", "rows", "bytes", "sha256", "provenance", "error"]),
    ]
    for source in report["historical_inventory"]:
        rows = [row["data"] for row in report["historical_rows"] if row["source"] == source["path"]]
        rows = [row if isinstance(row, dict) else {"value": row} for row in rows]
        if rows:
            columns = list(dict.fromkeys(key for row in rows[:20] for key in row))
            sections.extend(["### Historical: " + source["path"], _table(rows[:20], columns)])
    sections.extend(["## Interpretation limits", "\n".join("- " + item for item in report["limitations"])])
    return "\n\n".join(sections) + "\n"


def _csv_text(rows: list[dict[str, Any]], default_fields: list[str]) -> str:
    import io
    output = io.StringIO(newline="")
    fields = list(dict.fromkeys([*default_fields, *(key for row in rows for key in row)]))
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({key: _cell(value) for key, value in row.items()} for row in rows)
    return output.getvalue()


def write_reports(
    records: Iterable[dict[str, Any]], output_dir: Path, *, project_root: Path = PROJECT_ROOT,
    tests: Iterable[dict[str, Any]] = (), graph_summary: dict[str, Any] | None = None,
    historical_paths: Iterable[Path] = (),
) -> dict[str, Path]:
    """Create JSON/CSV/Markdown reports exclusively; never overwrite existing files."""
    report = build_report(records, project_root=project_root, tests=tests, graph_summary=graph_summary,
                          historical_paths=historical_paths)
    output_dir = Path(output_dir)
    paths = {key: output_dir / name for key, name in REPORT_FILES.items()}
    collisions = [str(path) for path in paths.values() if path.exists()]
    if collisions:
        raise FileExistsError("Refusing to overwrite existing reports: " + ", ".join(collisions))
    flat = [_flatten_run(record) for record in report["runs"]]
    numerical = [{"run_id": run.get("run_id"), "variant": run.get("variant"), "domain": run["domain"], **item}
                 for run in report["runs"] for item in run["numerical"]]
    retrieval = [{"run_id": run.get("run_id"), "variant": run.get("variant"), "domain": run["domain"],
                  "retrieval_status": run.get("retrieval_status", "not_requested"),
                  "domain_status": run.get("domain_status", ""),
                  "plan_source": run.get("plan", {}).get("plan_source", ""),
                  "reason": run.get("reason", ""),
                  **run.get("context", {})} for run in report["runs"]]
    serialized = {
        "json": json.dumps(report, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n",
        "markdown": render_markdown(report),
        "csv": _csv_text(flat, ["run_id", "variant", "domain"]),
        "numerical": _csv_text(numerical, ["run_id", "variant", "domain", "component", "status", "rmse", "relative_rmse"]),
        "retrieval": _csv_text(retrieval, ["run_id", "variant", "domain", *CONTEXT_FIELDS]),
        "tests": _csv_text(report["test_outcomes"], ["name", "status", "tests", "failures", "errors", "skipped", "duration_s", "details"]),
        "paired": _csv_text(report["paired_comparisons"], ["domain", "config_id", "comparison_status", "execution_delta", "rmse_delta"]),
        "history": _csv_text(report["historical_inventory"], ["path", "status", "provenance", "sha256", "rows"]),
        "historical_rows": _csv_text(report["historical_rows"], ["source", "provenance", "row_index", "data"]),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, path in paths.items():
        with path.open("x", encoding="utf-8", newline="") as handle:
            handle.write(serialized[key])
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="Runner JSON containing runs/results records")
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory for report exports")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--historical", nargs="*", type=Path, default=[])
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    records = manifest.get("runs", manifest.get("results", [])) if isinstance(manifest, dict) else manifest
    paths = write_reports(records, args.output_dir, project_root=args.project_root,
                          tests=manifest.get("tests", []) if isinstance(manifest, dict) else [],
                          graph_summary=manifest.get("graph_summary", {}) if isinstance(manifest, dict) else {},
                          historical_paths=args.historical)
    print(f"Wrote {len(paths)} offline reports to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
