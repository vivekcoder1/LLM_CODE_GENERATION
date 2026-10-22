"""Construct a domain graph from curated profiles and labeled reference sources.

Default: validate sources, write an inspection export, and synchronize Neo4j.
Use --export-only to validate/export without connecting. See KNOWLEDGE_GRAPH.md.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import struct
import sys
import time
import traceback
from typing import Any
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent
LOGGER = logging.getLogger("domain_knowledge_graph")
_LOG_SECRETS: set[str] = set()
LABELS = {
    "Domain", "ReferenceSimulation", "FieldSpec", "UpdateStep", "ValueSpec",
    "ParameterSpec", "SourceDefinition", "OutputSpec", "SaveOperation",
    "Artifact", "Guidance", "CodeComponent", "ApiCandidate",
}
RELATIONS = {
    "IN_DOMAIN", "HAS_FIELD", "HAS_STEP", "NEXT_STEP", "READS", "WRITES",
    "USES_API", "USES_API_CANDIDATE", "HAS_PARAMETER", "USES_PARAMETER",
    "HAS_HELPER", "CALLS_HELPER", "USES_HELPER", "PRODUCES", "HAS_SAVE",
    "HAS_ARTIFACT_OBSERVATION", "GUIDED_BY", "HAS_VALUE",
}


def redact_neo4j_message(message: str, password: str | None = None) -> str:
    """Keep diagnostics useful without displaying passwords or URI credentials."""
    for secret in ({password, os.getenv("NEO4J_PASSWORD")} | _LOG_SECRETS) - {None, ""}:
        message = message.replace(secret, "[REDACTED]")
    return re.sub(r"((?:neo4j|bolt)(?:\+[a-z]+)?://)[^\s/@]+@", r"\1[REDACTED]@", message, flags=re.IGNORECASE)


def safe_neo4j_uri(uri: str) -> str:
    """Show the server address without user information or query parameters."""
    return redact_neo4j_message(uri.partition("?")[0])


class SecretFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_neo4j_message(record.getMessage())
        record.args = ()
        return True


def configure_logging(debug: bool = False, log_file: Path | None = None) -> None:
    for handler in LOGGER.handlers:
        handler.close()
    LOGGER.handlers.clear()
    LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)
    LOGGER.propagate = False
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    for handler in handlers:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"))
        handler.addFilter(SecretFilter())
        LOGGER.addHandler(handler)


def digest(value: str | bytes) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def encoded(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def inside(root: Path, relative: str) -> Path:
    """Reject manifest paths outside the project, including symlink escapes."""
    if Path(relative).is_absolute():
        raise ValueError(f"Expected a repository-relative path: {relative}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes project root: {relative}")
    return path


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = call_name(node.value)
        return f"{parent}.{node.attr}" if parent else ""
    return ""


def targets(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Assign):
        return [target.id for target in node.targets if isinstance(target, ast.Name)]
    return []


class Source:
    def __init__(self, root: Path, relative: str):
        self.path = relative
        self.text = inside(root, relative).read_text(encoding="utf-8-sig")
        self.sha256 = digest(self.text)
        self.tree = ast.parse(self.text, filename=relative)

    def evidence(self, node: ast.AST, kind: str = "source_fact") -> dict[str, Any]:
        start = getattr(node, "lineno", 1)
        return {"source_path": self.path, "source_lines": [start, getattr(node, "end_lineno", None) or start],
                "source_sha256": self.sha256, "evidence_kind": kind, "review_status": "draft"}

    def segment(self, node: ast.AST) -> str:
        return ast.get_source_segment(self.text, node) or ast.unparse(node)

    def assignment(self, variable: str) -> ast.Assign:
        matches = [node for node in self.tree.body if variable in targets(node)]
        if len(matches) != 1:
            raise ValueError(f"{self.path}: expected one module assignment to {variable}, found {len(matches)}")
        return matches[0]

    def function(self, name: str) -> ast.FunctionDef:
        matches = [node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
        if len(matches) != 1:
            raise ValueError(f"{self.path}: expected one function {name}")
        return matches[0]

    def scope(self, name: str) -> list[ast.stmt]:
        if name == "module":
            return self.tree.body
        if name.startswith("function:"):
            body = self.function(name.partition(":")[2]).body
        elif name == "loop":
            loops = [node for node in self.tree.body if isinstance(node, ast.For)]
            if len(loops) != 1 or loops[0].orelse:
                raise ValueError(f"{self.path}: loop scope requires one for loop without an else")
            body = loops[0].body
        else:
            raise ValueError(f"Unsupported scope: {name}")
        if any(isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match)) for node in body):
            raise ValueError(f"{self.path}: only straight-line update scopes are supported")
        return body

    def locate(self, code: str, scope: str) -> ast.stmt:
        parsed = ast.parse(code).body
        if len(parsed) != 1:
            raise ValueError("A code selector must contain exactly one statement")
        fingerprint = ast.dump(parsed[0], include_attributes=False)
        matches = [node for node in self.scope(scope) if ast.dump(node, include_attributes=False) == fingerprint]
        if len(matches) != 1:
            raise ValueError(f"{self.path}: selector in {scope} matched {len(matches)} statements: {code}")
        return matches[0]


class StaticSymbolResolver:
    """Find local definitions and explicit re-exports without importing a library.

    Star imports, external dependencies, and instance methods remain unresolved.
    Definition verification is not a guarantee about runtime wildcard bindings.
    """

    def __init__(self, code_root: Path):
        self.root = code_root.resolve()
        self.cache: dict[str, dict[str, Any] | None] = {}

    def resolve(self, symbol: str, seen: frozenset[str] = frozenset()) -> dict[str, Any] | None:
        if symbol in self.cache:
            return self.cache[symbol]
        if symbol in seen:
            return None
        seen = seen | {symbol}
        parts = symbol.split(".")
        if not all(part.isidentifier() for part in parts):
            return None
        for split in range(len(parts) - 1, 0, -1):
            module_parts, remaining = parts[:split], parts[split:]
            module = self.root.joinpath(*module_parts)
            for path in [module.with_suffix(".py"), module / "__init__.py"]:
                if not path.is_file() or not path.resolve().is_relative_to(self.root):
                    continue
                text = path.read_text(encoding="utf-8-sig")
                tree = ast.parse(text, filename=str(path))
                definitions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                               and len(remaining) == 1 and node.name == remaining[0]]
                if len(definitions) == 1:
                    node = definitions[0]
                    result = {"qualified_name": symbol, "definition_path": path.relative_to(self.root).as_posix(),
                              "definition_lines": [node.lineno, node.end_lineno], "definition_sha256": digest(text),
                              "component_type": "Class" if isinstance(node, ast.ClassDef) else "Function"}
                    self.cache[symbol] = result
                    return result
                for node in tree.body:
                    if not isinstance(node, ast.ImportFrom):
                        continue
                    package = module_parts if path.name == "__init__.py" else module_parts[:-1]
                    if node.level > len(package):
                        continue
                    base = package[:len(package) - node.level + 1] if node.level else []
                    base += node.module.split(".") if node.module else []
                    for alias in node.names:
                        if alias.name != "*" and (alias.asname or alias.name) == remaining[0]:
                            result = self.resolve(".".join(base + [alias.name] + remaining[1:]), seen)
                            if result:
                                self.cache[symbol] = result
                                return result
        self.cache[symbol] = None
        return None


def npy_header(path: Path) -> dict[str, Any]:
    """Read only an array header; never deserialize data or pickle."""
    with path.open("rb") as stream:
        if stream.read(6) != b"\x93NUMPY":
            raise ValueError(f"Not a NumPy array: {path}")
        version = stream.read(2)
        if len(version) != 2 or version[0] not in (1, 2, 3):
            raise ValueError(f"Unsupported NPY version: {path}")
        width = 2 if version[0] == 1 else 4
        raw = stream.read(width)
        if len(raw) != width:
            raise ValueError(f"Truncated NPY header: {path}")
        length = struct.unpack("<H" if width == 2 else "<I", raw)[0]
        if length > 1_000_000:
            raise ValueError(f"NPY header exceeds size limit: {path}")
        raw = stream.read(length)
        if len(raw) != length:
            raise ValueError(f"Truncated NPY header: {path}")
        header = ast.literal_eval(raw.decode("utf-8" if version[0] == 3 else "latin1").strip())
        if not isinstance(header, dict) or not isinstance(header.get("shape"), tuple):
            raise ValueError(f"Invalid NPY header: {path}")
        return {"shape": list(header["shape"]), "dtype": str(header["descr"]),
                "fortran_order": bool(header["fortran_order"]), "header_sha256": digest(raw)}


class KnowledgeGraphBuilder:
    def __init__(self, root: Path = DEFAULT_ROOT, spec_path: Path = HERE / "domain_graph_spec.json", code_root: Path | None = None):
        self.root = Path(root).resolve()
        self.spec_path = Path(spec_path).resolve()
        self.spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        if self.spec.get("schema_version") != 1:
            raise ValueError("Only specification schema_version 1 is supported")
        self.dataset = self.spec["dataset"]
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", self.dataset):
            raise ValueError("dataset must contain only letters, digits, underscores, and hyphens")
        self.resolver = StaticSymbolResolver(Path(code_root) if code_root else self.root / "phiflow")
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[str, dict[str, Any]] = {}
        self.report: list[dict[str, Any]] = []

    def node(self, key: str, label: str, evidence: dict[str, Any], **properties: Any) -> str:
        if label not in LABELS:
            raise ValueError(f"Unknown node label: {label}")
        node_id = f"dkg:{self.dataset}:{key}"
        existing = self.nodes.get(node_id)
        if existing and existing["label"] != label:
            raise ValueError(f"Node identity collision: {node_id}")
        self.nodes[node_id] = {"id": node_id, "label": label,
                               "properties": {"dataset": self.dataset, **evidence, **properties}}
        return node_id

    def edge(self, source: str, relation: str, target: str, evidence: dict[str, Any], **properties: Any) -> None:
        if relation not in RELATIONS or source not in self.nodes or target not in self.nodes:
            raise ValueError(f"Invalid relationship: {source} --{relation}--> {target}")
        values = {"dataset": self.dataset, **evidence, **properties}
        edge_id = f"dkg:{self.dataset}:edge:{digest(encoded([source, relation, target, values]))}"
        self.edges[edge_id] = {"id": edge_id, "source": source, "type": relation, "target": target, "properties": values}

    def apis(self, owner: str, statement: ast.AST, source: Source, scope_key: str, helpers: dict[str, str]) -> None:
        for call in [node for node in ast.walk(statement) if isinstance(node, ast.Call)]:
            name = call_name(call.func)
            if not name:
                continue
            evidence = source.evidence(call)
            if name in helpers:
                self.edge(owner, "CALLS_HELPER", helpers[name], evidence)
                continue
            symbol = self.spec["api_aliases"].get(name)
            resolved = self.resolver.resolve(symbol) if symbol else None
            if resolved:
                key = "code:" + resolved["qualified_name"]
                existing = self.nodes.get(f"dkg:{self.dataset}:{key}", {}).get("properties", {})
                aliases = sorted(set(existing.get("configured_aliases", [])) | {symbol})
                # Definition paths use the project root where possible, else an explicit code-root namespace.
                definition = self.resolver.root / resolved["definition_path"]
                relative = definition.relative_to(self.root).as_posix() if definition.is_relative_to(self.root) else "code-root:" + resolved["definition_path"]
                api = self.node(key, "CodeComponent", {
                    "source_path": relative, "source_lines": resolved["definition_lines"],
                    "source_sha256": resolved["definition_sha256"], "evidence_kind": "source_fact", "review_status": "draft",
                }, **resolved, configured_aliases=aliases, verification="local_static_definition")
                self.edge(owner, "USES_API", api, evidence, observed_call=name, configured_symbol=symbol,
                          binding_status="configured_alias_to_static_definition")
            else:
                candidate = self.node(f"{scope_key}:api:{name}", "ApiCandidate", evidence, observed_call=name,
                                      configured_symbol=symbol or "", resolution_status="unresolved",
                                      reason="External API, instance method, or alias without a local definition")
                self.edge(owner, "USES_API_CANDIDATE", candidate, evidence)

    def notes(self, reference: str, relative: str) -> None:
        path = inside(self.root, relative)
        if not path.is_file():
            self.report.append({"source": relative, "status": "missing_note"})
            return
        text = path.read_text(encoding="utf-8-sig")
        lines = text.splitlines()
        starts = [index for index, line in enumerate(lines) if line.startswith("## ")]
        wanted = {"Context to give an LLM", "Retrieval hints", "Differences and unresolved details", "Human refinement"}
        for offset, start in enumerate(starts):
            end = starts[offset + 1] if offset + 1 < len(starts) else len(lines)
            title = lines[start][3:]
            if title not in wanted:
                continue
            evidence = {"source_path": relative, "source_lines": [start + 1, end], "source_sha256": digest(text),
                        "evidence_kind": "unresolved" if title == "Differences and unresolved details" else "proposed_hint", "review_status": "draft"}
            guidance = self.node(f"guidance:{relative}:{title}", "Guidance", evidence, name=title,
                                 text="\n".join(lines[start + 1:end]).strip(),
                                 condition="When planning or reproducing this reference", author="curated_domain_note")
            self.edge(reference, "GUIDED_BY", guidance, evidence)

    def dependencies(self, owner: str, statement: ast.AST, source: Source,
                     parameters: dict[str, str], helpers: dict[str, str]) -> None:
        names = {node.id for node in ast.walk(statement) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
        for name in sorted(names):
            if name in parameters:
                self.edge(owner, "USES_PARAMETER", parameters[name], source.evidence(statement, "interpretation"), variable=name)
            if name in helpers:
                self.edge(owner, "USES_HELPER", helpers[name], source.evidence(statement, "interpretation"), variable=name)

    def build_reference(self, profile: dict[str, Any]) -> None:
        domain = profile["domain"]
        source = Source(self.root, profile["source"])
        key = f"reference:{domain}:ground_truth"
        whole = {"source_path": source.path, "source_lines": [1, max(1, len(source.text.splitlines()))],
                 "source_sha256": source.sha256, "evidence_kind": "source_fact", "review_status": "draft"}
        domain_id = self.node(f"domain:{domain}", "Domain", {**whole, "evidence_kind": "interpretation"}, name=domain)
        imports = [source.segment(node) for node in source.tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        ref = self.node(key, "ReferenceSimulation", whole, name=f"{domain} ground truth", domain=domain,
                        imports=imports, source_text=source.text, curation_file=self.spec_path.name,
                        curation_sha256=digest(self.spec_path.read_bytes()))
        self.edge(ref, "IN_DOMAIN", domain_id, {**whole, "evidence_kind": "interpretation"})
        alias_map: dict[str, str] = {}
        fields: dict[str, str] = {}
        for field in profile["fields"]:
            statement = source.assignment(field["variable"])
            evidence = source.evidence(statement)
            if field["id"] in fields:
                raise ValueError(f"Duplicate field id in {domain}: {field['id']}")
            field_id = self.node(f"{key}:field:{field['id']}", "FieldSpec", evidence, name=field["id"],
                                 variable=field["variable"], aliases=field["aliases"], role=field["role"],
                                 representation=field["representation"], semantic_metadata_evidence="curated_profile",
                                 expression=source.segment(statement))
            fields[field["id"]] = field_id
            self.edge(ref, "HAS_FIELD", field_id, evidence)
            for alias in field["aliases"]:
                if alias in alias_map:
                    raise ValueError(f"Duplicate field alias in {domain}: {alias}")
                alias_map[alias] = field_id
        helpers: dict[str, str] = {}
        for name in profile.get("helpers", []):
            statement = source.function(name)
            evidence = source.evidence(statement)
            helpers[name] = self.node(f"{key}:helper:{name}", "SourceDefinition", evidence, name=name, expression=source.segment(statement))
            self.edge(ref, "HAS_HELPER", helpers[name], evidence)
        parameters: dict[str, str] = {}
        for name in profile.get("bindings", []):
            statement = source.assignment(name)
            evidence = source.evidence(statement)
            properties = {"name": name, "expression": source.segment(statement)}
            try:
                properties["literal_json"] = encoded(ast.literal_eval(statement.value))
            except (ValueError, TypeError):
                pass
            parameters[name] = self.node(f"{key}:parameter:{name}", "ParameterSpec", evidence, **properties)
            self.edge(ref, "HAS_PARAMETER", parameters[name], evidence)
            self.apis(parameters[name], statement, source, key, helpers)
        scope = profile["update_scope"]
        body = source.scope(scope)
        if scope.startswith("function:"):
            function = source.function(scope.partition(":")[2])
            defaults = dict(zip([arg.arg for arg in function.args.args][-len(function.args.defaults):], function.args.defaults))
            for arg in function.args.args:
                if arg.arg in alias_map:
                    continue
                default = defaults.get(arg.arg)
                evidence = source.evidence(default if default is not None else arg)
                parameters[arg.arg] = self.node(f"{key}:parameter:{arg.arg}", "ParameterSpec", evidence, name=arg.arg,
                                                expression=source.segment(default) if default is not None else "required_argument",
                                                parameter_kind="function_argument")
                self.edge(ref, "HAS_PARAMETER", parameters[arg.arg], evidence)
            scope_text = source.segment(function)
        else:
            scope_text = source.segment(next(node for node in source.tree.body if isinstance(node, ast.For)))
        self.nodes[ref]["properties"].update(update_scope_source=scope_text, update_scope=scope)
        for field in profile["fields"]:
            statement = source.assignment(field["variable"])
            self.apis(fields[field["id"]], statement, source, key, helpers)
            self.dependencies(fields[field["id"]], statement, source, parameters, helpers)
        for name, helper in helpers.items():
            self.apis(helper, source.function(name), source, key, helpers)
            self.dependencies(helper, source.function(name), source, parameters, helpers)
        for name in profile.get("bindings", []):
            self.dependencies(parameters[name], source.assignment(name), source, parameters, helpers)
        versions: dict[str, int] = defaultdict(int)
        previous, previous_line = None, 0
        step_ids: set[str] = set()
        selected: set[int] = set()
        for index, spec in enumerate(profile["steps"]):
            if spec["id"] in step_ids:
                raise ValueError(f"Duplicate step id in {domain}: {spec['id']}")
            step_ids.add(spec["id"])
            statement = source.locate(spec["code"], scope)
            if statement.lineno <= previous_line:
                raise ValueError(f"Configured step order differs from source in {domain}")
            previous_line = statement.lineno
            selected.add(statement.lineno)
            if not isinstance(statement, (ast.Assign, ast.Return)):
                raise ValueError("Update steps support Assign and Return only")
            evidence = source.evidence(statement)
            step = self.node(f"{key}:step:{spec['id']}", "UpdateStep", evidence, name=spec["name"], order=index,
                             expression=source.segment(statement), scope=scope, semantic_metadata_evidence="curated_profile")
            self.edge(ref, "HAS_STEP", step, evidence, order=index)
            if previous:
                self.edge(previous, "NEXT_STEP", step, evidence)
            previous = step
            read_names = sorted({node.id for node in ast.walk(statement.value) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)})
            for name in read_names:
                if name in alias_map:
                    target = alias_map[name]
                    self.edge(step, "READS", target, source.evidence(statement, "interpretation"), variable=name,
                              state_version=versions[target], analysis="AST name load within one update")
                elif name in parameters:
                    self.edge(step, "USES_PARAMETER", parameters[name], evidence, variable=name)
            if isinstance(statement, ast.Return):
                if spec.get("return_field") not in fields:
                    raise ValueError("Return steps must name a configured return_field")
                writes = [(spec["return_field"], fields[spec["return_field"]])]
            else:
                if not targets(statement) or any(not isinstance(target, ast.Name) for target in statement.targets):
                    raise ValueError("Update assignments require simple variable targets")
                writes = []
                for name in targets(statement):
                    if name not in alias_map:
                        value = self.node(f"{key}:value:{name}", "ValueSpec", evidence, name=name, expression=source.segment(statement))
                        alias_map[name] = value
                        self.edge(ref, "HAS_VALUE", value, evidence)
                    writes.append((name, alias_map[name]))
            for name, target in writes:
                versions[target] += 1
                self.edge(step, "WRITES", target, source.evidence(statement, "interpretation"), variable=name,
                          state_version=versions[target], analysis="AST assignment or configured return target")
            self.apis(step, statement, source, key, helpers)
        for statement in body:
            if statement.lineno in selected:
                continue
            bare_return = isinstance(statement, ast.Return) and isinstance(statement.value, ast.Name) and statement.value.id in alias_map
            capture = isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call) and call_name(statement.value.func).endswith(".append")
            if not (bare_return or capture):
                raise ValueError(f"Unconfigured statement in {domain} update at line {statement.lineno}")
        output_ids: set[str] = set()
        for output in profile["outputs"]:
            if output["id"] in output_ids:
                raise ValueError(f"Duplicate output id in {domain}: {output['id']}")
            output_ids.add(output["id"])
            statement = source.locate(output["code"], "module")
            if output["variable"] not in targets(statement):
                raise ValueError(f"Output selector does not assign {output['variable']}")
            evidence = source.evidence(statement)
            saves = [node for node in source.tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                     and call_name(node.value.func) == "np.save" and len(node.value.args) >= 2
                     and output["variable"] in {name.id for name in ast.walk(node.value.args[1]) if isinstance(name, ast.Name)}]
            output_id = self.node(f"{key}:output:{output['id']}", "OutputSpec", evidence, name=output["id"],
                                  variable=output["variable"], expression=source.segment(statement), axis_order=output["axis_order"],
                                  initial_frame=output["initial_frame"], output_conventions_evidence="curated_profile",
                                  save_status="explicit" if saves else "not_explicit")
            self.edge(ref, "PRODUCES", output_id, evidence)
            self.apis(output_id, statement, source, key, helpers)
            self.dependencies(output_id, statement, source, parameters, helpers)
            for save in saves:
                filename = ast.literal_eval(save.value.args[0])
                if not isinstance(filename, str):
                    raise ValueError("Save filenames must be literal strings")
                save_evidence = source.evidence(save)
                save_id = self.node(f"{key}:save:{filename}", "SaveOperation", save_evidence, filename=filename, expression=source.segment(save))
                self.edge(output_id, "HAS_SAVE", save_id, save_evidence)
                self.apis(save_id, save, source, key, helpers)
            for relative in output.get("artifacts", []):
                path = inside(self.root, relative)
                if not path.is_file():
                    self.report.append({"source": relative, "status": "missing_artifact"})
                    continue
                observation = {"source_path": relative, "source_lines": [], "evidence_kind": "artifact_observation", "review_status": "draft"}
                artifact = self.node(f"artifact:{relative}", "Artifact", observation, **npy_header(path), provenance_status="production_history_unverified")
                self.edge(output_id, "HAS_ARTIFACT_OBSERVATION", artifact, {**observation, "evidence_kind": "interpretation"}, association_basis="curated_profile")
        self.notes(ref, profile["note"])
        self.report.append({"domain": domain, "source": source.path, "status": "built"})

    def build(self) -> dict[str, Any]:
        self.nodes.clear()
        self.edges.clear()
        self.report.clear()
        self.resolver.cache.clear()
        profiles = self.spec["references"]
        domains = [profile["domain"] for profile in profiles]
        sources = [profile["source"] for profile in profiles]
        if len(set(domains)) != len(domains) or len(set(sources)) != len(sources):
            raise ValueError("Profiles require unique domains and sources")
        for profile in profiles:
            if not re.fullmatch(r"[a-zA-Z0-9_-]+", profile["domain"]):
                raise ValueError(f"Invalid domain identifier: {profile['domain']}")
            path = inside(self.root, profile["source"])
            if not path.name.endswith("_ground_truth.py"):
                raise ValueError(f"Source is not labeled ground truth: {profile['source']}")
            if not path.is_file() or not path.read_text(encoding="utf-8-sig").strip():
                raise ValueError(f"Configured reference source is missing or empty: {profile['source']}")
            self.build_reference(profile)
        for path in sorted(self.root.glob("test_*/*ground_truth.py")):
            relative = path.relative_to(self.root).as_posix()
            if relative not in sources:
                status = "unconfigured_source" if path.read_text(encoding="utf-8-sig").strip() else "empty_source"
                self.report.append({"source": relative, "status": status})
        for task in sorted((self.root / "test").glob("*.md")):
            if task.stem not in domains and not list((self.root / f"test_{task.stem}").glob("*ground_truth.py")):
                self.report.append({"domain": task.stem, "status": "missing_ground_truth"})
        nodes = sorted(self.nodes.values(), key=lambda row: row["id"])
        edges = sorted(self.edges.values(), key=lambda row: row["id"])
        graph = {"schema_version": 1, "dataset": self.dataset, "nodes": nodes, "edges": edges, "report": sorted(self.report, key=encoded)}
        graph["summary"] = {"nodes": len(nodes), "edges": len(edges),
                            "node_labels": dict(sorted(Counter(row["label"] for row in nodes).items())),
                            "relationship_types": dict(sorted(Counter(row["type"] for row in edges).items()))}
        graph["graph_sha256"] = digest(encoded(graph))
        return graph


def neo4j_properties(row: dict[str, Any]) -> dict[str, Any]:
    result = {"id": row["id"]}
    for key, value in row["properties"].items():
        if value is None:
            continue
        if isinstance(value, dict) or isinstance(value, list) and any(isinstance(item, (list, dict)) for item in value):
            result[key + "_json"] = encoded(value)
        else:
            result[key] = value
    return result


def neo4j_dataset_counts(session: Any, dataset: str) -> dict[str, int]:
    counts = {}
    queries = {
        "nodes": "MATCH (n:DomainKG {dataset: $dataset}) RETURN count(n) AS count",
        "edges": "MATCH (a:DomainKG {dataset: $dataset})-[r]->(b:DomainKG {dataset: $dataset}) "
                 "WHERE r.dataset = $dataset RETURN count(r) AS count",
    }
    for name, query in queries.items():
        row = session.run(query, dataset=dataset).single(strict=True)
        counts[name] = int(row["count"])
    return counts


def write_neo4j(graph: dict[str, Any], uri: str, user: str, password: str, database: str | None = None) -> None:
    """Synchronize only DomainKG entities owned by the specified dataset."""
    if not graph["nodes"]:
        raise ValueError("Refusing to synchronize an empty graph")
    dataset = graph["dataset"]
    if not isinstance(dataset, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+", dataset):
        raise ValueError("Invalid graph dataset")
    node_ids = {row["id"] for row in graph["nodes"]}
    for row in graph["nodes"] + graph["edges"]:
        if row["properties"].get("dataset") != dataset or not row["id"].startswith(f"dkg:{dataset}:"):
            raise ValueError("Graph contains an entity outside its dataset")
    for row in graph["edges"]:
        if row["source"] not in node_ids or row["target"] not in node_ids:
            raise ValueError("Graph contains a dangling relationship")
    try:
        from neo4j import GraphDatabase
    except ImportError as error:
        raise ValueError("Neo4j import requires the neo4j Python package") from error
    grouped_nodes, grouped_edges = defaultdict(list), defaultdict(list)
    for row in graph["nodes"]:
        if row["label"] not in LABELS:
            raise ValueError("Unexpected node label in graph")
        grouped_nodes[row["label"]].append({"id": row["id"], "properties": neo4j_properties(row)})
    for row in graph["edges"]:
        if row["type"] not in RELATIONS:
            raise ValueError("Unexpected relationship type in graph")
        grouped_edges[row["type"]].append({**row, "properties": neo4j_properties(row)})

    started = time.perf_counter()
    LOGGER.info("Neo4j target: uri=%s | user=%s | requested database=%s | dataset=%s",
                safe_neo4j_uri(uri), user, database or "<server default>", dataset)
    LOGGER.info("Prepared %d nodes in %d label batches and %d relationships in %d type batches",
                len(graph["nodes"]), len(grouped_nodes), len(graph["edges"]), len(grouped_edges))
    attempt = 0

    def transaction(tx: Any) -> dict[str, int]:
        nonlocal attempt
        attempt += 1
        LOGGER.info("BEGIN data transaction, attempt %d (a retry repeats uncommitted batch logs)", attempt)
        totals = dict.fromkeys(["nodes_created", "nodes_deleted", "relationships_created", "relationships_deleted", "properties_set"], 0)

        def run_batch(stage: str, query: str, **parameters: Any) -> None:
            if "rows" in parameters:
                LOGGER.info("%s: submitting %d rows", stage, len(parameters["rows"]))
            else:
                LOGGER.info("%s: executing cleanup with %d retained IDs", stage, len(parameters["ids"]))
            LOGGER.debug("Cypher [%s]: %s", stage, query)
            summary = tx.run(query, **parameters).consume()
            changes = {key: getattr(summary.counters, key) for key in totals}
            for key, value in changes.items():
                totals[key] += value
            LOGGER.info("%s: completed (uncommitted) | nodes created=%d, deleted=%d | relationships created=%d, deleted=%d | properties set=%d",
                        stage, changes["nodes_created"], changes["nodes_deleted"], changes["relationships_created"],
                        changes["relationships_deleted"], changes["properties_set"])

        for label, rows in sorted(grouped_nodes.items()):
            run_batch(f"Node batch {label}",
                      f"UNWIND $rows AS row MERGE (n:DomainKG {{id: row.id}}) SET n:{label} SET n = row.properties", rows=rows)
        for relation, rows in sorted(grouped_edges.items()):
            run_batch(f"Relationship batch {relation}",
                      f"UNWIND $rows AS row MATCH (a:DomainKG {{id: row.source}}), (b:DomainKG {{id: row.target}}) "
                      f"MERGE (a)-[r:{relation} {{id: row.id}}]->(b) SET r = row.properties", rows=rows)
        run_batch("Stale relationship cleanup",
                  "MATCH (a:DomainKG {dataset: $dataset})-[r]->(b:DomainKG {dataset: $dataset}) "
                  "WHERE r.dataset = $dataset AND NOT r.id IN $ids DELETE r",
                  dataset=dataset, ids=[row["id"] for row in graph["edges"]])
        run_batch("Stale node cleanup", "MATCH (n:DomainKG {dataset: $dataset}) WHERE NOT n.id IN $ids DETACH DELETE n",
                  dataset=dataset, ids=[row["id"] for row in graph["nodes"]])
        return totals

    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        LOGGER.info("Checking connectivity and authentication...")
        driver.verify_connectivity()
        LOGGER.info("Connectivity check passed; opening database session")
        with driver.session(database=database) as session:
            LOGGER.info("Ensuring DomainKG identity constraint exists...")
            schema = session.run("CREATE CONSTRAINT domainKGIdentity IF NOT EXISTS FOR (n:DomainKG) REQUIRE n.id IS UNIQUE").consume()
            actual_database = schema.database or database or "<server did not report name>"
            LOGGER.info("Server=%s | agent=%s | actual database=%s | constraints created=%d",
                        schema.server.address, schema.server.agent, actual_database, schema.counters.constraints_added)
            before = neo4j_dataset_counts(session, dataset)
            LOGGER.info("BEFORE: dataset=%s has %d nodes and %d relationships", dataset, before["nodes"], before["edges"])
            totals = session.execute_write(transaction)
            LOGGER.info("COMMIT confirmed: nodes created=%d, deleted=%d | relationships created=%d, deleted=%d | properties set=%d",
                        totals["nodes_created"], totals["nodes_deleted"], totals["relationships_created"],
                        totals["relationships_deleted"], totals["properties_set"])
            after = neo4j_dataset_counts(session, dataset)
            expected = {"nodes": len(graph["nodes"]), "edges": len(graph["edges"])}
            LOGGER.info("AFTER: actual database=%s | nodes=%d/%d expected | relationships=%d/%d expected",
                        actual_database, after["nodes"], expected["nodes"], after["edges"], expected["edges"])
            if after != expected:
                raise ValueError(f"Neo4j COMMITTED, but verification failed in database {actual_database}: expected {expected}, observed {after}")
            if before == after:
                LOGGER.info("Counts are unchanged: MERGE can update existing entities without increasing node/relationship counts")
            LOGGER.info("VERIFIED Neo4j synchronization in %.2fs. In Browser, select database %s and run:",
                        time.perf_counter() - started, actual_database)
            LOGGER.info("MATCH (n:DomainKG {dataset: '%s'}) RETURN n LIMIT 100;", dataset)


def load_neo4j_config(root: Path, env_file: Path | None = None, uri: str | None = None,
                     user: str | None = None, database: str | None = None) -> dict[str, Any]:
    """Read one complete credentials file, without environment/root fallbacks.

    dotenv_values does not mutate os.environ. Interpolation is disabled so an
    inherited NEO4J_* value cannot enter the selected file through ${...}.
    """
    selected = (Path(env_file) if env_file is not None else Path(root) / "knowledge_context" / ".env").resolve()
    LOGGER.info("Selected Neo4j credentials file: %s", selected)
    LOGGER.info("Configuration isolation: root .env and inherited NEO4J_* settings are ignored")
    if not selected.is_file():
        raise ValueError(f"Selected Neo4j .env file does not exist: {selected}. No fallback is allowed.")
    try:
        from dotenv import dotenv_values
    except ImportError as error:
        raise ValueError("Reading the selected credentials file requires python-dotenv; environment fallback is disabled") from error
    values = dotenv_values(selected, interpolate=False, encoding="utf-8-sig")
    if values.get("NEO4J_PASSWORD"):
        _LOG_SECRETS.add(values["NEO4J_PASSWORD"])
    required = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]
    missing = [name for name in required if not values.get(name) or not values[name].strip()]
    if missing:
        raise ValueError(f"Missing Neo4j settings in {selected}: " + ", ".join(missing) + ". This file must contain all three credentials; no other source is consulted.")
    if any(re.search(r"\$\{[^}]+\}", values[name]) for name in required):
        raise ValueError(f"Neo4j settings in {selected} must be literal values; ${{...}} interpolation is disabled")
    config = {"uri": (uri if uri is not None else values["NEO4J_URI"]).strip(),
              "user": (user if user is not None else values["NEO4J_USER"]).strip(),
              "password": values["NEO4J_PASSWORD"],
              "database": (database if database is not None else values.get("NEO4J_DATABASE") or "").strip() or None}
    try:
        address = urlsplit(config["uri"])
        valid = address.scheme in {"bolt", "bolt+s", "bolt+ssc", "neo4j", "neo4j+s", "neo4j+ssc"} and bool(address.hostname)
        _ = address.port  # Validate a supplied port even though the driver handles the connection.
        if not valid or address.username is not None or address.password is not None or address.fragment:
            raise ValueError
    except ValueError as error:
        raise ValueError("NEO4J_URI must be a valid bolt:// or neo4j:// URI (including TLS variants), without embedded credentials") from error
    if not config["user"]:
        raise ValueError("Neo4j username must not be empty")
    LOGGER.info("Connection settings loaded | URI source=%s | user source=%s | database source=%s | password source=%s (hidden)",
                "--uri" if uri is not None else selected, "--user" if user is not None else selected,
                "--database" if database is not None else selected if config["database"] else "server default", selected)
    LOGGER.info("Selected target: uri=%s | user=%s | requested database=%s", safe_neo4j_uri(config["uri"]),
                config["user"], config["database"] or "<server default>")
    return config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Project root; defaults to parent of this script's directory")
    parser.add_argument("--spec", type=Path, default=HERE / "domain_graph_spec.json")
    parser.add_argument("--code-root", type=Path, help="Directory containing local packages, default ROOT/phiflow")
    parser.add_argument("--output", type=Path, help="Default ROOT/knowledge_context/domain_knowledge_graph.json")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--export-only", action="store_true", help="Validate and export JSON without connecting to Neo4j")
    mode.add_argument("--check-config", action="store_true", help="Show the selected credentials file and target, without building or connecting")
    mode.add_argument("--neo4j", action="store_true", help=argparse.SUPPRESS)  # Backward-compatible; Neo4j is now the default.
    parser.add_argument("--uri", help="Explicit URI override after the selected credentials file is validated")
    parser.add_argument("--user", help="Explicit username override after the selected credentials file is validated")
    parser.add_argument("--database", help="Override the database in the selected credentials file")
    parser.add_argument("--env-file", type=Path, help="Read only this credentials file; default ROOT/knowledge_context/.env; no fallbacks")
    parser.add_argument("--debug", action="store_true", help="Show Cypher statements and redacted error tracebacks")
    parser.add_argument("--log-file", type=Path, help="Also save timestamped diagnostics to this file")
    args = parser.parse_args(argv)
    last_password = None
    try:
        configure_logging(args.debug, args.log_file)
        LOGGER.info("Starting %s", Path(__file__).resolve())
        LOGGER.info("Python=%s | working directory=%s | mode=%s", sys.executable, Path.cwd(),
                    "EXPORT ONLY (Neo4j will not be changed)" if args.export_only else
                    "CONFIGURATION CHECK (no Neo4j connection or writes)" if args.check_config else "NEO4J SYNCHRONIZATION")
        if args.log_file:
            LOGGER.info("Diagnostics file: %s", args.log_file.resolve())
        config = None
        if not args.export_only:
            config = load_neo4j_config(args.root, args.env_file, args.uri, args.user, args.database)
            last_password = config["password"]
        if args.check_config:
            LOGGER.info("Configuration check complete; no graph build, database connection, or writes were attempted")
            return 0
        LOGGER.info("Building graph | root=%s | specification=%s", args.root.resolve(), args.spec.resolve())
        builder = KnowledgeGraphBuilder(args.root, args.spec, args.code_root)
        graph = builder.build()
        if not graph["nodes"]:
            raise ValueError("No usable references; refusing an empty export or database synchronization")
        output = args.output or builder.root / "knowledge_context" / "domain_knowledge_graph.json"
        if output.suffix.lower() != ".json":
            raise ValueError("Output must have a .json extension")
        protected = [inside(builder.root, profile["source"]) for profile in builder.spec["references"]]
        protected += [inside(builder.root, profile["note"]) for profile in builder.spec["references"]]
        protected += [args.spec.resolve(), Path(__file__).resolve()]
        if output.resolve() in protected:
            raise ValueError("Output must not overwrite a source, note, specification, or this script")
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(output.name + ".tmp")
        temporary.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(output)
        LOGGER.info("Exported %d nodes and %d relationships to %s", graph["summary"]["nodes"], graph["summary"]["edges"], output)
        for item in graph["report"]:
            if item["status"] != "built":
                LOGGER.warning("%s: %s", item["status"], item.get("source", item.get("domain")))
        if not args.export_only:
            try:
                from neo4j.exceptions import DriverError, Neo4jError
            except ImportError as error:
                raise ValueError("Neo4j import requires the neo4j Python package") from error
            try:
                write_neo4j(graph, **config)
            except (DriverError, Neo4jError) as error:
                detail = redact_neo4j_message(str(error), last_password)
                code = getattr(error, "code", None) or "no server error code"
                raise ValueError(f"Neo4j synchronization failed: {type(error).__name__} [{code}]: {detail}. Local export remains at {output}") from error
            LOGGER.info("Synchronized Neo4j dataset %s", graph["dataset"])
        else:
            LOGGER.info("Export-only run complete; no Neo4j connection or writes were attempted")
        return 0
    except (ValueError, OSError, SyntaxError, KeyError, TypeError) as error:
        message = redact_neo4j_message(str(error), last_password)
        if LOGGER.handlers:
            LOGGER.error("Build failed: %s", message)
            if args.debug:
                LOGGER.debug("Failure traceback:\n%s", redact_neo4j_message(traceback.format_exc(), last_password))
        else:
            print(f"Build failed: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
