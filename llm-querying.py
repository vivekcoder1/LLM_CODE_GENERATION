import json
from pydantic import BaseModel, Field
from typing import List
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent

class SearchBlueprint(BaseModel):
    """Pydantic model forcing Claude to generate distinct search commands to hit our graph schema."""
    semantic_queries: List[str] = Field(
        ..., 
        description="Semantic search sentences to hit the vector index (e.g., 'creating computational grid in 2D')."
    )
    target_classes: List[str] = Field(
        default_factory=list, 
        description="Exact class names mentioned or expected (e.g., 'CenteredGrid', 'Domain')."
    )
    target_functions: List[str] = Field(
        default_factory=list, 
        description="Exact physical solvers or helper function names (e.g., 'diffuse', 'advect')."
    )


# ==========================================
# 2. END-TO-END RAG PIPELINE
# ==========================================
class E2ERagPipeline:
    def __init__(self, *, driver=None, client=None, embed_model=None,
                 domain_retriever=None, database=None, model=None,
                 code_env_file=None, llm_env_file=None, allow_llm=True,
                 domain_graph_path=ROOT / "knowledge_context" / "domain_knowledge_graph.json"):
        """Federate code/domain knowledge with independently selected credentials.

        Injected clients make offline tests independent of models and services.
        The database is only queried; this pipeline never builds or rewrites it.
        """
        self.embed_model = embed_model
        self.client = client
        self.allow_llm = bool(allow_llm)
        self.model = model or "claude-sonnet-4-6"
        self.last_generation_metadata = {}
        self._owns_client = False
        self._owns_driver = driver is None
        self.database = database
        if driver is None:
            from knowledge_context.pipeline_config import create_read_driver, load_connection_config
            config = load_connection_config(code_env_file or ROOT / ".env", role="code", root=ROOT)
            driver = create_read_driver(config)
            self.database = database or config.get("database")
        self.driver = driver
        if self.client is None and allow_llm:
            import anthropic
            from knowledge_context.pipeline_config import load_llm_config
            settings = load_llm_config(llm_env_file or ROOT / ".env", model=model)
            headers = {"anthropic-workspace-id": settings["workspace_id"]} if settings.get("workspace_id") else None
            self.client = anthropic.Anthropic(api_key=settings["api_key"], default_headers=headers,
                                              timeout=120, max_retries=0)
            self.model = settings["model"]
            self._owns_client = True
        if domain_retriever is None:
            from knowledge_context.domain_retrieval import DomainKnowledgeRetriever
            if domain_graph_path is not None and Path(domain_graph_path).is_file():
                domain_retriever = DomainKnowledgeRetriever.from_json(Path(domain_graph_path))
            else:
                domain_retriever = DomainKnowledgeRetriever()
        self.domain_retriever = domain_retriever

    def close(self):
        if self._owns_driver:
            self.driver.close()
        if self._owns_client:
            self.client.close()

    def _session(self):
        return self.driver.session(database=self.database, default_access_mode="READ")

    def _require_llm(self):
        if not self.allow_llm or self.client is None:
            raise RuntimeError("LLM calls are disabled. Supply a cached blueprint for retrieval or configure an explicit LLM client.")

    def retrieve_context(self, domain, task_description, variant="combined", blueprint=None, settings=None):
        from knowledge_context.combined_retrieval import retrieve_context
        return retrieve_context(self, domain, task_description, variant=variant, blueprint=blueprint, settings=settings)

    def generate_search_blueprint(self, task_description: str) -> dict:
        """Instruct Claude to analyze the physics task (including LaTeX math) and map it to framework targets."""
        print("Analyzing task markdown file to extract query parameters...")
        self._require_llm()
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0,
                system=(
                    "You are a repository-level code analyzer specializing in physics simulations and differentiable programming frameworks (like PhiFlow).\n"
                    "Your task is to analyze simulation task requirements (which may contain LaTeX math) and deconstruct them into expected codebase components.\n\n"
                    "TRANSLATION GUIDELINES:\n"
                    "- Domain & Grid (e.g., Ω = [0, Lx] x [0, Ly], Nx, Ny) -> target_classes: ['CenteredGrid', 'Grid', 'Box', 'Domain']\n"
                    "- Boundary Conditions (e.g., periodic u(0,y,t)=u(Lx,y,t)) -> target_classes: ['PERIODIC', 'extrapolation', 'Extrapolation']\n"
                    "- Governing PDEs (advection u·∇u, diffusion ν∇²u) -> target_functions: ['advect', 'diffuse', 'laplace', 'semi_lagrangian', 'mac_cormack', 'explicit', 'implicit']\n"
                    "- Semantic Queries: Write clean, plain-English sentences WITHOUT raw LaTeX markup (e.g., 'creating 2D centered grid with periodic boundary conditions', 'diffusive and advective step for velocity field').\n\n"
                    "Return ONLY valid JSON matching this schema:\n"
                    "{\n"
                    '  "semantic_queries": [],\n'
                    '  "target_classes": [],\n'
                    '  "target_functions": []\n'
                    "}"
                ),
                messages=[
                    {
                        "role": "user",
                        "content": f"Task description:\n{task_description}"
                    }
                ]
            )
            
            text = ""
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    text = block.text.strip()
                    break

            if not text:
                raise ValueError("No text block found in Claude's response.")

            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                text = text.rsplit("```", 1)[0]
            blueprint = SearchBlueprint.model_validate_json(text)

            return blueprint.model_dump()
        except Exception as e:
            from knowledge_context.pipeline_config import redact_message
            self.last_blueprint_error = redact_message(e)
            print(f"Failed to generate search blueprint: {self.last_blueprint_error}")
            return {"semantic_queries": [], "target_classes": [], "target_functions": []}

    def find_seed_nodes(
        self,
        blueprint: dict,
        fulltext_limit: int = 5,
        description_limit: int = 5,
        function_limit: int = 4,
        class_limit: int = 4,
    ) -> List[str]:
        """Step 2: Hybrid Search with wildcards and higher initial seed capacity."""
        seed_ids = set()
        
        with self._session() as session:
            # A. Full-Text Search on Expected Class Names
            for cls_name in blueprint.get("target_classes", []):
                term = cls_name.strip().rsplit(".", 1)[-1]
                if not term or len(term) < 2: continue
                res = session.run("""
                    CALL db.index.fulltext.queryNodes("classNames", $term) YIELD node, score
                    RETURN node.id AS id LIMIT $limit
                """, term=f"{term}* OR {term}", limit=fulltext_limit)
                for r in res:
                    if r["id"] is not None:
                        seed_ids.add(r["id"])

            # B. Full-Text Search on Expected Function Names
            for func_name in blueprint.get("target_functions", []):
                term = func_name.strip().rsplit(".", 1)[-1]
                if not term or len(term) < 2: continue
                res = session.run("""
                    CALL db.index.fulltext.queryNodes("functionNames", $term) YIELD node, score
                    RETURN node.id AS id LIMIT $limit
                """, term=f"{term}* OR {term}", limit=fulltext_limit)
                for r in res:
                    if r["id"] is not None:
                        seed_ids.add(r["id"])

            # C. Vector Similarity Search across all vector indexes
            for sem_query in blueprint.get("semantic_queries", []):
                if not sem_query.strip(): continue
                vector = self.get_embedding(sem_query)
                
                # Check Generated Descriptions Index
                res = session.run("""
                    CALL db.index.vector.queryNodes("descEmbed", $limit, $vector) YIELD node, score
                    MATCH (parent)-[:has_description]->(node)
                    RETURN parent.id AS id
                """, vector=vector, limit=description_limit)
                for r in res:
                    if r["id"] is not None:
                        seed_ids.add(r["id"])

                # Check Function Docstring Index
                res = session.run("""
                    CALL db.index.vector.queryNodes("funcDocEmbed", $limit, $vector) YIELD node, score
                    RETURN node.id AS id
                """, vector=vector, limit=function_limit)
                for r in res:
                    if r["id"] is not None:
                        seed_ids.add(r["id"])

                # Check Class Docstring Index
                res = session.run("""
                    CALL db.index.vector.queryNodes("classDocEmbed", $limit, $vector) YIELD node, score
                    RETURN node.id AS id
                """, vector=vector, limit=class_limit)
                for r in res:
                    if r["id"] is not None:
                        seed_ids.add(r["id"])

        return sorted(seed_ids)

    def get_embedding(self, text: str) -> List[float]:
        """Converts search strings into 384-dimensional vectors."""
        if self.embed_model is None:
            from sentence_transformers import SentenceTransformer
            self.embed_model = SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)
        return self.embed_model.encode(text).tolist()

    def traverse_subgraph(self, seed_ids: List[str]) -> List[dict]:
        """Step 3: Directed 2-Hop neighborhood expansion fetching public API metadata."""
        if not seed_ids:
            return []
            
        print(f"Performing 2-hop graph traversal starting from {len(seed_ids)} target seed nodes...")
        with self._session() as session:
            query = """
                MATCH (seed) WHERE seed.id IN $seed_ids AND NOT seed:DomainKG
                OPTIONAL MATCH path = (seed)-[rel:has_parameter|defines_function|defines_class|has_method|returns_type|has_return_type|has_type|of_type|has_description*1..2]-(neighbor)
                UNWIND CASE WHEN path IS NULL THEN [null] ELSE relationships(path) END AS r
                WITH DISTINCT CASE WHEN r IS NULL THEN seed ELSE startNode(r) END AS src,
                              r, CASE WHEN r IS NULL THEN seed ELSE endNode(r) END AS tgt
                
                OPTIONAL MATCH (src)-[:has_description]->(src_desc:GeneratedDescription)
                OPTIONAL MATCH (tgt)-[:has_description]->(tgt_desc:GeneratedDescription)
                
                RETURN coalesce(src.id, labels(src)[0] + ':' + coalesce(src.name, src.text, 'unknown')) AS src_id,
                       labels(src)[0] AS src_type,
                       src.name AS src_name,
                       coalesce(src.is_public_api, false) AS src_is_public,
                       coalesce(src.import_path, "") AS src_import_path,
                       coalesce(src.docstring, "") AS src_doc,
                       coalesce(src_desc.text, src.text, "") AS src_gen_desc,
                       type(r) AS relationship,
                       coalesce(tgt.id, labels(tgt)[0] + ':' + coalesce(tgt.name, tgt.text, 'unknown')) AS tgt_id,
                       labels(tgt)[0] AS tgt_type,
                       tgt.name AS tgt_name,
                       coalesce(tgt.is_public_api, false) AS tgt_is_public,
                       coalesce(tgt.import_path, "") AS tgt_import_path,
                       coalesce(tgt.docstring, "") AS tgt_doc,
                       coalesce(tgt_desc.text, tgt.text, "") AS tgt_gen_desc
            """
            result = session.run(query, seed_ids=seed_ids)
            return [row.data() for row in result]

    def filter_subgraph(
        self, 
        task_description: str, 
        raw_relations: List[dict], 
        top_k: int = 35, 
        min_score: float = 0.15,
        method_min_score: float = 0.30,
        max_methods_per_class: int = 8,
        public_boost: float = 0.20,
        private_penalty: float = 0.15
    ) -> List[dict]:
        """Filters and reranks triples while limiting noisy public class methods."""
        if not raw_relations:
            return []
            
        print(f"\nReranking {len(raw_relations)} raw graph triples with Public API prioritization...")
        query_vector = np.array(self.get_embedding(task_description), dtype=float).flatten()
        norm_q = np.linalg.norm(query_vector)

        candidate_texts = []
        clean_rows = []

        for row in raw_relations:
            target_name = row.get("tgt_name") or ""
            target_type = row.get("tgt_type") or ""
            
            if target_type == "GeneratedDescription":
                # A definition can have only a description edge. Rank the
                # definition itself so this metadata does not erase its API.
                if row.get("src_is_public") and row.get("src_type") in {"Class", "Function", "Method"}:
                    row = dict(row)
                    for key in ("id", "type", "name", "is_public", "import_path", "doc", "gen_desc"):
                        row["tgt_" + key] = row.get("src_" + key)
                    row["relationship"] = None
                    target_name = row.get("tgt_name") or ""
                    target_type = row.get("tgt_type") or ""
                else:
                    continue
                
            if target_name.startswith("__") and target_name.endswith("__"):
                continue

            gen_desc = row.get("tgt_gen_desc") or ""
            docstring = row.get("tgt_doc") or ""
            functional_summary = gen_desc if gen_desc else docstring

            text_representation = f"[{target_type}] {target_name}: {functional_summary}".strip()
            candidate_texts.append(text_representation)
            clean_rows.append(row)

        if not candidate_texts:
            return []

        if norm_q == 0:
            selected = [row for row in clean_rows
                        if row.get("src_is_public") or row.get("tgt_is_public")][:top_k]
            return self.complete_code_metadata(raw_relations, selected)

        candidate_vectors = self.embed_model.encode(candidate_texts)
        scored_rows = []

        for idx, row in enumerate(clean_rows):
            node_vector = np.array(candidate_vectors[idx], dtype=float).flatten()
            norm_n = np.linalg.norm(node_vector)

            base_score = float(np.dot(query_vector, node_vector) / (norm_q * norm_n)) if norm_n > 0 else 0.0
            
            # Apply public API boost vs private/internal penalty
            is_public = row.get("tgt_is_public", False)
            if is_public:
                final_score = base_score + public_boost
            else:
                final_score = base_score - private_penalty

            scored_rows.append((final_score, base_score, row))

        # Sort descending by adjusted score
        scored_rows.sort(key=lambda x: x[0], reverse=True)

        print("--- Top 10 Reranked Similarity Scores (Adjusted for Public API Priority) ---")
        for final_s, base_s, row in scored_rows[:10]:
            target = row.get('tgt_name') or row.get('src_name')
            pub_flag = "PUBLIC" if row.get('tgt_is_public') else "INTERNAL"
            print(f"  Score: {final_s:.4f} (Base: {base_s:.4f}) | [{pub_flag}] [{row.get('tgt_type')}] {target}")

        filtered_results = []
        method_counts = {}
        method_owners = {row.get("tgt_id"): row.get("src_id") for row in raw_relations
                         if row.get("relationship") == "has_method" and row.get("tgt_type") == "Method"}
        selected_methods = set()
        for final_score, base_score, row in scored_rows:
            if final_score < min_score:
                continue
            if not (row.get("src_is_public", False) or row.get("tgt_is_public", False)):
                continue

            if row.get("tgt_type") == "Method":
                if base_score < method_min_score:
                    continue
                method = row.get("tgt_id")
                owner = method_owners.get(method, "__unknown_owner__")
                if method not in selected_methods:
                    if method_counts.get(owner, 0) >= max_methods_per_class:
                        continue
                    method_counts[owner] = method_counts.get(owner, 0) + 1
                    selected_methods.add(method)

            filtered_results.append(row)
            if len(filtered_results) == top_k:
                break
        print(f"Retained {len(filtered_results)} high-confidence public-api triples (score >= {min_score})")

        return self.complete_code_metadata(raw_relations, filtered_results)

    def complete_code_metadata(self, raw_relations: List[dict], selected_rows: List[dict]) -> List[dict]:
        """Keep signatures/descriptions with selected public definitions.

        Structural metadata does not consume the semantic triple budget. This
        closure uses only the already retrieved rows and performs no queries.
        """
        selected_ids = {
            row.get(side + "_id") for row in selected_rows for side in ("src", "tgt")
            if row.get(side + "_is_public") and row.get(side + "_type") in {"Class", "Function", "Method"}
        }
        parameters = {
            row.get("tgt_id") for row in raw_relations
            if row.get("relationship") == "has_parameter" and row.get("src_id") in selected_ids
        }
        extra = [row for row in raw_relations if
                 (row.get("src_id") in selected_ids and row.get("relationship") in
                  {"has_parameter", "returns_type", "has_return_type", "has_description"}) or
                 (row.get("src_id") in parameters and row.get("relationship") in {"of_type", "has_type"})]
        result, seen = [], set()
        for row in [*selected_rows, *extra]:
            key = (row.get("src_id"), row.get("relationship"), row.get("tgt_id"))
            if key not in seen:
                seen.add(key)
                result.append(row)
        return result

    def serialize_subgraph(self, raw_relations: List[dict], max_nodes: int = 18) -> str:
        """Formats the retrievable public API context and omits private/internal symbols by default."""
        if not raw_relations:
            return "No matching codebase components found."

        nodes_dict = {}
        relationships = set()
        parameter_types = {}  # Map from parameter ID to type name
        return_types = {}  # Map from function/method ID to return type name

        # Type rows may occur after their owning callable/parameter rows.
        for row in raw_relations:
            if row.get("relationship") in ("has_type", "of_type") and row.get("src_type") == "Parameter":
                parameter_types[str(row.get("src_id"))] = row.get("tgt_name", "Unknown")

        # First pass: collect all nodes and build parameter-to-type and return-type mappings
        for row in raw_relations:
            src_id = row.get("src_id")
            tgt_id = row.get("tgt_id")
            rel = row.get("relationship")

            if src_id is None:
                src_id = "__missing_src__"
            if tgt_id is None:
                tgt_id = "__missing_tgt__"

            src_key = str(src_id)
            tgt_key = str(tgt_id)

            if src_key not in nodes_dict:
                nodes_dict[src_key] = {
                    "name": row.get("src_name") or "Unknown",
                    "type": row.get("src_type") or "Unknown",
                    "is_public": row.get("src_is_public", False),
                    "import_path": row.get("src_import_path", ""),
                    "docstring": row.get("src_doc") if row.get("src_type") != "GeneratedDescription" else "",
                    "description": row.get("src_gen_desc") or "",
                    "parameters": [],
                    "return_type": ""
                }

            if tgt_key not in nodes_dict:
                nodes_dict[tgt_key] = {
                    "name": row.get("tgt_name") or "Unknown",
                    "type": row.get("tgt_type") or "Unknown",
                    "is_public": row.get("tgt_is_public", False),
                    "import_path": row.get("tgt_import_path", ""),
                    "docstring": row.get("tgt_doc") if row.get("tgt_type") != "GeneratedDescription" else "",
                    "description": row.get("tgt_gen_desc") or "",
                    "parameters": [],
                    "return_type": ""
                }

            # Build parameter-to-type mapping: Parameter -[has_type]-> Type
            if rel in ("has_type", "of_type") and row.get("src_type") == "Parameter":
                parameter_types[src_key] = row.get("tgt_name", "Unknown")
            
            # Build return-type mapping: Function/Method -[has_return_type|returns_type]-> Type
            if rel in ("has_return_type", "returns_type") and row.get("src_type") in ("Function", "Method"):
                return_types[src_key] = row.get("tgt_name", "Unknown")

            if rel == "has_description" and row.get("tgt_type") == "GeneratedDescription":
                nodes_dict[src_key]["description"] = row.get("tgt_gen_desc") or row.get("tgt_doc") or nodes_dict[src_key]["description"]
            elif rel == "has_parameter":
                param_id = tgt_key
                param_name = row.get('tgt_name', 'param')
                param_type = parameter_types.get(param_id, "")
                param_info = f"{param_name}"
                if param_type:
                    param_info += f" ({param_type})"
                if row.get("tgt_doc"):
                    param_info += f": {row.get('tgt_doc', '')}"
                if param_info not in nodes_dict[src_key]["parameters"]:
                    nodes_dict[src_key]["parameters"].append(param_info)

        # Apply return types and fill in any missing parameter type info
        for node_id, node_info in nodes_dict.items():
            if node_id in return_types:
                node_info["return_type"] = return_types[node_id]

        ordered_public_node_ids = []
        for row in raw_relations:
            for node_id, node_type, is_public in (
                (row.get("src_id"), row.get("src_type"), row.get("src_is_public", False)),
                (row.get("tgt_id"), row.get("tgt_type"), row.get("tgt_is_public", False)),
            ):
                node_key = str(node_id) if node_id is not None else ""
                if (
                    node_key in nodes_dict
                    and node_key not in ordered_public_node_ids
                    and node_type not in ("GeneratedDescription", "Parameter", "Type", "File", "Attribute")
                    and is_public
                ):
                    ordered_public_node_ids.append(node_key)
                if len(ordered_public_node_ids) >= max_nodes:
                    break
            if len(ordered_public_node_ids) >= max_nodes:
                break

        public_node_ids = set(ordered_public_node_ids)

        for row in raw_relations:
            src_id = row.get("src_id")
            tgt_id = row.get("tgt_id")
            rel = row.get("relationship")

            if src_id is None or tgt_id is None:
                continue

            src_key = str(src_id)
            tgt_key = str(tgt_id)

            if src_key not in public_node_ids or tgt_key not in public_node_ids:
                continue

            if rel and rel != "has_description" and row.get("tgt_type") != "GeneratedDescription":
                rel_label = rel.replace('_', ' ').title()
                src_str = f"[{nodes_dict[src_key]['type']}] {nodes_dict[src_key]['name']}"
                tgt_str = f"[{nodes_dict[tgt_key]['type']}] {nodes_dict[tgt_key]['name']}"
                relationships.add(f"- {src_str} --({rel_label})--> {tgt_str}")

        public_nodes = [
            nodes_dict[nid]
            for nid in ordered_public_node_ids
            if nodes_dict[nid]["type"] != "GeneratedDescription"
        ]

        md_context = "# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE\n\n"
        md_context += "## 1. PRIMARY PUBLIC API ENDPOINTS (PREFER USING THESE)\n\n"

        if not public_nodes:
            md_context += "_No explicit public APIs retrieved. Rely on standard framework imports._\n\n"
            return md_context

        for info in public_nodes:
            md_context += f"### [{info['type']}] {info['name']}\n"
            if info["import_path"]:
                import_path = info["import_path"]
                md_context += f"**Import Path:** `{import_path}`\n\n"
                
                if info["type"] == "Method":
                    owner, method = import_path.rsplit(".", 1)
                    md_context += f"**Usage:** On an initialized `{owner.rsplit('.', 1)[-1]}` instance, call `instance.{method}(...)`.\n\n"
                elif import_path.startswith("phi.flow."):
                    # phi.flow is a module with exported attributes, not a package.
                    attribute_path = import_path[len("phi.flow."):]
                    exported = attribute_path.split(".", 1)[0]
                    md_context += f"**Usage:** `from phi.flow import {exported}; {attribute_path}(...)`\n\n"
                elif info["type"] == "Function" and "." in import_path:
                    parts = import_path.rsplit(".", 1)
                    if len(parts) == 2:
                        module_path, func_name = parts
                        # Extract the module name (last component)
                        module_name = module_path.split(".")[-1]
                        md_context += f"**Usage:** `{module_name}.{func_name}(...)` or `from {module_path} import {func_name}; {func_name}(...)`\n\n"
                elif info["type"] == "Class" and "." in import_path:
                    parts = import_path.rsplit(".", 1)
                    if len(parts) == 2:
                        module_path, class_name = parts
                    md_context += f"**Usage:** `from {module_path} import {class_name}; {class_name}(...)`\n\n"
            
            if info["description"]:
                md_context += f"**Description:**\n{info['description'][:600]}\n\n"
            
            if info["parameters"]:
                md_context += f"**Parameters:**\n"
                for param in info["parameters"]:
                    md_context += f"- {param}\n"
                md_context += "\n"
            
            if info["return_type"]:
                md_context += f"**Returns:** `{info['return_type']}`\n\n"
            
            if info["docstring"] and info["docstring"] != "No docstring available.":
                docstring = info['docstring']
                if len(docstring) > 3500:
                    docstring = docstring[:3500] + "\n[Docstring shortened; consult the original for remaining details.]"
                md_context += f"**Signature/Docstring:**\n```python\n{docstring}\n```\n\n"

        if relationships:
            md_context += "---\n\n## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES\n\n"
            md_context += "\n".join(sorted(relationships)) + "\n"

        return md_context

    def generate_grounded_code(self, task_description: str, codebase_context: str, max_tokens: int = 20000,
                               domain_context: str = "", api_resolution=None) -> str:
        """Step 5: Code Generation strictly preferring primary public APIs."""
        print("Generating complete codebase-aligned script with Claude...")
        self._require_llm()
        from knowledge_context.combined_retrieval import NAMESPACE_CAVEAT
        resolution_evidence = [{key: item.get(key) for key in
                                ("observed_call", "status", "quality", "code_id", "code_import_path")}
                               for item in (api_resolution or [])]

        response = self.client.messages.create(
            model=self.model,
                max_tokens=max_tokens,
            temperature=0,
            system=(
                "You are an expert computational software architect specializing in the PhiFlow differentiable physics framework. "
                "Your objective is to generate an executable Python simulation using the current task, retrieved public API documentation, and optional domain-reference guidance.\n"
                "The CURRENT TASK has authority over reference parameters, initial conditions, equations, time counts, and output filenames. "
                "Domain references describe prior implementations; adapt their methods without silently replacing the requested problem. "
                "Never copy a reference output filename over a requested output contract.\n\n"
                "ABSOLUTE HARD REQUIREMENTS:\n"
                "Return ONLY raw Python code, with NO markdown fences (```python, ``` etc.), NO prose, NO explanation, and NO comments.\n"
                "The output must be a complete, runnable script that can be saved directly to a .py file and executed immediately.\n"
                "Use documented public framework APIs. You may define local step/initialization/helper functions and use Python, NumPy, and standard-library arithmetic or output operations. "
                "Do not invent framework APIs or treat unresolved API candidates as verified signatures.\n"
                "Do NOT import from internal/private module locations or assume undocumented APIs exist.\n"
                "Follow the provided Usage examples and documented signatures. A qualified attribute endpoint is not necessarily an importable submodule.\n"
                "PhiFlow compatibility rules: pass grid resolutions as spatial(x=..., y=...) or spatial(x=..., y=..., z=...), never as Python tuples; construct vectors with vec(x=..., y=..., z=...) or tensor(..., channel(vector='...')).\n"
                "For cylinder(), include named center dimensions. In 2D, pass axis=vec(x=0, y=1) when depth is omitted; in 3D include z in the center and use axis='z' only with a z-dimensional center.\n"
                "For make_incompressible(), pass obstacles with the named obstacles= argument. For pressure solves, use the documented solve parameter and avoid unconstrained singular systems.\n"
                "If a required function or class is not in the context, find an alternative approach using only what IS provided.\n"
                "Ensure all variables and imports are defined, and preserve named spatial/channel dimensions.\n"
                "The script should produce the requested simulation or visualization behavior.\n"
                "Do not include comments, docstrings, markdown blocks, or any textual wrappers of any kind."
            ),
            messages=[
                {
                    "role": "user", 
                    "content": (
                        f"[EXISTING CODEBASE SCHEMA & STRUCTURES]\n"
                        f"{codebase_context}\n\n"
                        f"[DOMAIN REFERENCE PRIOR: CURRENT TASK OVERRIDES CONFLICTS]\n"
                        f"{domain_context or 'No domain-reference context supplied.'}\n\n"
                        f"[DOMAIN TO CODE API RESOLUTION EVIDENCE]\n"
                        f"{NAMESPACE_CAVEAT}\n{json.dumps(resolution_evidence, ensure_ascii=False)}\n\n"
                        f"[USER SIMULATION TASK REQUIREMENTS]\n"
                        f"{task_description}\n\n"
                        f"Generate the final Python script now. Output ONLY valid Python code with NO markdown fences, NO comments, and NO extra text."
                    )
                }
            ]
        )
        usage = getattr(response, "usage", None)
        self.last_generation_metadata = {
            "model": self.model, "temperature": 0, "max_tokens": max_tokens,
            "stop_reason": getattr(response, "stop_reason", None),
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
        }
        if self.last_generation_metadata["stop_reason"] == "max_tokens":
            raise ValueError("LLM generation hit max_tokens; incomplete code is not accepted")
        for block in response.content:
            if block.type == "text":
                raw_code = block.text.strip()
                
                # Strip markdown fences if present
                if raw_code.startswith("```"):
                    lines = raw_code.split("\n")
                    # Remove opening fence (and optional language specifier)
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    # Remove closing fence
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    raw_code = "\n".join(lines).strip()
                
                return raw_code

        raise ValueError("No text block found in Claude's response.")


# ==========================================
#  MAIN RUNNER
# ==========================================

if __name__ == "__main__":
    from knowledge_context.run_combined_experiment import main
    raise SystemExit(main())
