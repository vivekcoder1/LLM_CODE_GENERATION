"""Read domain recipes and prepare bounded, provenance-bearing LLM context.

This module has no environment loading, connection creation, or database writes.
Pass an inspection-export dictionary, explicitly call ``from_json(path)``, or
inject an existing Neo4j driver. Reference recipes are prior evidence; the
current task always supplies the requirements for the generated program.
"""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
import re
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_DATASET = "ground_truth_domains"
_PROVENANCE = (
    "source_path", "source_lines", "source_sha256", "evidence_kind",
    "review_status", "semantic_metadata_evidence", "output_conventions_evidence",
)
_RELATIONS = (
    "IN_DOMAIN", "HAS_FIELD", "HAS_STEP", "NEXT_STEP", "READS", "WRITES",
    "USES_API", "USES_API_CANDIDATE", "HAS_PARAMETER", "USES_PARAMETER",
    "HAS_HELPER", "CALLS_HELPER", "USES_HELPER", "PRODUCES", "HAS_SAVE",
    "HAS_ARTIFACT_OBSERVATION", "GUIDED_BY", "HAS_VALUE",
)
_LABELS = {
    "Domain", "ReferenceSimulation", "FieldSpec", "UpdateStep", "ValueSpec",
    "ParameterSpec", "SourceDefinition", "OutputSpec", "SaveOperation",
    "Artifact", "Guidance", "CodeComponent", "ApiCandidate",
}
_NODE_FIELDS = (
    "dataset", "name", "domain", *_PROVENANCE, "variable", "aliases", "role",
    "representation", "expression", "literal_json", "parameter_kind", "order",
    "scope", "axis_order", "initial_frame", "save_status", "filename", "shape",
    "dtype", "fortran_order", "header_sha256", "provenance_status", "text",
    "condition", "author", "qualified_name", "configured_aliases",
    "component_type", "verification", "definition_path", "definition_lines",
    "definition_sha256", "observed_call", "configured_symbol",
    "resolution_status", "reason",
)

# Names and relationship types are constants. All user input is a query parameter.
# Projection deliberately excludes source_text and update_scope_source, even on
# reads, so a full reference program is never fetched to create prompt context.
DOMAIN_READ_QUERY = """
MATCH (reference:DomainKG:ReferenceSimulation {dataset: $dataset, domain: $domain})
MATCH path=(reference)-[:%s*0..4]->(node:DomainKG)
WHERE all(n IN nodes(path) WHERE n:DomainKG AND n.dataset = $dataset)
  AND all(r IN relationships(path) WHERE r.dataset = $dataset)
WITH collect(DISTINCT node) AS domain_nodes, collect(DISTINCT path) AS paths
RETURN [n IN domain_nodes | {
    id: n.id, labels: labels(n), properties: n{%s}
}] AS nodes,
reduce(result = [], p IN paths | result + [r IN relationships(p) | {
    id: r.id, source: startNode(r).id, target: endNode(r).id,
    type: type(r), properties: properties(r)
}]) AS edges
""" % ("|".join(_RELATIONS), ", ".join("." + field for field in _NODE_FIELDS))


def _provenance(properties: dict[str, Any]) -> dict[str, Any]:
    return {key: copy.deepcopy(properties[key]) for key in _PROVENANCE if key in properties}


def _plain_guidance(text: str) -> str:
    """Keep curated prose; fenced source and artifact names are not defaults."""
    text = re.sub(r"```[^\n]*\n.*?```", "[reference code omitted]", text, flags=re.S)
    text = re.sub(r"[\w./\\-]*ground_truth[\w./\\-]*\.npy", "<reference artifact>", text)
    return text.strip()[:6000]


def _public_name(observed: str, aliases: list[str], qualified_name: str) -> str:
    if observed:
        return observed
    # Static definitions may live in private modules. The curated public alias is
    # more useful to the code graph's public API search than that internal path.
    for alias in sorted(aliases):
        if alias.startswith("phi.physics."):
            return alias.removeprefix("phi.physics.")
        if alias.startswith("phi.field."):
            name = alias.removeprefix("phi.field.")
            return name if name[:1].isupper() else "field." + name
        if alias.startswith("phi.geom."):
            return alias.removeprefix("phi.geom.")
        if alias.startswith("phiml.math."):
            return alias.removeprefix("phiml.math.")
    return qualified_name.rsplit(".", 1)[-1]


