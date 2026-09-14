import json
import os
import anthropic 
from pydantic import BaseModel, Field
from typing import List
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from pathlib import Path
from dotenv import load_dotenv
import numpy as np

# Load credentials securely
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

DRY_RUN = False


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
    def __init__(self):
        # vector transformer matching 
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2') 
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY was not found in environment variables!")

        self.client = anthropic.Anthropic(api_key=api_key)
        
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def generate_search_blueprint(self, task_description: str) -> dict:
        """Instruct Claude to analyze the physics task (including LaTeX math) and map it to framework targets."""
        print("Analyzing task markdown file to extract query parameters...")
        try:
            response = self.client.messages.create(
                model="claude-sonnet-5",
                max_tokens=1000,
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
            print(f"Failed to generate search blueprint: {e}")
            return {"semantic_queries": [], "target_classes": [], "target_functions": []}

    def find_seed_nodes(self, blueprint: dict) -> List[str]:
        """Step 2: Hybrid Search with wildcards and higher initial seed capacity."""
        seed_ids = set()
        
        with self.driver.session() as session:
            # A. Full-Text Search on Expected Class Names
            for cls_name in blueprint.get("target_classes", []):
                term = cls_name.strip()
                if not term or len(term) < 2: continue
                res = session.run("""
                    CALL db.index.fulltext.queryNodes("classNames", $term) YIELD node, score
                    RETURN node.id AS id LIMIT 5
                """, term=f"{term}* OR {term}")
                for r in res: seed_ids.add(r["id"])

            # B. Full-Text Search on Expected Function Names
            for func_name in blueprint.get("target_functions", []):
                term = func_name.strip()
                if not term or len(term) < 2: continue
                res = session.run("""
                    CALL db.index.fulltext.queryNodes("functionNames", $term) YIELD node, score
                    RETURN node.id AS id LIMIT 5
                """, term=f"{term}* OR {term}")
                for r in res: seed_ids.add(r["id"])

            # C. Vector Similarity Search across all vector indexes
            for sem_query in blueprint.get("semantic_queries", []):
                if not sem_query.strip(): continue
                vector = self.get_embedding(sem_query)
                
                # Check Generated Descriptions Index
                res = session.run("""
                    CALL db.index.vector.queryNodes("descEmbed", 5, $vector) YIELD node, score
                    MATCH (parent)-[:has_description]->(node)
                    RETURN parent.id AS id
                """, vector=vector)
                for r in res: seed_ids.add(r["id"])

                # Check Function Docstring Index
                res = session.run("""
                    CALL db.index.vector.queryNodes("funcDocEmbed", 4, $vector) YIELD node, score
                    RETURN node.id AS id
                """, vector=vector)
                for r in res: seed_ids.add(r["id"])

                # Check Class Docstring Index
                res = session.run("""
                    CALL db.index.vector.queryNodes("classDocEmbed", 4, $vector) YIELD node, score
                    RETURN node.id AS id
                """, vector=vector)
                for r in res: seed_ids.add(r["id"])

        return list(seed_ids)

    def get_embedding(self, text: str) -> List[float]:
        """Converts search strings into 384-dimensional vectors."""
        return self.embed_model.encode(text).tolist()

    def traverse_subgraph(self, seed_ids: List[str]) -> List[dict]:
        """Step 3: Directed 2-Hop neighborhood expansion fetching public API metadata."""
        if not seed_ids:
            return []
            
        print(f"Performing 2-hop graph traversal starting from {len(seed_ids)} target seed nodes...")
        with self.driver.session() as session:
            query = """
                MATCH (seed) WHERE seed.id IN $seed_ids
                OPTIONAL MATCH path = (seed)-[rel:has_parameter|defines_function|defines_class|has_method|returns_type|has_return_type|has_type|has_description*1..2]-(neighbor)
                UNWIND relationships(path) AS r
                WITH DISTINCT startNode(r) AS src, r, endNode(r) AS tgt
                
                OPTIONAL MATCH (src)-[:has_description]->(src_desc:GeneratedDescription)
                OPTIONAL MATCH (tgt)-[:has_description]->(tgt_desc:GeneratedDescription)
                
                RETURN src.id AS src_id,
                       labels(src)[0] AS src_type,
                       src.name AS src_name,
                       coalesce(src.is_public_api, false) AS src_is_public,
                       coalesce(src.import_path, "") AS src_import_path,
                       coalesce(src.docstring, "") AS src_doc,
                       coalesce(src_desc.text, src.text, "") AS src_gen_desc,
                       type(r) AS relationship,
                       tgt.id AS tgt_id,
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

        if norm_q == 0:
            return raw_relations[:top_k]

        candidate_texts = []
        clean_rows = []

        for row in raw_relations:
            target_name = row.get("tgt_name") or ""
            target_type = row.get("tgt_type") or ""
            
            if target_type == "GeneratedDescription":
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
        for final_score, base_score, row in scored_rows:
            if final_score < min_score:
                continue
            if not (row.get("src_is_public", False) or row.get("tgt_is_public", False)):
                continue

            if row.get("tgt_type") == "Method":
                if base_score < method_min_score:
                    continue
                owner = row.get("src_id")
                method_counts[owner] = method_counts.get(owner, 0) + 1
                if method_counts[owner] > max_methods_per_class:
                    continue

            filtered_results.append(row)
            if len(filtered_results) == top_k:
                break
        print(f"✓ Retained {len(filtered_results)} high-confidence public-api triples (score >= {min_score})")

        return filtered_results

    def serialize_subgraph(self, raw_relations: List[dict], max_nodes: int = 18) -> str:
        """Formats the retrievable public API context and omits private/internal symbols by default."""
        if not raw_relations:
            return "No matching codebase components found."

        nodes_dict = {}
        relationships = set()
        parameter_types = {}  # Map from parameter ID to type name
        return_types = {}  # Map from function/method ID to return type name

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
                    "description": "",
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
                    "description": "",
                    "parameters": [],
                    "return_type": ""
                }

            # Build parameter-to-type mapping: Parameter -[has_type]-> Type
            if rel == "has_type" and row.get("src_type") == "Parameter":
                parameter_types[src_key] = row.get("tgt_name", "Unknown")
            
            # Build return-type mapping: Function/Method -[has_return_type|returns_type]-> Type
            if rel in ("has_return_type", "returns_type") and row.get("src_type") in ("Function", "Method"):
                return_types[src_key] = row.get("tgt_name", "Unknown")

            if rel == "has_description" and row.get("tgt_type") == "GeneratedDescription":
                nodes_dict[src_key]["description"] = row.get("tgt_doc") or ""
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
                    and node_type not in ("GeneratedDescription", "Method")
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
                
                # Extract module context for Functions to show calling convention
                if info["type"] == "Function" and "." in import_path:
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
                        md_context += f"**Usage:** `from {import_path} import {class_name}; {class_name}(...)` or direct instantiation from phi.flow\n\n"
            
            if info["description"]:
                md_context += f"**Description:**\n{info['description']}\n\n"
            
            if info["parameters"]:
                md_context += f"**Parameters:**\n"
                for param in info["parameters"]:
                    md_context += f"- {param}\n"
                md_context += "\n"
            
            if info["return_type"]:
                md_context += f"**Returns:** `{info['return_type']}`\n\n"
            
            if info["docstring"] and info["docstring"] != "No docstring available.":
                md_context += f"**Signature/Docstring:**\n```python\n{info['docstring']}\n```\n\n"

        if relationships:
            md_context += "---\n\n## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES\n\n"
            md_context += "\n".join(sorted(relationships)) + "\n"

        return md_context

    def generate_grounded_code(self, task_description: str, codebase_context: str) -> str:
        """Step 5: Code Generation strictly preferring primary public APIs."""
        print("Generating complete codebase-aligned script with Claude...")

        response = self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=20000,
            system=(
                "You are an expert computational software architect specializing in the PhiFlow differentiable physics framework. "
                "Your objective is to generate an executable Python simulation script based ONLY on the user's task requirements and the retrieved public API context.\n\n"
                "ABSOLUTE HARD REQUIREMENTS:\n"
                "Return ONLY raw Python code, with NO markdown fences (```python, ``` etc.), NO prose, NO explanation, and NO comments.\n"
                "The output must be a complete, runnable script that can be saved directly to a .py file and executed immediately.\n"
                "CRITICAL: Never invent, define, or use functions or classes that are NOT explicitly documented in the provided context.\n"
                "Always use ONLY functions and classes from the retrieved public API endpoints.\n"
                "Do NOT import from internal/private module locations or assume undocumented APIs exist.\n"
                "Use the exact import paths and signatures shown in the context. Do not guess or modify them.\n"
                "PhiFlow compatibility rules: pass grid resolutions as spatial(x=..., y=...) or spatial(x=..., y=..., z=...), never as Python tuples; construct vectors with vec(x=..., y=..., z=...) or tensor(..., channel(vector='...')).\n"
                "For cylinder(), include named center dimensions. In 2D, pass axis=vec(x=0, y=1) when depth is omitted; in 3D include z in the center and use axis='z' only with a z-dimensional center.\n"
                "For make_incompressible(), pass obstacles with the named obstacles= argument. For pressure solves, use the documented solve parameter and avoid unconstrained singular systems.\n"
                "If a required function or class is not in the context, find an alternative approach using only what IS provided.\n"
                "Ensure all variables, classes, functions, and imports are valid and defined in the context.\n"
                "The script should produce the requested simulation or visualization behavior.\n"
                "Do not include comments, docstrings, markdown blocks, or any textual wrappers of any kind."
            ),
            messages=[
                {
                    "role": "user", 
                    "content": (
                        f"[EXISTING CODEBASE SCHEMA & STRUCTURES]\n"
                        f"{codebase_context}\n\n"
                        f"[USER SIMULATION TASK REQUIREMENTS]\n"
                        f"{task_description}\n\n"
                        f"Generate the final Python script now. Output ONLY valid Python code with NO markdown fences, NO comments, and NO extra text. Every function and class must be from the context above."
                    )
                }
            ]
        )
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
    all_dirs = [
        "heat_flow","burgers2d","julia_set", "lid_driven_cavity", 
        "reaction_diffusion", "smoke_plume", "structural_mechanics", "wake_flow"
    ]
    
    BASE_DIR = Path("D:/Vivek/research")
    
    pipeline = E2ERagPipeline()
    
    try:
        for folder_name in all_dirs:
            print(f"\n==========================================")
            print(f" PROCESSING DOMAIN: {folder_name.upper()}")
            print(f"==========================================")
            
            output_dir = BASE_DIR / f"test_{folder_name}"
            os.makedirs(output_dir, exist_ok=True)
            
            task_file = BASE_DIR / "test" / f"{folder_name}.md"

            if not task_file.exists():
                alt_task_file = output_dir / f"{folder_name}.md"
                if alt_task_file.exists():
                    task_file = alt_task_file
                else:
                    print(f"❌ ERROR: Task file not found at '{task_file}' or '{alt_task_file}'. Skipping {folder_name}!")
                    continue

            print(f"Reading task requirements from: {task_file}")
            with open(task_file, "r", encoding="utf-8") as f:
                task_sheet_content = f.read()

            first_line = task_sheet_content.strip().split('\n')[0] if task_sheet_content else "EMPTY"
            print(f"   --> Task Title Preview: {first_line[:80]}")

            blueprint = pipeline.generate_search_blueprint(task_sheet_content)
            print(f"\n--- [1] Blueprint Generated ---")
            print(json.dumps(blueprint, indent=2))
            
            seed_nodes = pipeline.find_seed_nodes(blueprint)
            print(f"\n--- [2] Seed Nodes Found ({len(seed_nodes)}) ---")
            print(seed_nodes)
            
            raw_graph_data = pipeline.traverse_subgraph(seed_nodes)
            filtered_graph_data = pipeline.filter_subgraph(
                task_sheet_content, 
                raw_graph_data, 
                top_k=24, 
                min_score=0.15,
                method_min_score=0.30,
                max_methods_per_class=3,
                public_boost=0.20,
                private_penalty=0.15
            )
            print(f"--- Retained Top {len(filtered_graph_data)} Relevant Triples ---")

            formatted_context = pipeline.serialize_subgraph(filtered_graph_data, max_nodes=18)
            
            context_file = output_dir / "retrieved_context.md"
            with open(context_file, "w", encoding="utf-8") as cf:
                cf.write(formatted_context)
            print(f"✓ Saved retrieved codebase context to: {context_file}")

            if DRY_RUN:
                print(f"Check context file here: {context_file}")
            else:
                final_code = pipeline.generate_grounded_code(task_sheet_content, formatted_context)
                
                output_file = output_dir / f"generated_{folder_name}_simulation.py"
                with open(output_file, "w", encoding="utf-8") as out_f:
                    out_f.write(final_code)
                print(f"✓ Successfully saved generated solution to: {output_file}")

    finally:
        pipeline.close()