"""Run isolated retrieval comparisons and optional simulation experiments.

Default ``retrieval`` mode uses hash-matched cached search blueprints. It never
loads LLM credentials, constructs an LLM SDK client, lists models, or calls an
LLM. ``existing`` and ``--also-rerun-existing`` execute historical scripts only
when ``--execute`` is explicit, and label them historical_rerun, once per domain.
``generate`` is opt-in, checks the requested model is listed, and is the only
mode permitted to call blueprint/code generation. No database writes occur.

Execution uses a new directory, a restricted child environment, an AST screen,
and a timeout. This is a precaution, not an operating-system security sandbox;
only execute generated code that you trust. Reports never overwrite originals.

Inject ``pipeline``/``runtime``/``executor`` into run_experiment for offline tests.
The pipeline contract is E2ERagPipeline.retrieve_context(domain, task, variant,
blueprint, settings) and generate_grounded_code(task, code_context, max_tokens,
domain_context, api_resolution). Runtime dictionaries contain ``connections`` [{role,driver,
database,description}], ``preflight``, ``generation_allowed``, ``model``, and
``errors``; authentication secrets are never serialized.
"""

from __future__ import annotations

import argparse
import ast
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import subprocess
import sys
import time
from typing import Any, Callable

try:
    from .combined_evaluation import REQUESTED_OUTPUTS, sha256_file, write_reports
    from .pipeline_config import DEFAULT_MODEL, redact_message
except ImportError:
    from combined_evaluation import REQUESTED_OUTPUTS, sha256_file, write_reports
    from pipeline_config import DEFAULT_MODEL, redact_message


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOMAINS = ("burgers2d", "heat_flow", "julia_set", "reaction_diffusion")
DEFAULT_SETTINGS = {
    "top_k": 32, "min_score": .2, "method_min_score": .3,
    "max_methods_per_class": 5, "max_nodes": 12, "fulltext_limit": 5,
    "description_limit": 8, "function_limit": 6, "class_limit": 6,
    "public_boost": .20, "private_penalty": .15, "max_semantic_queries": 12,
    "max_target_classes": 24, "max_target_functions": 32,
}
REQUIRED_INDEXES = {"classNames", "functionNames", "descEmbed", "funcDocEmbed", "classDocEmbed"}
FORBIDDEN_IMPORTS = {
    "neo4j", "anthropic", "dotenv", "requests", "httpx", "urllib", "socket",
    "subprocess", "os", "shutil", "pathlib", "builtins", "importlib", "ctypes",
}
FORBIDDEN_CALLS = {"eval", "exec", "__import__", "compile", "open", "getattr", "setattr", "delattr"}


class DisabledLLMClient:
    """An explicit injected sentinel makes unexpected LLM access fail locally."""
    def __getattr__(self, name):
        raise RuntimeError("LLM access is disabled in retrieval/existing mode")


def _progress(message: str) -> None:
    print("[combined experiment] " + message, flush=True)


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _read_rows(driver, database: str | None, query: str) -> list[dict[str, Any]]:
    with driver.session(database=database, default_access_mode="READ") as session:
        return session.execute_read(lambda tx: [dict(row) for row in tx.run(query)])


def graph_snapshot(driver, database: str | None = None, *, role: str = "graph") -> dict[str, Any]:
    """Count/hash graph element IDs using only READ transactions, without properties."""
    snapshot: dict[str, Any] = {"status": "available", "scope": "counts_and_element_ids_only; properties_not_hashed"}
    for label, query in (
        ("nodes", "MATCH (n) RETURN elementId(n) AS element_id ORDER BY element_id"),
        ("relationships", "MATCH ()-[r]->() RETURN elementId(r) AS element_id ORDER BY element_id"),
    ):
        _progress(f"{role}: READ snapshot {label} IDs")
        rows = _read_rows(driver, database, query)
        digest = hashlib.sha256()
        for row in rows:
            digest.update((str(row["element_id"]) + "\n").encode("utf-8"))
        snapshot[label + "_count"] = len(rows)
        snapshot[label + "_id_sha256"] = digest.hexdigest()
        _progress(f"{role}: READ snapshot {label} complete ({len(rows)} IDs)")
    _progress(f"{role}: READ index names/status")
    snapshot["indexes"] = _read_rows(driver, database,
        "SHOW INDEXES YIELD name, state, type RETURN name, state, type ORDER BY name")
    _progress(f"{role}: READ indexes complete ({len(snapshot['indexes'])} indexes)")
    return snapshot