def _serialize_context(knowledge: dict[str, Any], max_chars: int) -> tuple[str, dict[str, Any]]:
    """Deduplicate evidence hashes and budget prose without cutting a recipe.

    Full structured knowledge is returned separately. This prompt view omits
    redundant graph identifiers and repeated AST analysis descriptions. Every
    source-bearing record retains its source span, evidence kind and review
    status; the source path/hash are held once in evidence_sources.
    """
    sources: dict[tuple[str, str], str] = {}
    evidence_sources: dict[str, dict[str, Any]] = {}

    def evidence(value: dict[str, Any]) -> dict[str, Any]:
        source_key = (value.get("source_path", ""), value.get("source_sha256", ""))
        source_id = sources.get(source_key)
        if source_id is None:
            source_id = "S" + str(len(sources) + 1)
            sources[source_key] = source_id
            evidence_sources[source_id] = {"path": source_key[0], "sha256": source_key[1]}
        return {"source": source_id,
                **{key: value[key] for key in ("source_lines", "evidence_kind", "review_status") if key in value}}

    def compact(value):
        if isinstance(value, list):
            return [compact(item) for item in value]
        if not isinstance(value, dict):
            return value
        return {("evidence" if key == "provenance" else "binding_evidence" if key == "binding_provenance" else key):
                evidence(item) if key in ("provenance", "binding_provenance") else compact(item)
                for key, item in value.items() if key not in ("id", "analysis", "reason")}

    payload = compact(knowledge)
    payload["evidence_sources"] = evidence_sources
    guidance = []
    for recipe in payload["references"]:
        guidance.extend((recipe, item) for item in recipe.pop("guidance", []))
        recipe["guidance"] = []
    prefix = "DOMAIN REFERENCE KNOWLEDGE (evidence, subject to the current task)\n"

    def render():
        return prefix + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    # Keep ordering, versioned dependencies, definitions and task authority before
    # optional prose. A single oversized recipe is returned intact with an
    # explicit over-budget flag instead of silently deleting core evidence.
    minimal_size = len(render())
    omitted = 0
    for recipe, item in guidance:
        room = max_chars - len(render()) - len(json.dumps({**item, "text": ""}, ensure_ascii=False)) - 12
        if room < 100:
            omitted += 1
            continue
        item["text"] = item["text"][:room]
        recipe["guidance"].append(item)
        if len(render()) > max_chars:
            recipe["guidance"].pop()
            omitted += 1
    text = render()
    return text, {"max_chars": max_chars, "characters": len(text), "omitted_guidance_sections": omitted,
                  "core_exceeds_budget": minimal_size > max_chars}


