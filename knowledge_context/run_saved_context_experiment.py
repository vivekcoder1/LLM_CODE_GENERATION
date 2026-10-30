"""Generate eight new scripts from a validated, frozen retrieval snapshot.

All eight source arms are validated before loading credentials or calling an API.
No planner, embedding model, graph driver, graph query, or graph snapshot is used.
Source contexts describe their original retrieval date; they do not establish
current graph contents. New scripts retain fresh-generation provenance.

CLI requires --context-manifest and --execute. Generated code uses the existing
AST screen, restricted child environment and timeout, which are not an OS sandbox.
For offline tests inject ``generator`` into run_saved_experiment; no API client or
credentials are constructed in that path. The normal CLI owns/closes its client.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

try:
    from .combined_evaluation import REQUESTED_OUTPUTS, sha256_file, write_reports
    from .pipeline_config import DEFAULT_MODEL, load_llm_config, redact_message
    from .run_combined_experiment import ROOT, DEFAULT_DOMAINS, _atomic_json, _hash_text, execute_script, load_pipeline_class
except ImportError:
    from combined_evaluation import REQUESTED_OUTPUTS, sha256_file, write_reports
    from pipeline_config import DEFAULT_MODEL, load_llm_config, redact_message
    from run_combined_experiment import ROOT, DEFAULT_DOMAINS, _atomic_json, _hash_text, execute_script, load_pipeline_class


class NoGraphDriver:
    """Injected guard: accidental graph access fails locally before a connection."""
    def session(self, *args, **kwargs):
        raise RuntimeError("Saved-context generation forbids graph access")

    def execute_query(self, *args, **kwargs):
        raise RuntimeError("Saved-context generation forbids graph access")

    def close(self):
        pass


class NoDomainRetriever:
    def get_domain_context(self, *args, **kwargs):
        raise RuntimeError("Saved-context generation forbids new domain retrieval")


def _canonical_hash(value: Any) -> str:
    return _hash_text(json.dumps(value, sort_keys=True, ensure_ascii=True))


def validate_source_manifest(path: Path, project_root: Path = ROOT) -> dict[str, Any]:
    """Validate every source arm without constructing clients or changing files."""
    path = Path(path).resolve()
    source = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(source, dict) or not source.get("completed_utc"):
        raise ValueError("Source must be a completed experiment manifest.")
    if not isinstance(source.get("settings"), dict) or not source.get("config_id"):
        raise ValueError("Source manifest must identify its retrieval settings and config_id.")
    expected_config = _canonical_hash(source["settings"])[:12]
    if source["config_id"] != expected_config:
        raise ValueError("Source config_id does not match its settings.")
    records = source.get("runs")
    if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
        raise ValueError("Source runs must be a list of dictionaries.")
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    errors = []
    for record in records:
        domain, variant = record.get("domain"), record.get("variant")
        if variant == "historical_rerun":
            continue
        if domain not in DEFAULT_DOMAINS or variant not in {"code_only", "combined"}:
            errors.append(f"Unexpected source arm {domain}/{variant}")
            continue
        key = domain, variant
        if key in selected:
            errors.append(f"Duplicate source arm {domain}/{variant}")
        selected[key] = record
    expected = {(domain, variant) for domain in DEFAULT_DOMAINS for variant in ("code_only", "combined")}
    for domain, variant in sorted(expected - selected.keys()):
        errors.append(f"Missing source arm {domain}/{variant}")
    validated = []
    for domain in DEFAULT_DOMAINS:
        for variant in ("code_only", "combined"):
            record = selected.get((domain, variant))
            if record is None:
                continue
            label = f"{domain}/{variant}"
            try:
                if record.get("retrieval_status") != "passed":
                    raise ValueError("original retrieval did not pass")
                if record.get("config_id") != source["config_id"]:
                    raise ValueError("source arm uses a different retrieval configuration")
                directory = Path(record["run_dir"]).resolve()
                if not directory.is_relative_to(path.parent):
                    raise ValueError("source arm directory is outside the selected snapshot")
                files = {name: directory / name for name in (
                    "task.md", "code_context.md", "domain_context.md", "context.md", "blueprint.json",
                )}
                text = {name: files[name].read_text(encoding="utf-8") for name in files}
                current_task = (Path(project_root) / "test" / f"{domain}.md").read_text(encoding="utf-8")
                metadata = record.get("metadata", {})
                if _hash_text(current_task) != metadata.get("task_hash") or text["task.md"] != current_task:
                    raise ValueError("current/saved task does not match original task_hash")
                if not text["code_context.md"].strip():
                    raise ValueError("saved public-code context is empty")
                for filename, key in (("code_context.md", "code_context_hash"), ("domain_context.md", "domain_context_hash")):
                    if _hash_text(text[filename]) != metadata.get(key):
                        raise ValueError(f"saved {filename} does not match {key}")
                if len(text["context.md"]) != record.get("context", {}).get("context_chars"):
                    raise ValueError("saved full context length does not match original context_chars")
                if variant == "combined" and (record.get("domain_status") != "available" or not text["domain_context.md"].strip()):
                    raise ValueError("combined arm requires originally available, nonempty domain context")
                if variant == "code_only" and text["domain_context.md"].strip():
                    raise ValueError("code_only arm unexpectedly contains a domain prior")
                blueprint = json.loads(text["blueprint.json"])
                if not isinstance(blueprint, dict) or not any(blueprint.get(key) for key in ("semantic_queries", "target_classes", "target_functions")):
                    raise ValueError("saved base blueprint is empty/invalid")
                resolution = record.get("api_resolution", [])
                if not isinstance(resolution, list) or not all(isinstance(item, dict) for item in resolution):
                    raise ValueError("API-resolution evidence must be a list of dictionaries")
                if metadata.get("api_resolution_hash") and _canonical_hash(resolution) != metadata["api_resolution_hash"]:
                    raise ValueError("API-resolution evidence hash does not match")
                effective_path = directory / "effective_blueprint.json"
                effective = json.loads(effective_path.read_text(encoding="utf-8")) if effective_path.is_file() else None
                if effective is not None and record.get("plan", {}).get("effective_sha256") != _canonical_hash(effective):
                    raise ValueError("effective blueprint does not match its recorded hash")
                validated.append({"domain": domain, "variant": variant, "source_record": copy.deepcopy(record),
                    "task": current_task, "code_context": text["code_context.md"],
                    "domain_context": text["domain_context.md"], "context": text["context.md"],
                    "blueprint": blueprint, "effective_blueprint": effective,
                    "api_resolution": copy.deepcopy(resolution), "source_directory": str(directory),
                    "source_file_hashes": {name: sha256_file(file) for name, file in files.items()},
                    "source_record_hash": _canonical_hash(record),
                    "full_context_integrity": "Current file hash recorded; original snapshot recorded its character count, not a full-context hash."})
            except (OSError, EOFError, ValueError, TypeError, KeyError) as exc:
                errors.append(f"{label}: {exc}")
    for domain in DEFAULT_DOMAINS:
        arms = [item for item in validated if item["domain"] == domain]
        if len(arms) == 2 and arms[0]["blueprint"] != arms[1]["blueprint"]:
            errors.append(f"{domain}: paired source base blueprints differ")
    if errors:
        raise ValueError("Saved-context validation failed before any API access:\n" + "\n".join(errors))
    return {"manifest_path": str(path), "manifest_sha256": sha256_file(path),
            "source_created_utc": source.get("created_utc"), "source_completed_utc": source["completed_utc"],
            "settings": copy.deepcopy(source["settings"]), "config_id": source["config_id"], "arms": validated}


def _stop_generation(reason: str) -> bool:
    lowered = reason.lower()
    return any(value in lowered for value in ("401", "authentication", "invalid x-api-key", "credit balance",
                                              "insufficient credits", "billing", "payment required"))


def run_saved_experiment(args, *, client=None, generator=None, executor: Callable = execute_script) -> dict[str, Any]:
    """Generate once per validated arm; failures remain records, never rerolls."""
    snapshot = validate_source_manifest(args.context_manifest, args.project_root)
    tests = []
    if args.test_results:
        tests = json.loads(Path(args.test_results).read_text(encoding="utf-8-sig"))
        if not isinstance(tests, list) or not all(isinstance(item, dict) for item in tests):
            raise ValueError("--test-results must contain a JSON list of dictionaries")
    output = Path(args.output_dir) if args.output_dir else Path(args.project_root) / "integration_runs" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ") + "_saved_context")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    provenance = {key: value for key, value in snapshot.items() if key != "arms"}
    manifest: dict[str, Any] = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "generate_saved_context", "output_dir": str(output), "context_origin": "saved_retrieval_snapshot",
        "source_snapshot": provenance, "settings": snapshot["settings"], "config_id": snapshot["config_id"],
        "runs": [], "tests": tests, "graph_integrity": {"status": "not_queried", "reason": "No graph connections, queries, or current integrity checks in saved-context mode."},
        "execution_limitations": "AST screen and restricted child environment are not an OS sandbox."}
    _atomic_json(output / "manifest.json", manifest)
    owned_client = False
    model = args.model or DEFAULT_MODEL
    allowed, block_reason = False, ""
    try:
        try:
            if generator is not None:
                allowed = True
                manifest["preflight"] = {"status": "injected_offline_generator", "model": model}
            else:
                if client is None:
                    # Every source arm has already passed validation above.
                    llm = load_llm_config(args.llm_env_file, args.model)
                    model = llm["model"]
                    import anthropic
                    headers = {"anthropic-workspace-id": llm["workspace_id"]} if llm.get("workspace_id") else None
                    client = anthropic.Anthropic(api_key=llm["api_key"], default_headers=headers, timeout=120, max_retries=0)
                    owned_client = True
                available = [item.id for item in client.models.list(limit=100)]
                allowed = model in available
                manifest["preflight"] = {"status": "passed" if allowed else "blocked", "model": model, "available_models": available}
                if not allowed:
                    raise ValueError("Requested model was not listed by the selected account")
                generator = load_pipeline_class(args.project_root)(
                    driver=NoGraphDriver(), client=client, embed_model=None,
                    domain_retriever=NoDomainRetriever(), database=None, model=model,
                    allow_llm=True, domain_graph_path=None,
                )
        except Exception as exc:
            allowed, block_reason = False, redact_message(exc)
            manifest["preflight"] = {"status": "blocked", "model": model, "error": block_reason}
        for arm in snapshot["arms"]:
            domain, variant = arm["domain"], arm["variant"]
            directory = output / "runs" / domain / (variant + "_0")
            directory.mkdir(parents=True, exist_ok=False)
            record = {"run_id": f"{domain}_{variant}_0", "domain": domain, "variant": variant, "replicate": 0,
                "config_id": snapshot["config_id"], "run_dir": str(directory),
                "context_origin": "saved_retrieval_snapshot", "retrieval_status": "restored_not_requeried",
                "domain_status": arm["source_record"].get("domain_status"),
                "context": copy.deepcopy(arm["source_record"].get("context", {})),
                "api_resolution": copy.deepcopy(arm["api_resolution"]),
                "source_snapshot": provenance, "source_record": arm["source_record"],
                "source_record_hash": arm["source_record_hash"], "source_directory": arm["source_directory"],
                "source_file_hashes": arm["source_file_hashes"], "full_context_integrity": arm["full_context_integrity"],
                "plan": {"plan_source": "saved_retrieval_snapshot", "base_sha256": _canonical_hash(arm["blueprint"])},
                "metadata": {"model": model, "temperature": 0, "seed": None, "max_tokens": args.max_tokens,
                    "task_hash": _hash_text(arm["task"]), "code_context_hash": _hash_text(arm["code_context"]),
                    "domain_context_hash": _hash_text(arm["domain_context"]), "api_resolution_hash": _canonical_hash(arm["api_resolution"])},
                "alignment": copy.deepcopy(arm["source_record"].get("alignment", {"generated_time_axis": 0, "reference_time_axis": 0})),
                "generation": {"status": "blocked", "error": block_reason or "Generation unavailable"},
                "execution": {"status": "not_run"}, "artifact_provenance": "not_generated", "artifacts": {}}
            for name, value in (("task.md", arm["task"]), ("code_context.md", arm["code_context"]),
                                ("domain_context.md", arm["domain_context"]), ("context.md", arm["context"])):
                (directory / name).write_text(value, encoding="utf-8")
            _atomic_json(directory / "blueprint.json", arm["blueprint"])
            _atomic_json(directory / "api_resolution.json", arm["api_resolution"])
            if arm["effective_blueprint"] is not None:
                _atomic_json(directory / "effective_blueprint.json", arm["effective_blueprint"])
            if allowed:
                try:
                    generate = generator.generate_grounded_code if hasattr(generator, "generate_grounded_code") else generator
                    code = generate(arm["task"], arm["code_context"], max_tokens=args.max_tokens,
                                    domain_context=arm["domain_context"], api_resolution=copy.deepcopy(arm["api_resolution"]))
                    if not isinstance(code, str) or not code.strip():
                        raise ValueError("Generation returned empty/nontext code")
                    script = directory / f"generated_{domain}_simulation.py"
                    script.write_text(code, encoding="utf-8")
                    record.update(generation_source="fresh_llm", artifact_provenance="fresh", script_path=str(script), script_sha256=sha256_file(script))
                    record["generation"] = {**copy.deepcopy(getattr(generator, "last_generation_metadata", {})), "status": "generated"}
                    record["execution"] = executor(script, timeout=args.timeout, project_root=Path(args.project_root)) if args.execute else {"status": "not_run", "reason": "Execution not enabled"}
                    record["artifacts"] = {component: str(directory / filename) for component, filename in REQUESTED_OUTPUTS[domain].items() if (directory / filename).is_file()}
                    record["observed_artifacts"] = [{"filename": path.name, "path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
                                                    for path in sorted(directory.glob("*.npy")) if path.is_file()]
                except Exception as exc:
                    reason = redact_message(exc)
                    record["generation"] = {**copy.deepcopy(getattr(generator, "last_generation_metadata", {})), "status": "failed", "error": reason}
                    record["execution"] = {"status": "not_run", "error": reason}
                    if _stop_generation(reason):
                        allowed, block_reason = False, "Further generation blocked after authentication/credits failure: " + reason
            _atomic_json(directory / "record.json", record)
            manifest["runs"].append(record)
            _atomic_json(output / "manifest.json", manifest)
            print(f"{domain}/{variant}: context=saved_snapshot generation={record['generation']['status']} execution={record['execution']['status']}", flush=True)
    finally:
        if owned_client and client is not None:
            client.close()
        manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
        _atomic_json(output / "manifest.json", manifest)
    historical = [Path(args.project_root) / "evaluation_report.csv", Path(args.project_root) / "evaluation_report.json",
                  Path(args.project_root) / "l2summary.csv"]
    paths = write_reports(manifest["runs"], output / "reports", project_root=Path(args.project_root), tests=tests,
                          graph_summary={"context_origin": "saved_retrieval_snapshot", "source_snapshot": provenance,
                                         "live_graph_status": "not_queried", "model_preflight": manifest.get("preflight")},
                          historical_paths=historical)
    manifest["reports"] = {key: str(path) for key, path in paths.items()}
    _atomic_json(output / "manifest.json", manifest)
    return manifest


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context-manifest", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--llm-env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--model")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--test-results", type=Path)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--max-tokens", type=int, default=20000)
    args = parser.parse_args(argv)
    if args.timeout < 1 or args.max_tokens < 1:
        parser.error("timeout and max-tokens must be positive")
    return args


def main(argv=None):
    manifest = run_saved_experiment(parse_args(argv))
    print("Manifest:", Path(manifest["output_dir"]) / "manifest.json")
    print("Report:", manifest["reports"]["markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