def _snapshot_connections(connections: list[dict[str, Any]]) -> dict[str, Any]:
    snapshots = {}
    for connection in connections:
        try:
            role = connection["role"]
            _progress(f"{role}: starting READ-only graph snapshot")
            snapshots[role] = graph_snapshot(connection["driver"], connection.get("database"), role=role)
            _progress(f"{role}: READ-only graph snapshot complete")
        except Exception as exc:
            snapshots[connection["role"]] = {"status": "unavailable", "error": redact_message(exc)}
            _progress(f"{connection['role']}: READ-only graph snapshot unavailable (details saved in manifest)")
    return snapshots


def compare_graph_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Unavailable reads never count as proof of unchanged graph topology."""
    comparison = {}
    fields = ("nodes_count", "relationships_count", "nodes_id_sha256", "relationships_id_sha256")
    for role in sorted(before.keys() | after.keys()):
        a, b = before.get(role, {}), after.get(role, {})
        if a.get("status") != "available" or b.get("status") != "available":
            comparison[role] = "unavailable"
        elif all(a.get(key) == b.get(key) and a.get(key) is not None for key in fields):
            comparison[role] = "unchanged_topology_ids"
        else:
            comparison[role] = "changed_topology_ids"
    return comparison


def load_pipeline_class(root: Path = ROOT):
    # A direct ``python knowledge_context/run_combined_experiment.py`` invocation
    # puts knowledge_context, rather than its package parent, on sys.path.
    if str(Path(root).resolve()) not in sys.path:
        sys.path.insert(0, str(Path(root).resolve()))
    spec = importlib.util.spec_from_file_location("combined_experiment_llm_querying", Path(root) / "llm-querying.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not import llm-querying.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.E2ERagPipeline


def prepare_runtime(args) -> tuple[Any, dict[str, Any]]:
    """Create explicit read connections; LLM configuration is accessed only in generate mode."""
    try:
        from .pipeline_config import load_connection_config, load_llm_config, create_read_driver, describe_connection
        from .domain_retrieval import DomainKnowledgeRetriever
    except ImportError:
        from pipeline_config import load_connection_config, load_llm_config, create_read_driver, describe_connection
        from domain_retrieval import DomainKnowledgeRetriever
    runtime: dict[str, Any] = {"connections": [], "preflight": {}, "errors": [],
                               "generation_allowed": False, "model": args.model or DEFAULT_MODEL}
    if args.mode == "existing":
        runtime["preflight"] = {"llm": {"status": "not_requested"}, "graphs": {"status": "not_requested"}}
        return None, runtime
    code_driver = None
    code_database = None
    # Passing None would authorize the pipeline constructor's default JSON
    # adapter. An explicit unavailable adapter prevents a failed selected source
    # from silently becoming a different source.
    domain_retriever = DomainKnowledgeRetriever()
    try:
        _progress("code: reading the explicitly selected credentials file")
        config = load_connection_config(args.code_env_file, "code", args.project_root)
        code_driver, code_database = create_read_driver(config), config.get("database")
        _progress("code: lazy READ driver constructed")
        runtime["connections"].append({"role": "code", "driver": code_driver, "database": code_database,
                                       "description": describe_connection(config, args.code_env_file, "code")})
    except Exception as exc:
        runtime["errors"].append("Code connection: " + redact_message(exc))
        _progress("code: configuration unavailable (details saved in manifest)")
    try:
        if args.domain_source == "json":
            _progress("domain: loading the explicitly selected local graph JSON")
            domain_retriever = DomainKnowledgeRetriever.from_json(args.domain_graph_json)
            _progress("domain: local graph JSON loaded")
        else:
            _progress("domain: reading the explicitly selected credentials file")
            config = load_connection_config(args.domain_env_file, "domain", args.project_root)
            driver = create_read_driver(config)
            _progress("domain: lazy READ driver constructed")
            runtime["connections"].append({"role": "domain", "driver": driver, "database": config.get("database"),
                                           "description": describe_connection(config, args.domain_env_file, "domain")})
            domain_retriever = DomainKnowledgeRetriever(driver=driver, database=config.get("database"))
    except Exception as exc:
        runtime["errors"].append("Domain connection: " + redact_message(exc))
        _progress("domain: configuration unavailable (details saved in manifest)")
    before = _snapshot_connections(runtime["connections"])
    runtime["preflight"]["graphs"] = before
    code_snapshot = before.get("code", {})
    online = {row["name"] for row in code_snapshot.get("indexes", []) if row.get("state") == "ONLINE"}
    missing = sorted(REQUIRED_INDEXES - online)
    runtime["preflight"]["required_indexes"] = {"status": "passed" if not missing else "blocked", "missing_or_offline": missing}
    _progress("code: required retrieval indexes " + ("ONLINE" if not missing else "missing or offline; retrieval blocked"))
    if missing:
        runtime["errors"].append("Code retrieval indexes missing/offline: " + ", ".join(missing))
    client: Any = DisabledLLMClient()
    if args.mode == "generate":
        try:
            import anthropic
            llm = load_llm_config(args.llm_env_file, args.model)
            runtime["model"] = llm["model"]
            headers = {"anthropic-workspace-id": llm["workspace_id"]} if llm.get("workspace_id") else None
            client = anthropic.Anthropic(api_key=llm["api_key"], default_headers=headers, max_retries=0)
            available = [item.id for item in client.models.list(limit=100)]
            allowed = runtime["model"] in available
            runtime["generation_allowed"] = allowed
            runtime["preflight"]["llm"] = {"status": "passed" if allowed else "blocked", "model": runtime["model"], "available_models": available}
            if not allowed:
                runtime["errors"].append("Requested model was not listed by the selected account.")
        except Exception as exc:
            runtime["preflight"]["llm"] = {"status": "blocked", "error": redact_message(exc)}
            runtime["errors"].append("LLM preflight: " + redact_message(exc))
    else:
        runtime["preflight"]["llm"] = {"status": "not_requested", "reason": "Retrieval mode makes no LLM/API calls."}
        _progress("LLM/API access disabled for retrieval mode")
    pipeline = None
    if code_driver is not None and not missing:
        try:
            _progress("embedding: importing local SentenceTransformer runtime")
            from sentence_transformers import SentenceTransformer
            _progress("embedding: loading cached model with local_files_only=True")
            embedder = SentenceTransformer(args.embedding_model, local_files_only=True)
            _progress("embedding: cached model loaded")
            _progress("pipeline: initializing injected READ-only retrieval components")
            pipeline = load_pipeline_class(args.project_root)(
                driver=code_driver, client=client, embed_model=embedder,
                domain_retriever=domain_retriever, database=code_database,
                model=runtime["model"], code_env_file=args.code_env_file, llm_env_file=args.llm_env_file,
                allow_llm=args.mode == "generate",
            )
            _progress("pipeline: retrieval initialization complete")
        except Exception as exc:
            runtime["errors"].append("Pipeline initialization: " + redact_message(exc))
            _progress("pipeline: initialization unavailable (details saved in manifest)")
    return pipeline, runtime


def cached_blueprint(domain: str, task: str, directory: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Require the original optimizer's exact domain + SHA1(task) filename."""
    task_sha1 = hashlib.sha1(task.encode("utf-8")).hexdigest()
    path = Path(directory) / f"{domain}_{task_sha1[:12]}_blueprint.json"
    if not path.is_file():
        raise ValueError(f"No cached blueprint matching this task: {path}")
    plan = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(plan, dict) or not any(plan.get(key) for key in ("semantic_queries", "target_classes", "target_functions")):
        raise ValueError(f"Cached blueprint is empty or invalid: {path}")
    for key in ("semantic_queries", "target_classes", "target_functions"):
        if not isinstance(plan.get(key, []), list) or not all(isinstance(item, str) for item in plan.get(key, [])):
            raise ValueError(f"Cached blueprint field {key} must be a list of strings")
    return plan, {"plan_source": "cached", "path": str(path.resolve()), "sha256": sha256_file(path), "task_sha1": task_sha1}


