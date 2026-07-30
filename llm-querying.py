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


DRY_RUN =False


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
        self.client = anthropic.Anthropic()
        
        
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
        """Step 3: Directed 2-Hop neighborhood expansion fetching linked GeneratedDescriptions."""
        if not seed_ids:
            return []
            
        print(f"Performing 2-hop graph traversal starting from {len(seed_ids)} target seed nodes...")
        with self.driver.session() as session:
            query = """
                MATCH (seed) WHERE seed.id IN $seed_ids
                OPTIONAL MATCH path = (seed)-[rel:has_parameter|defines_function|defines_class|has_method|returns_type|has_description*1..2]-(neighbor)
                UNWIND relationships(path) AS r
                WITH DISTINCT startNode(r) AS src, r, endNode(r) AS tgt
                
                // Fetch linked GeneratedDescription text for source node
                OPTIONAL MATCH (src)-[:has_description]->(src_desc:GeneratedDescription)
                // Fetch linked GeneratedDescription text for target node
                OPTIONAL MATCH (tgt)-[:has_description]->(tgt_desc:GeneratedDescription)
                
                RETURN src.id AS src_id,
                       labels(src)[0] AS src_type,
                       src.name AS src_name,
                       coalesce(src.docstring, "") AS src_doc,
                       coalesce(src_desc.text, src.text, "") AS src_gen_desc,
                       type(r) AS relationship,
                       tgt.id AS tgt_id,
                       labels(tgt)[0] AS tgt_type,
                       tgt.name AS tgt_name,
                       coalesce(tgt.docstring, "") AS tgt_doc,
                       coalesce(tgt_desc.text, tgt.text, "") AS tgt_gen_desc
            """
            result = session.run(query, seed_ids=seed_ids)
            return [row.data() for row in result]

    def filter_subgraph(self, task_description: str, raw_relations: List[dict], top_k: int = 35, min_score: float = 0.20) -> List[dict]:
        """Filters and reranks sub-graph triples using LLM-generated descriptions for semantic scoring."""
        if not raw_relations:
            return []
            
        print(f"\nReranking {len(raw_relations)} raw graph triples using Generated Descriptions...")
        query_vector = np.array(self.get_embedding(task_description), dtype=float).flatten()
        norm_q = np.linalg.norm(query_vector)

        if norm_q == 0:
            return raw_relations[:top_k]

        candidate_texts = []
        clean_rows = []

        for row in raw_relations:
            target_name = row.get("tgt_name") or ""
            target_type = row.get("tgt_type") or ""
            
            # Skip raw GeneratedDescription nodes from candidate list (they are metadata attached to code nodes)
            if target_type == "GeneratedDescription":
                continue
                
            # Skip dunder / private methods
            if target_name.startswith("__") and target_name.endswith("__"):
                continue

            # PRIORITIZE: Generated Description -> Docstring -> Empty
            gen_desc = row.get("tgt_gen_desc") or ""
            docstring = row.get("tgt_doc") or ""
            
            functional_summary = gen_desc if gen_desc else docstring

            # Construct contextual embedding string: "[Function] semi_lagrangian: Performs backward trajectory tracing..."
            text_representation = f"[{target_type}] {target_name}: {functional_summary}".strip()
            
            candidate_texts.append(text_representation)
            clean_rows.append(row)

        if not candidate_texts:
            return []

        # Batch encode candidates for performance
        candidate_vectors = self.embed_model.encode(candidate_texts)

        scored_rows = []
        for idx, row in enumerate(clean_rows):
            node_vector = np.array(candidate_vectors[idx], dtype=float).flatten()
            norm_n = np.linalg.norm(node_vector)

            score = float(np.dot(query_vector, node_vector) / (norm_q * norm_n)) if norm_n > 0 else 0.0
            scored_rows.append((score, row))

        # Sort descending by similarity score
        scored_rows.sort(key=lambda x: x[0], reverse=True)

        print("--- Top 10 Reranked Similarity Scores (Based on Generated Descriptions) ---")
        for score, row in scored_rows[:10]:
            target = row.get('tgt_name') or row.get('src_name')
            print(f"  Score: {score:.4f} | Target: [{row.get('tgt_type')}] {target}")

        filtered_results = [item[1] for item in scored_rows if item[0] >= min_score][:top_k]
        print(f"✓ Retained {len(filtered_results)} high-confidence triples (score >= {min_score})")

        return filtered_results

    def serialize_subgraph(self, raw_relations: List[dict]) -> str:
        """Step 4: Formats retrieved graph relationships into readable, rich markdown context,
        attaching LLM-generated descriptions directly to their parent components."""
        if not raw_relations:
            return "No matching codebase components found."

        nodes_dict = {}
        relationships = set()

        # Step 1: Collect node metadata and bind GeneratedDescriptions to parent nodes
        for row in raw_relations:
            src_id = row["src_id"]
            tgt_id = row["tgt_id"]
            rel = row["relationship"]

            # Initialize source component
            if src_id not in nodes_dict:
                nodes_dict[src_id] = {
                    "name": row["src_name"] or "Unknown",
                    "type": row["src_type"] or "Unknown",
                    "docstring": row["src_doc"] if row["src_type"] != "GeneratedDescription" else "",
                    "description": ""
                }

            # Initialize target component
            if tgt_id not in nodes_dict:
                nodes_dict[tgt_id] = {
                    "name": row["tgt_name"] or "Unknown",
                    "type": row["tgt_type"] or "Unknown",
                    "docstring": row["tgt_doc"] if row["tgt_type"] != "GeneratedDescription" else "",
                    "description": ""
                }

            # If edge is 'has_description', attach description text directly to the source component
            if rel == "has_description" and row["tgt_type"] == "GeneratedDescription":
                nodes_dict[src_id]["description"] = row["tgt_doc"] or ""

        # Step 2: Build structural dependency relationships (ignoring raw description nodes)
        for row in raw_relations:
            src_id = row["src_id"]
            tgt_id = row["tgt_id"]
            rel = row["relationship"]

            if rel and rel != "has_description" and row["tgt_type"] != "GeneratedDescription":
                rel_label = rel.replace('_', ' ').title()
                src_str = f"[{nodes_dict[src_id]['type']}] {nodes_dict[src_id]['name']}"
                tgt_str = f"[{nodes_dict[tgt_id]['type']}] {nodes_dict[tgt_id]['name']}"
                relationships.add(f"- {src_str} --({rel_label})--> {tgt_str}")

        # Step 3: Serialize into rich Markdown context
        md_context = "# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE\n\n"
        md_context += "## 1. COMPONENT SIGNATURES & FUNCTIONAL DESCRIPTIONS\n\n"

        for nid, info in nodes_dict.items():
            # Skip rendering standalone GeneratedDescription nodes as headers
            if info["type"] == "GeneratedDescription":
                continue

            md_context += f"### [{info['type']}] {info['name']}\n"
            
            # Display LLM-generated functional purpose if available
            if info["description"]:
                md_context += f"**Functional Purpose (LLM-Generated Summary):**\n{info['description']}\n\n"
            
            # Display source docstring/signature
            if info["docstring"] and info["docstring"] != "No docstring available.":
                md_context += f"**Signature/Docstring:**\n```python\n{info['docstring']}\n```\n\n"
            elif not info["description"]:
                md_context += "**Signature/Docstring:**\n```python\nNo docstring available.\n```\n\n"

        if relationships:
            md_context += "---\n\n## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES\n\n"
            md_context += "\n".join(sorted(relationships)) + "\n"

        return md_context

    def generate_grounded_code(self, task_description: str, codebase_context: str) -> str:
        """Step 5: Code Generation guided strictly by the retrieved repository structures."""
        print("Generating complete codebase-aligned script with Claude...")

        response = self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=20000,
            system=(
                "You are an expert computational software architect specializing in the PhiFlow differentiable physics framework. "
                "Your objective is to generate an executable Python simulation script based on the user's task requirements. "
                "You must align your solution exactly with the API, classes, methods, parameters, and naming patterns "
                "found in the existing codebase context provided below. Generate clean, documented, and fully complete code."
            ),
            messages=[
                {
                    "role": "user", 
                    "content": (
                        f"[EXISTING CODEBASE SCHEMA & STRUCTURES]\n"
                        f"{codebase_context}\n\n"
                        f"[USER SIMULATION TASK REQUIREMENTS]\n"
                        f"{task_description}\n\n"
                        f"Output only the complete Python simulation script inside standard ```python ... ``` formatting."
                    )
                }
            ]
        )
        for block in response.content:
            if block.type == "text":
                return block.text

        raise ValueError("No text block found in Claude's response.")


