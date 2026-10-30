"""Read-only artifact audit of this completed frozen-context experiment.

Creates new audit outputs exclusively. No APIs, credentials, graphs, simulation
reruns, or evaluation-library metric helpers are used.
"""

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


RUN = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def text_digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_digest(value):
    return text_digest(json.dumps(value, sort_keys=True))


def main():
    manifest_path = RUN / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = json.loads(Path(manifest["reports"]["json"]).read_text(encoding="utf-8"))
    source_path = Path(manifest["source_snapshot"]["manifest_path"])
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source_rows = {(row.get("domain"), row.get("variant")): row for row in source["runs"]}
    report_rows = {row["run_id"]: row for row in report["runs"]}
    checks, arrays, usage = [], [], []

    def check(name, passed, detail=""):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    expected = {(domain, variant) for domain in ("burgers2d", "heat_flow", "julia_set", "reaction_diffusion")
                for variant in ("code_only", "combined")}
    check("completed manifest", bool(manifest.get("completed_utc")))
    check("exactly eight requested generation arms", len(manifest["runs"]) == 8 and {(r["domain"], r["variant"]) for r in manifest["runs"]} == expected)
    check("source manifest file hash", digest(source_path) == manifest["source_snapshot"]["manifest_sha256"])
    check("current graph integrity is explicitly unmeasured", manifest["graph_integrity"]["status"] == "not_queried")
    check("API preflight model listed", manifest["preflight"]["status"] == "passed" and manifest["preflight"]["model"] in manifest["preflight"]["available_models"])
    for record in manifest["runs"]:
        run_id = record["run_id"]
        folder = Path(record["run_dir"])
        original = source_rows[(record["domain"], record["variant"])]
        evaluated = report_rows[run_id]
        gen, execution = record["generation"], record["execution"]
        check(run_id + ": successful fresh generation and execution", gen["status"] == "generated" and execution["status"] == "passed" and execution.get("execution_ok") is True and record["artifact_provenance"] == "fresh")
        check(run_id + ": restored context remains labeled historical retrieval", record["context_origin"] == "saved_retrieval_snapshot" and record["retrieval_status"] == "restored_not_requeried")
        check(run_id + ": source record hash", canonical_digest(original) == record["source_record_hash"])
        check(run_id + ": generated script hash", digest(record["script_path"]) == record["script_sha256"])
        for name, key in (("task.md", "task_hash"), ("code_context.md", "code_context_hash"), ("domain_context.md", "domain_context_hash")):
            check(run_id + ": " + name + " normalized content hash", text_digest((folder / name).read_text(encoding="utf-8")) == record["metadata"][key])
        for name, expected_digest in record["source_file_hashes"].items():
            check(run_id + ": original " + name + " byte hash", digest(Path(record["source_directory"]) / name) == expected_digest)
        check(run_id + ": source API resolution preserved", original.get("api_resolution", []) == record["api_resolution"])
        check(run_id + ": API resolution hash", canonical_digest(record["api_resolution"]) == record["metadata"]["api_resolution_hash"])
        check(run_id + ": generation controls match metadata", all(gen.get(key) == record["metadata"].get(key) for key in ("model", "temperature", "max_tokens")))
        usage.append({"run_id": run_id, "domain": record["domain"], "variant": record["variant"],
            "context_origin": record["context_origin"], "model": gen.get("model"),
            "input_tokens": gen.get("input_tokens"), "output_tokens": gen.get("output_tokens"),
            "stop_reason": gen.get("stop_reason"), "max_tokens": gen.get("max_tokens"),
            "script_sha256": digest(record["script_path"]),
            "artifact_count_recorded": len(record["artifacts"]),
            "artifact_count_existing": sum(Path(path).is_file() for path in record["artifacts"].values()),
            "execution_status": execution.get("status"), "execution_duration_s": execution.get("duration_s")})
        for numerical in evaluated["numerical"]:
            component = numerical["component"]
            generated_path = Path(record["artifacts"][component])
            reference_path = Path(numerical["reference_path"])
            generated = np.load(generated_path, allow_pickle=False)
            reference = np.load(reference_path, allow_pickle=False)
            finite = np.isfinite(generated)
            reference_finite = np.isfinite(reference).all()
            row = {"run_id": run_id, "domain": record["domain"], "variant": record["variant"], "component": component,
                   "generated_path": str(generated_path), "generated_shape": list(generated.shape),
                   "reference_shape": list(reference.shape), "nonfinite_count": int((~finite).sum()),
                   "reference_all_finite": bool(reference_finite), "report_status": numerical["status"],
                   "report_rmse": numerical.get("rmse"), "independent_rmse": None}
            check(run_id + "/" + component + ": expected output filename", generated_path.name == numerical["expected_output"])
            check(run_id + "/" + component + ": isolated artifact path", generated_path.resolve().is_relative_to(folder.resolve()))
            check(run_id + "/" + component + ": generated data hash", digest(generated_path) == numerical["generated_sha256"])
            check(run_id + "/" + component + ": reference array hash", digest(reference_path) == numerical["reference_sha256"])
            check(run_id + "/" + component + ": reference program hash", digest(numerical["reference_source"]) == numerical["reference_source_sha256"])
            check(run_id + "/" + component + ": source-profile shape", list(generated.shape) == numerical["expected_shape"] and generated.shape == reference.shape)
            if not finite.all():
                first = int(np.flatnonzero(~finite)[0])
                row["first_nonfinite_index"] = list(np.unravel_index(first, generated.shape))
                row["first_nonfinite_index"] = [int(value) for value in row["first_nonfinite_index"]]
                check(run_id + "/" + component + ": invalid data excluded from numerical scores", numerical["status"] == "comparison_error" and numerical.get("rmse") is None and numerical.get("relative_rmse") is None)
            elif reference_finite and generated.shape == reference.shape:
                difference = generated.astype(np.float64) - reference.astype(np.float64)
                independent = float(np.sqrt(np.mean(difference * difference)))
                row["independent_rmse"] = independent
                check(run_id + "/" + component + ": independently recomputed elementwise RMSE", math.isclose(independent, numerical["rmse"], rel_tol=1e-12, abs_tol=1e-15))
            if record["domain"] in {"burgers2d", "heat_flow"}:
                check(run_id + "/" + component + ": physical comparability caveat retained", bool(numerical["caveats"]) and numerical["status"] in {"measured_caveated", "comparison_error"})
            arrays.append(row)
    check("four matched descriptive pairs", len(report["paired_comparisons"]) == 4 and all(row["comparison_status"] == "observed_pair" for row in report["paired_comparisons"]))
    check("execution deltas reflect equal pass outcomes", all(row["execution_delta"] == 0 for row in report["paired_comparisons"]))
    check("caveated domains have no numerical delta", all(not row.get("component_rmse_deltas") and row.get("rmse_delta") is None for row in report["paired_comparisons"] if row["domain"] in {"burgers2d", "heat_flow"}))
    summary = {"manifest": str(manifest_path), "manifest_sha256": digest(manifest_path),
        "source_context_date_utc": manifest["source_snapshot"]["source_completed_utc"],
        "checks": len(checks), "passed": sum(row["passed"] for row in checks),
        "failed": [row for row in checks if not row["passed"]],
        "generated_scripts": len(usage), "execution_passes": sum(row["execution_status"] == "passed" for row in usage),
        "recorded_trajectory_artifacts": sum(row["artifact_count_existing"] for row in usage),
        "input_tokens": sum(row["input_tokens"] for row in usage), "output_tokens": sum(row["output_tokens"] for row in usage),
        "interpretation": [
            "All scripts exiting successfully does not imply every trajectory is finite or physically correct.",
            "Burgers and heat reference comparisons remain caveated by initial-condition/operator disagreements.",
            "Julia and reaction-diffusion exact-array agreement is observed for these deterministic reference cases, not general proof of domain performance.",
            "Eight fresh scripts used previously saved retrieval contexts; no current graph integrity claim is made.",
            "Provider seed is absent and one sample per arm cannot establish statistical superiority.",
        ], "array_inventory": arrays, "checks_detail": checks}
    usage_path = RUN / "reports/generation_usage.csv"
    audit_path = RUN / "audit/independent_audit.json"
    if usage_path.exists() or audit_path.exists():
        raise FileExistsError("Audit outputs already exist; refusing to overwrite")
    with usage_path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(usage[0]))
        writer.writeheader()
        writer.writerows(usage)
    with audit_path.open("x", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({key: summary[key] for key in ("checks", "passed", "failed", "generated_scripts", "execution_passes", "recorded_trajectory_artifacts", "input_tokens", "output_tokens")}, indent=2))
    print("Array outcomes:")
    for row in arrays:
        print(row["run_id"], row["component"], row["generated_shape"], "nonfinite=" + str(row["nonfinite_count"]),
              "first=" + str(row.get("first_nonfinite_index")), row["report_status"], "RMSE=" + str(row["independent_rmse"]))
    print(usage_path)
    print(audit_path)


if __name__ == "__main__":
    main()