def inspect_script(source: str) -> list[str]:
    """Screen obvious credential/network/process access. This is not a sandbox."""
    issues = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"SyntaxError line {exc.lineno}: {exc.msg}"]
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for name in names:
                if name.split(".")[0] in FORBIDDEN_IMPORTS:
                    issues.append(f"Forbidden import {name} at line {node.lineno}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            issues.append(f"Dunder attribute access at line {node.lineno}")
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if name in FORBIDDEN_CALLS:
                issues.append(f"Forbidden call {name} at line {node.lineno}")
            if name in {"save", "savez", "savez_compressed", "savetxt", "tofile"}:
                target = node.args[0] if node.args else next((item.value for item in node.keywords if item.arg in {"file", "fname"}), None)
                if not isinstance(target, ast.Constant) or not isinstance(target.value, str):
                    issues.append(f"Output path must be a literal relative filename at line {node.lineno}")
                else:
                    value = target.value
                    windows, posix = PureWindowsPath(value), PurePosixPath(value)
                    if windows.is_absolute() or windows.drive or posix.is_absolute() or ".." in windows.parts or ".." in posix.parts:
                        issues.append(f"Absolute/traversal output path at line {node.lineno}")
    return sorted(set(issues))


def child_environment(project_root: Path) -> dict[str, str]:
    """Allow only OS/runtime settings; no inherited authentication/configuration."""
    allowed = {"SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "COMSPEC", "TEMP", "TMP", "LOCALAPPDATA",
               "APPDATA", "USERPROFILE", "HOME", "LANG", "LC_ALL", "OMP_NUM_THREADS", "MKL_NUM_THREADS"}
    environment = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    local_source = Path(project_root) / "phiflow"
    environment["PYTHONPATH"] = str(local_source) if local_source.is_dir() else str(project_root)
    environment.update(MPLBACKEND="Agg", PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
                       HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    return environment


def execute_script(script_path: Path, *, timeout: int, project_root: Path) -> dict[str, Any]:
    started = time.perf_counter()
    issues = inspect_script(script_path.read_text(encoding="utf-8"))
    if issues:
        return {"status": "blocked", "execution_ok": False, "error": "; ".join(issues), "duration_s": 0.0,
                "execution_guard": "AST screen; not an OS sandbox"}
    try:
        result = subprocess.run([sys.executable, str(script_path.resolve())], cwd=script_path.parent,
                                env=child_environment(project_root), capture_output=True, text=True,
                                timeout=timeout, encoding="utf-8", errors="replace")
        (script_path.parent / "stdout.txt").write_text(result.stdout, encoding="utf-8")
        (script_path.parent / "stderr.txt").write_text(result.stderr, encoding="utf-8")
        return {"status": "passed" if result.returncode == 0 else "failed", "execution_ok": result.returncode == 0,
                "exit_code": result.returncode, "duration_s": round(time.perf_counter() - started, 6),
                "error": result.stderr[-1500:] if result.returncode else "",
                "execution_guard": "AST screen and restricted environment; not an OS sandbox"}
    except subprocess.TimeoutExpired as exc:
        def decoded(value):
            return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""
        (script_path.parent / "stdout.txt").write_text(decoded(exc.stdout), encoding="utf-8")
        (script_path.parent / "stderr.txt").write_text(decoded(exc.stderr), encoding="utf-8")
        return {"status": "timeout", "timeout": True, "execution_ok": False,
                "duration_s": round(time.perf_counter() - started, 6), "error": f"Execution exceeded {timeout} seconds."}
    except Exception as exc:
        return {"status": "failed", "execution_ok": False, "duration_s": round(time.perf_counter() - started, 6),
                "error": redact_message(exc)}


def _run_record(domain, variant, replicate, directory, config_id, task, model):
    return {"run_id": f"{domain}_{variant}_{replicate}", "domain": domain, "variant": variant,
            "replicate": replicate, "config_id": config_id, "run_dir": str(directory.resolve()),
            "generation": {"status": "not_requested"}, "execution": {"status": "not_run"},
            "artifact_provenance": "not_generated", "artifacts": {}, "context": {},
            "metadata": {"model": model, "temperature": 0, "seed": None, "task_hash": _hash_text(task)},
            "alignment": {"generated_time_axis": 0, "reference_time_axis": 0}}


def _artifacts(record):
    directory = Path(record["run_dir"])
    return {component: str(directory / filename) for component, filename in REQUESTED_OUTPUTS.get(record["domain"], {}).items()
            if (directory / filename).is_file()}


def run_experiment(args, *, pipeline=None, runtime=None, executor: Callable = execute_script) -> dict[str, Any]:
    """Persist every arm incrementally, including blocked and failed outcomes."""
    project_root = Path(args.project_root).resolve()
    output = Path(args.output_dir) if args.output_dir else project_root / "integration_runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    settings = copy.deepcopy(DEFAULT_SETTINGS)
    if args.settings_file:
        settings.update(json.loads(Path(args.settings_file).read_text(encoding="utf-8")))
    config_id = _hash_text(json.dumps(settings, sort_keys=True))[:12]
    manifest: dict[str, Any] = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
                               "mode": args.mode, "settings": settings, "config_id": config_id,
                               "output_dir": str(output), "runs": [], "tests": [],
                               "generation_policy": "No fresh LLM calls in retrieval/existing modes.",
                               "execution_limitations": "AST screening/restricted environment are not an OS sandbox."}
    if args.test_results:
        test_path = Path(args.test_results).resolve()
        tests = json.loads(test_path.read_text(encoding="utf-8-sig"))
        if not isinstance(tests, list) or not all(isinstance(item, dict) for item in tests):
            raise ValueError("--test-results must contain a JSON list of per-test dictionaries.")
        manifest["tests"] = tests
        manifest["test_results_source"] = {"path": str(test_path), "sha256": sha256_file(test_path)}
    _atomic_json(output / "manifest.json", manifest)
    owned = runtime is None
    if runtime is None:
        if pipeline is None:
            try:
                pipeline, runtime = prepare_runtime(args)
            except Exception as exc:
                runtime = {"connections": [], "preflight": {}, "errors": [redact_message(exc)], "generation_allowed": False}
        else:
            runtime = {"connections": [], "preflight": {"status": "injected"}, "errors": [],
                       "generation_allowed": False, "model": args.model or DEFAULT_MODEL}
    manifest["preflight"] = copy.deepcopy(runtime.get("preflight", {}))
    manifest["connections"] = [item["description"] for item in runtime.get("connections", []) if item.get("description")]
    manifest["preflight_errors"] = list(runtime.get("errors", []))
    before = manifest["preflight"].get("graphs", {})
    try:
        for domain in args.domains:
            task_path = project_root / "test" / f"{domain}.md"
            try:
                task = task_path.read_text(encoding="utf-8")
                task_error = ""
            except Exception as exc:
                task, task_error = "", redact_message(exc)
            blueprint, plan_metadata, plan_error = {}, {}, task_error
            if args.mode != "existing" and not plan_error:
                try:
                    if args.mode == "generate" and runtime.get("generation_allowed") and pipeline is not None:
                        blueprint = pipeline.generate_search_blueprint(task)
                        if not isinstance(blueprint, dict) or not any(blueprint.get(key) for key in ("semantic_queries", "target_classes", "target_functions")):
                            reason = getattr(pipeline, "last_blueprint_error", "") or "Planner returned an empty/invalid blueprint."
                            runtime["generation_allowed"] = False
                            runtime.setdefault("errors", []).append("Planner failed; generation blocked: " + redact_message(reason))
                            blueprint, plan_metadata = cached_blueprint(domain, task, args.blueprint_dir)
                            plan_metadata["planner_error"] = redact_message(reason)
                        else:
                            plan_metadata = {"plan_source": "fresh_llm", "sha256": _hash_text(json.dumps(blueprint, sort_keys=True))}
                    else:
                        blueprint, plan_metadata = cached_blueprint(domain, task, args.blueprint_dir)
                except Exception as exc:
                    plan_error = redact_message(exc)
            for replicate in range(args.repeats):
                variants = ["historical_rerun"] if args.mode == "existing" else ["code_only", "combined"]
                if args.mode == "retrieval" and args.also_rerun_existing:
                    variants.append("historical_rerun")
                for variant in variants:
                    run_dir = output / "runs" / domain / f"{variant}_{replicate}"
                    run_dir.mkdir(parents=True, exist_ok=False)
                    record = _run_record(domain, variant, replicate, run_dir, config_id, task, runtime.get("model") if args.mode == "generate" else None)
                    record["metadata"]["max_tokens"] = args.max_tokens if args.mode == "generate" else None
                    record["plan"] = copy.deepcopy(plan_metadata)
                    record["task_source"] = str(task_path)
                    (run_dir / "task.md").write_text(task, encoding="utf-8")
                    _atomic_json(run_dir / "blueprint.json", blueprint)
                    try:
                        if variant == "historical_rerun":
                            record["generation_source"] = "historical_script_rerun"
                            record["generation"] = {"status": "historical_script", "reason": "Existing code; no context-conditioned generation."}
                            source = project_root / f"test_{domain}" / f"generated_{domain}_simulation.py"
                            script = run_dir / source.name
                            if not source.is_file():
                                raise ValueError(f"Existing script is missing: {source}")
                            shutil.copyfile(source, script)
                            record["script_source"] = str(source)
                            record["script_sha256"] = sha256_file(script)
                            record["artifact_provenance"] = "existing_outputs_rerun"
                        else:
                            if task_error or plan_error:
                                raise ValueError(task_error or plan_error)
                            if pipeline is None:
                                raise ValueError("Retrieval unavailable: " + "; ".join(runtime.get("errors", ["No pipeline"])) )
                            context = pipeline.retrieve_context(domain, task, variant=variant,
                                                                blueprint=copy.deepcopy(blueprint), settings=copy.deepcopy(settings))
                            effective_plan = context.get("blueprint", blueprint)
                            _atomic_json(run_dir / "effective_blueprint.json", effective_plan)
                            record["plan"]["effective_sha256"] = _hash_text(json.dumps(effective_plan, sort_keys=True))
                            code_context = context.get("code_context", "")
                            domain_context = context.get("domain_context", "")
                            record["context"] = copy.deepcopy(context.get("statistics", {}))
                            record["retrieval_status"] = "passed"
                            record["domain_status"] = context.get("domain_status")
                            record["api_resolution"] = copy.deepcopy(context.get("api_resolution", []))
                            record["metadata"]["api_resolution_hash"] = _hash_text(json.dumps(record["api_resolution"], sort_keys=True))
                            _atomic_json(run_dir / "retrieval_metadata.json", {
                                key: context.get(key) for key in ("statistics", "domain_status", "api_resolution", "provenance")
                            })
                            record["metadata"].update(code_context_hash=_hash_text(code_context), domain_context_hash=_hash_text(domain_context))
                            for filename, value in (("code_context.md", code_context), ("domain_context.md", domain_context),
                                                    ("context.md", context.get("context", code_context + "\n" + domain_context))):
                                (run_dir / filename).write_text(value, encoding="utf-8")
                            if args.mode == "retrieval":
                                record["generation"] = {"status": "not_requested", "reason": "Retrieval-only mode; no LLM call."}
                                script = None
                            elif not runtime.get("generation_allowed"):
                                record["generation"] = {"status": "blocked", "error": "; ".join(runtime.get("errors", [])) or "LLM model/auth preflight did not pass."}
                                script = None
                            elif variant == "combined" and (record.get("domain_status") != "available" or not domain_context.strip()):
                                record["generation"] = {"status": "blocked", "error": "Combined generation requires available, nonempty domain evidence from the selected source."}
                                script = None
                            else:
                                code = pipeline.generate_grounded_code(
                                    task, code_context, max_tokens=args.max_tokens,
                                    domain_context=domain_context, api_resolution=context.get("api_resolution", []),
                                )
                                if not code.strip():
                                    raise ValueError("Generation returned empty code")
                                script = run_dir / f"generated_{domain}_simulation.py"
                                script.write_text(code, encoding="utf-8")
                                record["script_sha256"] = sha256_file(script)
                                record["generation"] = {"status": "generated", **copy.deepcopy(getattr(pipeline, "last_generation_metadata", {}))}
                                record["generation_source"] = "fresh_llm"
                                record["artifact_provenance"] = "fresh"
                        if script is not None:
                            record["script_path"] = str(script)
                            if args.execute:
                                record["execution"] = executor(script, timeout=args.timeout, project_root=project_root)
                                record["artifacts"] = _artifacts(record)
                                record["observed_artifacts"] = [
                                    {"filename": path.name, "path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
                                    for path in sorted(run_dir.glob("*.npy")) if path.is_file()
                                ]
                            else:
                                record["execution"] = {"status": "not_run", "reason": "Pass --execute to execute scripts."}
                    except Exception as exc:
                        reason = redact_message(exc)
                        record["reason"] = reason
                        if variant != "historical_rerun" and not record.get("context"):
                            record["retrieval_status"] = "blocked"
                        record["generation"] = {"status": "blocked" if args.mode != "generate" else "failed", "error": reason}
                        record["execution"] = {"status": "not_run", "error": reason}
                        # A 401/auth failure prevents repeated paid/rejected generation attempts.
                        if any(marker in reason.lower() for marker in ("401", "authentication", "invalid x-api-key")):
                            runtime["generation_allowed"] = False
                            runtime.setdefault("errors", []).append("Generation blocked after authentication failure: " + reason)
                    _atomic_json(run_dir / "record.json", record)
                    manifest["runs"].append(record)
                    manifest["preflight_errors"] = list(runtime.get("errors", []))
                    _atomic_json(output / "manifest.json", manifest)
                    print(f"{domain} / {variant} / {replicate}: retrieval={record.get('retrieval_status', 'not_requested')} generation={record['generation']['status']} execution={record['execution']['status']}", flush=True)
    finally:
        after = _snapshot_connections(runtime.get("connections", []))
        manifest["graph_integrity"] = {"before": before, "after": after,
            "scope": "Counts and element-ID sets only; property values and concurrent changes are not attributed.",
            "comparison": compare_graph_snapshots(before, after)}
        if owned:
            for connection in runtime.get("connections", []):
                try:
                    connection["driver"].close()
                except Exception:
                    pass
        manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
        _atomic_json(output / "manifest.json", manifest)
    graph_summary = {"preflight": manifest["preflight"], "graph_integrity": manifest["graph_integrity"],
                     "retrieval_arms": sum(item.get("retrieval_status") == "passed" for item in manifest["runs"]),
                     "fresh_generations": sum(item.get("generation_source") == "fresh_llm" for item in manifest["runs"]),
                     "historical_reruns": sum(item.get("generation_source") == "historical_script_rerun" for item in manifest["runs"])}
    historical = [project_root / "evaluation_report.csv", project_root / "evaluation_report.json", project_root / "l2summary.csv",
                  project_root / "optimization_runs/pruned_cross_domain/cross_domain_execution_summary.csv",
                  project_root / "optimization_runs/pruned_cross_domain/cross_domain_quality_ranking.csv"]
    paths = write_reports(manifest["runs"], output / "reports", project_root=project_root,
                          tests=manifest["tests"], graph_summary=graph_summary, historical_paths=historical)
    manifest["reports"] = {key: str(path) for key, path in paths.items()}
    _atomic_json(output / "manifest.json", manifest)
    return manifest


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["retrieval", "generate", "existing"], default="retrieval")
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--domains", nargs="+", choices=sorted(REQUESTED_OUTPUTS), default=list(DEFAULT_DOMAINS))
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--also-rerun-existing", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--max-tokens", type=int, default=20000)
    parser.add_argument("--model")
    parser.add_argument("--code-env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--domain-env-file", type=Path, default=ROOT / "knowledge_context/.env")
    parser.add_argument("--llm-env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--domain-source", choices=["neo4j", "json"], default="neo4j")
    parser.add_argument("--domain-graph-json", type=Path, default=ROOT / "knowledge_context/domain_knowledge_graph.json")
    parser.add_argument("--blueprint-dir", type=Path, default=ROOT / "optimization_runs/cache")
    parser.add_argument("--embedding-model", default="all-MiniLM-L6-v2")
    parser.add_argument("--settings-file", type=Path)
    parser.add_argument("--test-results", type=Path, help="JSON list of recorded offline test outcome dictionaries")
    args = parser.parse_args(argv)
    if args.repeats < 1 or args.timeout < 1 or args.max_tokens < 1:
        parser.error("repeats, timeout, and max-tokens must be positive")
    if args.also_rerun_existing and args.mode != "retrieval":
        parser.error("--also-rerun-existing is only supported with --mode retrieval")
    return args


def main(argv=None) -> int:
    manifest = run_experiment(parse_args(argv))
    print(f"Manifest: {Path(manifest['output_dir']) / 'manifest.json'}")
    print(f"Report: {manifest['reports']['markdown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