# ==========================================
#  MAIN RUNNER
# ==========================================

if __name__ == "__main__":
    all_dirs = [
        "heat_flow", "julia_set", "lid_driven_cavity", 
        "reaction_diffusion", "smoke_plume", "structural_mechanics", "wake_flow"
    ]
    
    BASE_DIR = Path("D:/Vivek/research")
    
    pipeline = E2ERagPipeline()
    
    try:
        for folder_name in all_dirs:
            print(f"\n==========================================")
            print(f" PROCESSING DOMAIN: {folder_name.upper()}")
            print(f"==========================================")
            
            # Output folder for generated context and python script
            output_dir = BASE_DIR / f"test_{folder_name}"
            os.makedirs(output_dir, exist_ok=True)
            
            task_file = BASE_DIR / "test" / f"{folder_name}.md"

            # Fallback check if the file is in test_<folder_name>/<folder_name>.md
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
            
            # Find Seed Nodes
            seed_nodes = pipeline.find_seed_nodes(blueprint)
            print(f"\n--- [2] Seed Nodes Found ({len(seed_nodes)}) ---")
            print(seed_nodes)
            
            # Graph Traversal & Subgraph Filtering
            raw_graph_data = pipeline.traverse_subgraph(seed_nodes)
            filtered_graph_data = pipeline.filter_subgraph(
                task_sheet_content, 
                raw_graph_data, 
                top_k=35, 
                min_score=0.2
            )
            print(f"--- Retained Top {len(filtered_graph_data)} Relevant Triples ---")

            # Context Serialization
            formatted_context = pipeline.serialize_subgraph(filtered_graph_data)
            
            # Save retrieved context for inspection
            context_file = output_dir / "retrieved_context.md"
            with open(context_file, "w", encoding="utf-8") as cf:
                cf.write(formatted_context)
            print(f"✓ Saved retrieved codebase context to: {context_file}")

            # Code Generation
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