class DomainKnowledgeRetriever:
    """Read one dataset and explicitly selected domain, without owning a driver.

    ``graph`` and ``driver`` are mutually exclusive. ``graph=None`` with no
    driver yields an unavailable result and performs no filesystem or network
    access. Schema and adapter errors are raised to let the caller make any
    fallback visible. The injected driver remains open after retrieval.
    """

    def __init__(self, graph: dict[str, Any] | None = None, driver=None,
                 database: str | None = None, dataset: str = DEFAULT_DATASET,
                 max_context_chars: int = 16000):
        if graph is not None and driver is not None:
            raise ValueError("Pass a local graph or a Neo4j driver, not both")
        if not dataset or not isinstance(dataset, str):
            raise ValueError("An explicit nonempty dataset is required")
        if graph is not None and graph.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            raise ValueError("Unsupported domain graph schema_version")
        if max_context_chars < 1000:
            raise ValueError("max_context_chars must be at least 1000")
        self.graph = copy.deepcopy(graph)
        self.driver = driver
        self.database = database
        self.dataset = dataset
        self.max_context_chars = max_context_chars
        self.source_mode = "neo4j" if driver is not None else "local_json" if graph is not None else "none"

    @classmethod
    def from_json(cls, path: str | Path, *, dataset: str = DEFAULT_DATASET,
                  max_context_chars: int = 16000):
        """Load only the caller-selected file; never read a .env or source file."""
        graph = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        return cls(graph=graph, dataset=dataset, max_context_chars=max_context_chars)

    def _read(self, domain: str) -> dict[str, Any] | None:
        if self.driver is None:
            return self.graph
        with self.driver.session(database=self.database, default_access_mode="READ") as session:
            record = session.execute_read(
                lambda tx: tx.run(DOMAIN_READ_QUERY, dataset=self.dataset, domain=domain).single()
            )
        if not record:
            return {"schema_version": SCHEMA_VERSION, "dataset": self.dataset, "nodes": [], "edges": []}
        nodes = []
        for node in record["nodes"]:
            labels = sorted(set(node.get("labels", [])) & _LABELS)
            if len(labels) != 1:
                raise ValueError(f"Expected one domain schema label for {node.get('id')!r}")
            # Cypher map projections include absent properties as null, unlike
            # the inspection export. Normalize that difference before parsing
            # optional literal_json or serializing fields.
            properties = {key: value for key, value in node["properties"].items() if value is not None}
            nodes.append({"id": node["id"], "label": labels[0], "properties": properties})
        # Paths overlap. Deduplicate relationships without relying on result order.
        edges = {edge["id"]: edge for edge in record["edges"]}
        return {"schema_version": SCHEMA_VERSION, "dataset": self.dataset,
                "nodes": nodes, "edges": list(edges.values())}

    def _empty(self, domain: str, status: str) -> dict[str, Any]:
        return {"domain": domain, "dataset": self.dataset, "status": status, "context": "",
                "semantic_queries": [], "target_classes": [], "target_functions": [],
                "statistics": {"references": 0, "nodes": 0, "edges": 0,
                               "ordered_steps": 0, "verified_apis": 0, "api_candidates": 0},
                "source_mode": self.source_mode, "knowledge": {}, "api_hints": [],
                "context_budget": {"max_chars": self.max_context_chars, "characters": 0,
                                   "omitted_guidance_sections": 0, "core_exceeds_budget": False}}

    def get_domain_context(self, domain: str, task_description: str = "") -> dict[str, Any]:
        """Return bounded recipe context, public API hints, and retrieval counts.

        ``knowledge`` is the structured payload rendered in ``context``. A
        missing domain produces empty context, allowing code-only retrieval.
        State versions are scoped to one reference update, rather than claiming
        equivalence across timesteps or separate reference simulations.
        """
        domain = domain.strip()
        if not domain:
            return self._empty(domain, "missing_domain")
        graph = self._read(domain)
        if graph is None:
            return self._empty(domain, "unavailable")
        # Never mix datasets, including artifacts or shared API nodes.
        nodes = {node["id"]: node for node in graph.get("nodes", [])
                 if node.get("properties", {}).get("dataset") == self.dataset}
        references = sorted(
            (node for node in nodes.values() if node.get("label") == "ReferenceSimulation"
             and node["properties"].get("domain") == domain), key=lambda node: node["id"]
        )
        if not references:
            return self._empty(domain, "missing_domain")
        edges = [edge for edge in graph.get("edges", [])
                 if edge.get("properties", {}).get("dataset") == self.dataset
                 and edge.get("source") in nodes and edge.get("target") in nodes
                 and edge.get("type") in _RELATIONS]
        edges.sort(key=lambda edge: (edge["source"], edge["type"], edge["target"], edge.get("id", "")))
        outgoing: dict[str, list[dict[str, Any]]] = {}
        for edge in edges:
            outgoing.setdefault(edge["source"], []).append(edge)

        def connections(node_id: str, *relations: str):
            return [edge for edge in outgoing.get(node_id, []) if edge["type"] in relations]

        def linked(node_id: str, relation: str):
            return [nodes[edge["target"]] for edge in connections(node_id, relation)]

        def basic(node: dict[str, Any], *fields: str) -> dict[str, Any]:
            properties = node["properties"]
            return {"id": node["id"], **{key: copy.deepcopy(properties[key]) for key in fields if key in properties},
                    "provenance": _provenance(properties)}

        def dependency(edge: dict[str, Any]) -> dict[str, Any]:
            target = nodes[edge["target"]]
            properties = edge["properties"]
            return {"id": target["id"], "name": target["properties"].get("name", ""),
                    "kind": target["label"],
                    **{key: properties[key] for key in ("variable", "state_version", "analysis") if key in properties},
                    "provenance": _provenance(properties)}

        def dependencies(node_id: str, *relations: str):
            return [dependency(edge) for edge in connections(node_id, *relations)]

        all_selected: set[str] = set()
        all_edges: set[str] = set()
        verified: dict[tuple[str, str], dict[str, Any]] = {}
        candidates: dict[tuple[str, str], dict[str, Any]] = {}
        result_references = []
        semantic_queries: set[str] = set()
        reference_filenames: set[str] = set()
        for reference in references:
            ref_id = reference["id"]
            # Follow owned recipe edges, never incoming edges to shared API nodes
            # (which would pull unrelated domains into this context).
            selected = {ref_id}
            frontier = [ref_id]
            while frontier:
                owner = frontier.pop()
                for edge in outgoing.get(owner, []):
                    all_edges.add(edge.get("id", json.dumps([edge["source"], edge["type"], edge["target"]])))
                    if edge["target"] not in selected:
                        selected.add(edge["target"])
                        frontier.append(edge["target"])
            all_selected.update(selected)
            for owner in sorted(selected):
                for edge in connections(owner, "USES_API", "USES_API_CANDIDATE"):
                    target = nodes[edge["target"]]
                    properties = target["properties"]
                    if edge["type"] == "USES_API":
                        public = _public_name(edge["properties"].get("observed_call", ""),
                                              properties.get("configured_aliases", []),
                                              properties.get("qualified_name", ""))
                        item = basic(target, "qualified_name", "configured_aliases", "component_type", "verification", "definition_path")
                        item.update(public_name=public, observed_call=edge["properties"].get("observed_call", public),
                                    binding_provenance=_provenance(edge["properties"]),
                                    binding_status=edge["properties"].get("binding_status", ""))
                        verified[(target["id"], public)] = item
                    else:
                        item = basic(target, "observed_call", "configured_symbol", "resolution_status", "reason")
                        item["status"] = "candidate_only_not_verified"
                        candidates[(target["id"], properties.get("observed_call", ""))] = item
            recipe = basic(reference, "name", "domain")
            recipe["fields"] = []
            for node in linked(ref_id, "HAS_FIELD"):
                item = basic(node, "name", "variable", "aliases", "role", "representation", "expression")
                item["parameters"] = dependencies(node["id"], "USES_PARAMETER")
                item["helpers"] = dependencies(node["id"], "CALLS_HELPER", "USES_HELPER")
                recipe["fields"].append(item)
                semantic_queries.add(f"{domain.replace('_', ' ')} {node['properties'].get('role', '')} "
                                     f"{node['properties'].get('representation', '').replace('_', ' ')}".strip())
            recipe["parameters"] = []
            for node in linked(ref_id, "HAS_PARAMETER"):
                item = basic(node, "name", "expression", "parameter_kind")
                if "literal_json" in node["properties"]:
                    item["reference_value"] = json.loads(node["properties"]["literal_json"])
                item["parameters"] = dependencies(node["id"], "USES_PARAMETER")
                item["helpers"] = dependencies(node["id"], "CALLS_HELPER", "USES_HELPER")
                recipe["parameters"].append(item)
            recipe["helpers"] = []
            for node in linked(ref_id, "HAS_HELPER"):
                item = basic(node, "name")
                # Include the helper's return formula, not an entire body or an
                # executable copy of the reference function.
                try:
                    tree = ast.parse(node["properties"].get("expression", ""))
                    functions = [part for part in tree.body if isinstance(part, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    if functions:
                        function = functions[0]
                        item["arguments"] = [argument.arg for argument in function.args.args]
                        item["local_expressions"] = [
                            {"targets": [ast.unparse(target) for target in part.targets],
                             "value": ast.unparse(part.value)[:500]}
                            for part in function.body if isinstance(part, ast.Assign)
                        ]
                        item["return_expressions"] = [ast.unparse(part.value)[:500] for part in ast.walk(function)
                                                      if isinstance(part, ast.Return) and part.value is not None]
                except (SyntaxError, ValueError):
                    item["summary_status"] = "signature_unavailable"
                item["parameters"] = dependencies(node["id"], "USES_PARAMETER")
                item["helpers"] = dependencies(node["id"], "CALLS_HELPER", "USES_HELPER")
                recipe["helpers"].append(item)
            recipe["temporary_values"] = [basic(node, "name") for node in linked(ref_id, "HAS_VALUE")]
            steps = linked(ref_id, "HAS_STEP")
            steps.sort(key=lambda node: (node["properties"].get("order", 0), node["id"]))
            recipe["ordered_steps"] = []
            for node in steps:
                item = basic(node, "name", "order", "expression", "scope")
                item["reads"] = dependencies(node["id"], "READS")
                item["writes"] = dependencies(node["id"], "WRITES")
                item["parameters"] = dependencies(node["id"], "USES_PARAMETER")
                item["helpers"] = dependencies(node["id"], "CALLS_HELPER", "USES_HELPER")
                recipe["ordered_steps"].append(item)
                semantic_queries.add(f"{domain.replace('_', ' ')} {node['properties'].get('name', '')}".strip())
            recipe["outputs"] = []
            for node in linked(ref_id, "PRODUCES"):
                item = basic(node, "name", "variable", "axis_order", "initial_frame", "save_status")
                item["parameters"] = dependencies(node["id"], "USES_PARAMETER")
                item["artifact_observations"] = [basic(artifact, "shape", "dtype", "header_sha256", "provenance_status")
                                                  for artifact in linked(node["id"], "HAS_ARTIFACT_OBSERVATION")]
                recipe["outputs"].append(item)
                reference_filenames.update(save["properties"].get("filename", "")
                                           for save in linked(node["id"], "HAS_SAVE"))
            recipe["guidance"] = []
            for node in linked(ref_id, "GUIDED_BY"):
                if node["properties"].get("name") == "Human refinement":
                    continue  # Blank TODO prompts do not aid generation.
                item = basic(node, "name", "condition")
                item["text"] = _plain_guidance(node["properties"].get("text", ""))
                recipe["guidance"].append(item)
            result_references.append(recipe)

        requested_outputs = sorted(set(re.findall(r"[\w./\\-]+\.npy\b", task_description)))
        authority = {
            "priority": "Current task requirements are authoritative; reference recipes are prior evidence, not mandatory defaults.",
            "conflicts": "Make discrepancies explicit. Follow the current task on parameters, geometry, boundaries, API requirements, and filenames.",
            "output_names": "Use the output filenames requested by the current task; reference artifacts are provenance only.",
            "evidence": "Curated interpretations and unresolved API candidates are distinguished from statically verified definitions. Draft claims need review.",
            "state_versions": "READS/WRITES versions describe assignment order within one reference update; cached temporaries retain their producing version.",
        }
        differences = []
        if requested_outputs and reference_filenames and set(requested_outputs) != reference_filenames:
            differences.append("Requested output filenames differ from reference save filenames. Use task_requested_output_filenames.")
        verified_list = [verified[key] for key in sorted(verified)]
        candidate_list = [candidates[key] for key in sorted(candidates)]
        knowledge = {"schema_version": SCHEMA_VERSION, "dataset": self.dataset, "domain": domain,
                     "authority_policy": authority, "task_requested_output_filenames": requested_outputs,
                     "explicit_discrepancies": differences, "references": result_references,
                     "verified_api_hints": verified_list, "unresolved_api_candidates": candidate_list}
        # Public grid constructors have appeared as classes and factory functions
        # in code-graph versions. Search class names as well while retaining the
        # actual verified definition type in verified_api_hints.
        target_classes = sorted({item["public_name"] for item in verified_list
                                 if item.get("component_type") == "Class" or item["public_name"][:1].isupper()})
        target_functions = sorted({item["public_name"] for item in verified_list if item.get("component_type") == "Function"})
        context, context_budget = _serialize_context(knowledge, self.max_context_chars)
        return {"domain": domain, "dataset": self.dataset, "status": "available",
                "context": context, "context_budget": context_budget, "api_hints": verified_list,
                "semantic_queries": sorted(semantic_queries), "target_classes": target_classes,
                "target_functions": target_functions,
                "statistics": {"references": len(references), "nodes": len(all_selected), "edges": len(all_edges),
                               "ordered_steps": sum(len(recipe["ordered_steps"]) for recipe in result_references),
                               "verified_apis": len(verified_list), "api_candidates": len(candidate_list)},
                "source_mode": self.source_mode, "knowledge": knowledge}
