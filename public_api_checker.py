from pathlib import Path
import ast
import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

REPO_PATH = Path(os.getenv("REPO_PATH") or ".")
FLOW_FILE = REPO_PATH / "flow.py"

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

DRY_RUN = False


def get_tier1_exports(flow_file: Path) -> set[str]:
    """Extracts top-level symbols and __all__ exports from flow.py."""
    if not flow_file.exists():
        print(f"Warning: {flow_file} does not exist. Returning empty export set.")
        return set()

    with open(flow_file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    symbols = set()
    
    for node in ast.walk(tree):
        #  Parse standard imports: from ... import X as Y / X
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    symbols.add(alias.asname or alias.name)

        #  Parse top-level classes and functions not starting with '_'
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                symbols.add(node.name)

        #  Parse explicit __all__ = [...] assignments
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                symbols.add(elt.value)

    return symbols


if __name__ == "__main__":
    print(f"Parsing top-level public exports in {FLOW_FILE}...")
    tier1_symbols = get_tier1_exports(FLOW_FILE)
    print(f"Found {len(tier1_symbols)} top-level entry points in flow.py.\n")

    if not DRY_RUN:
        driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

        with driver.session() as session:
            #Reset existing flags and import paths
            print("Step 0: Resetting public API flags & import paths...")
            session.run("""
                MATCH (n)
                WHERE n:Class OR n:Function OR n:Method OR n:File OR n:Type
                SET n.is_public_api = false,
                    n.import_path = null
            """)

            # Tag Tier 1 entry points exported by flow.py
            print("Step 1: Tagging Tier 1 entry points from flow.py...")
            res1 = session.run("""
                UNWIND $symbols AS sym
                MATCH (n)
                WHERE (n:Class OR n:Function OR n:Type) AND n.name = sym
                   OR (n:File AND (n.name = sym + '.py' OR n.name = sym))
                SET n.is_public_api = true,
                    n.import_path = 'phi.flow.' + n.name
                RETURN count(DISTINCT n) AS count
            """, symbols=list(tier1_symbols))
            print(f"  --> Tagged {res1.single()['count']} Tier-1 direct export nodes (set import_path to 'phi.flow.*').")

            #  Propagate to public functions and classes inside exported submodules/files
            print(" Propagating to functions/classes inside public submodules...")
            res2 = session.run("""
                MATCH (f:File {is_public_api: true})-[:defines_function|defines_class]->(n)
                WHERE (n:Function OR n:Class)
                  AND NOT n.name STARTS WITH '_'
                WITH f, n, replace(f.name, '.py', '') AS mod_name
                SET n.is_public_api = true,
                    n.import_path = coalesce(n.import_path, 'phi.flow.' + mod_name + '.' + n.name)
                RETURN count(DISTINCT n) AS count
            """)
            print(f"  --> Tagged {res2.single()['count']} public functions/classes inside exported modules.")

            #  Propagate to public methods on public classes
            print(" Propagating to public methods on public classes...")
            res3 = session.run("""
                MATCH (c:Class {is_public_api: true})-[:has_method]->(m:Method)
                WHERE NOT m.name STARTS WITH '_'
                SET m.is_public_api = true,
                    m.import_path = c.import_path + '.' + m.name
                RETURN count(DISTINCT m) AS count
            """)
            print(f"  --> Tagged {res3.single()['count']} public class methods.")

            # Step 4: Fallback import paths for internal/private components
            print("Step 4: Assigning fallback import locations for internal nodes...")
            res4 = session.run("""
                MATCH (f:File)-[:defines_function|defines_class]->(n)
                WHERE n.is_public_api = false OR n.is_public_api IS NULL
                WITH f, n, replace(f.name, '.py', '') AS mod_name
                SET n.import_path = 'phi.' + mod_name + '.' + n.name
                RETURN count(DISTINCT n) AS count
            """)
            print(f"  --> Added structural module fallback paths to {res4.single()['count']} internal nodes.")

            # Summary
            total_res = session.run("""
                MATCH (n)
                WHERE n.is_public_api = true
                RETURN labels(n)[0] AS type, count(n) AS count
            """).data()

            print("\n================ SUMMARY ================")
            for row in total_res:
                print(f" - [{row['type']}]: {row['count']} public nodes")

        driver.close()
        print("\n✓ Database tagging and import path assignment complete.")