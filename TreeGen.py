import ast
import os
import anthropic
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import re
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class CodeParser(ast.NodeVisitor):
    """Parses a Python file to extract structured components matching the paper's schema."""
    def __init__(self, filename):
        self.filename = filename
        self.classes = []
        self.functions = []
        self.current_class = None

    def _get_type_str(self, node):
        """Converts AST annotation nodes into clean string representations of data types."""
        if node is None:
            return "Unknown"
        # ast.unparse converts the AST subtree back into its exact string representation
        return ast.unparse(node).strip()

    def visit_ClassDef(self, node):
        class_info = {
            "name": node.name,
            "methods": [],
            "attributes": set(),  # Collected via assignments inside class scope
            "docstring": ast.get_docstring(node) or ""
        }
        self.classes.append(class_info)
        
        old_class = self.current_class
        self.current_class = class_info
        self.generic_visit(node)
        self.current_class = old_class
        
        # Convert attributes set to list for serialization
        class_info["attributes"] = list(class_info["attributes"])

    def visit_FunctionDef(self, node):
        # Extract individual parameters and corresponding type hints
        parameters = []
        for arg in node.args.args:
            # Skip object instance pointers ('self', 'cls') to avoid graph noise
            if self.current_class and arg.arg in ("self", "cls"):
                continue
            
            param_type = self._get_type_str(arg.annotation) if arg.annotation else "Unknown"
            parameters.append({
                "name": arg.arg,
                "type": param_type
            })

        func_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "parameters": parameters,
            "return_type": self._get_type_str(node.returns) if node.returns else "Unknown"
        }
        
        if self.current_class:
            self.current_class["methods"].append(func_info)
        else:
            self.functions.append(func_info)
            
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Extracts class-level attributes and self instance attributes."""
        if self.current_class:
            for target in node.targets:
                # Matches simple class level variables: class MyClass: x = 1
                if isinstance(target, ast.Name):
                    self.current_class["attributes"].add(target.id)
                # Matches instance variables: self.x = 1 inside methods
                elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                    if target.value.id == "self":
                        self.current_class["attributes"].add(target.attr)
        self.generic_visit(node)


def parse_python_file(filepath):
    """Reads a Python file and extracts its structure using AST."""
    with open(filepath, "r", encoding="utf-8") as file:
        file_content = file.read()
    
    tree = ast.parse(file_content)
    parser = CodeParser(os.path.basename(filepath))
    parser.visit(tree)
    return parser


def find_python_files(directory, exclude_dirs=None):
    """Recursively finds all Python files in a directory while avoiding garbage paths."""
    if exclude_dirs is None:
        exclude_dirs = {'__pycache__', '.git', '.venv', 'venv', '.env', 'node_modules', '.pytest_cache'}
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files



def unpack_types(type_str):
    """Splits compound Union types or pipe types into a clean list of individual types."""
    if type_str == "Unknown":
        return []
    
    # Clean up 'Union[Type1, Type2]' -> 'Type1, Type2'
    if type_str.startswith("Union[") and type_str.endswith("]"):
        type_str = type_str[6:-1]
        
    # Split by commas (for Union) or pipes '|' (for Type1 | Type2)
    individual_types = re.split(r'[,|]', type_str)
    
    # Strip whitespace and ignore generic wrapper strings
    return [t.strip() for t in individual_types if t.strip()]

class MetadataEnricher:
    """Generates natural language summaries and numerical vector embeddings for the graph."""
    def __init__(self):
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2') 
        # SET ENVIRONMENT VARIABLE ANTHROPIC_API_KEY to your Anthropic API key before running this script
        self.client = anthropic.Anthropic()

    def get_embedding(self, text):
        """Converts string metadata into a 384-dimensional dense floating-point vector."""
        if not text.strip():
            return [0.0] * 384
        return self.embed_model.encode(text).tolist()
   
    def generate_llm_description(self, component_name, parent_context, context_text):
        if not context_text.strip():
            context_text = "No docstring available."
            
        try:
            response = self.client.messages.create(
                model="claude-sonnet-5",
                system=(
                    "You are an expert AI code analyst. Provide a brief, high-level, 1-2 sentence functional description "
                    "of this programming component based ONLY on its name, parent context, and provided docstring.\n\n"
                    "STRICT RULES:\n"
                    "1. NEVER write generic textbook definitions of Python concepts (e.g., do not explain what __init__ or a class is in general).\n"
                    "2. NEVER say 'Without seeing the specific code' or 'The code typically does...'.\n"
                    "3. If the docstring is missing, summarize ONLY what can be logically inferred from the name and parent class/parameters (e.g., 'Initializes the DataProcessor with a database target.').\n"
                    "4. Be concise, direct, and factual.\n" \
                    "5. Use no italics, bold, or other text formatting."
                ),
                messages=[
                    {
                        "role": "user", 
                        "content": f"Component: {component_name}\nParent Scope/Params: {parent_context}\nDocstring: {context_text}"
                    }
                ],
                max_tokens=100
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"Functional description generation failed: {str(e)}"

# ==========================================
# 3. NEO4J GRAPH BUILDER
# ==========================================
class KnowledgeGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._setup_indexes()

    def close(self):
        self.driver.close()

    def _setup_indexes(self):
        """Configures schema index constraints required for rapid hybrid retrieval matching."""
        with self.driver.session() as session:
            # 1. Full-Text Token Search Indexes
            session.run("CREATE FULLTEXT INDEX functionNames IF NOT EXISTS FOR (n:Function) ON EACH [n.name]")
            session.run("CREATE FULLTEXT INDEX classNames IF NOT EXISTS FOR (n:Class) ON EACH [n.name]")
            session.run("CREATE FULLTEXT INDEX methodNames IF NOT EXISTS FOR (n:Method) ON EACH [n.name]")
            
            # Index optimization for data types
            session.run("CREATE INDEX typeNames IF NOT EXISTS FOR (n:Type) ON (n.name)")

            # 2. Vector Semantic Similarity Indexes (384 dimensions for all-MiniLM-L6-v2)
            session.run("""
                CREATE VECTOR INDEX funcDocEmbed IF NOT EXISTS FOR (n:Function) ON (n.doc_embedding)
                OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """) 
            session.run("""
                CREATE VECTOR INDEX classDocEmbed IF NOT EXISTS FOR (n:Class) ON (n.doc_embedding)
                OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """) 
            session.run("""
                CREATE VECTOR INDEX methodDocEmbed IF NOT EXISTS FOR (n:Method) ON (n.doc_embedding)
                OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """) 
            session.run("""
                CREATE VECTOR INDEX descEmbed IF NOT EXISTS FOR (n:GeneratedDescription) ON (n.desc_embedding)
                OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """) 

    def create_file_nodes_and_relations(self, filename, parsed_data, enricher):
        """Assembles data models into Cypher commands executing atomic data injection."""
        base_file = os.path.basename(filename)
        
        with self.driver.session() as session:
            #  File identity
            session.run("MERGE (f:File {name: $name})", name=base_file)


            for func in parsed_data.functions:
                docstring = func["docstring"]
                params_str = ", ".join([p["name"] for p in func["parameters"]]) or "None"
                func_parent_context = f"Standalone Function defined in file '{base_file}'. Parameter signature: ({params_str})."

                llm_desc = enricher.generate_llm_description(func["name"],func_parent_context, docstring)
                
                doc_embed = enricher.get_embedding(docstring)
                desc_embed = enricher.get_embedding(llm_desc)
                
                # Composite functional namespace key to prevent same-name cross-file collisions
                func_id = f"{base_file}:{func['name']}"

                session.run("""
                    MATCH (f:File {name: $name})
                    MERGE (fn:Function {id: $func_id})
                    SET fn.name = $func_name, fn.docstring = $docstring, fn.doc_embedding = $doc_embed
                    MERGE (f)-[:defines_function]->(fn)
                    
                    MERGE (d:GeneratedDescription {text: $llm_desc})
                    SET d.desc_embedding = $desc_embed
                    MERGE (fn)-[:has_description]->(d)
                """, name=base_file, func_id=func_id, func_name=func["name"], docstring=docstring,
                     doc_embed=doc_embed, llm_desc=llm_desc, desc_embed=desc_embed)

                # Link Return Type if it's explicitly stated
                if func["return_type"] != "Unknown":
                    session.run("""
                        MATCH (fn:Function {id: $func_id})
                        MERGE (t:Type {name: $return_type})
                        MERGE (fn)-[:returns_type]->(t)
                    """, func_id=func_id, return_type=func["return_type"])

                # Link parameters and parameter type entities
                for param in func["parameters"]:
                    param_id = f"{func_id}({param['name']})"
                    session.run("""
                        MATCH (fn:Function {id: $func_id})
                        MERGE (p:Parameter {id: $param_id})
                        SET p.name = $param_name
                        MERGE (fn)-[:has_parameter]->(p)
                    """, func_id=func_id, param_id=param_id, param_name=param["name"])
                    types_list = unpack_types(param["type"])
                    for individual_type in types_list:
                        if param["type"] != "Unknown":
                            session.run("""
                                MATCH (p:Parameter {id: $param_id})
                                MERGE (t:Type {name: $param_type})
                                MERGE (p)-[:of_type]->(t)
                            """, param_id=param_id, param_type=individual_type)

            # Step C: Ingest File -> Class -> Methods & Attributes mappings
            for cls in parsed_data.classes:
                cls_docstring = cls["docstring"]
                
                # 1. Construct concrete structural context for the Class
                cls_methods_str = ", ".join([m["name"] for m in cls["methods"]]) or "None"
                cls_attrs_str = ", ".join(cls["attributes"]) or "None"
                cls_parent_context = f"Class defined in file '{base_file}'. Attributes: [{cls_attrs_str}]. Methods: [{cls_methods_str}]."
                
                # Generate description with structural context
                cls_llm_desc = enricher.generate_llm_description(cls["name"], cls_parent_context, cls_docstring)
                
                cls_doc_embed = enricher.get_embedding(cls_docstring)
                cls_desc_embed = enricher.get_embedding(cls_llm_desc)
                
                cls_id = f"{base_file}:{cls['name']}"

                session.run("""
                    MATCH (f:File {name: $name})
                    MERGE (c:Class {id: $cls_id})
                    SET c.name = $cls_name, c.docstring = $cls_docstring, c.doc_embedding = $cls_doc_embed
                    MERGE (f)-[:defines_class]->(c)
                    
                    MERGE (d:GeneratedDescription {text: $cls_llm_desc})
                    SET d.desc_embedding = $cls_desc_embed
                    MERGE (c)-[:has_description]->(d)
                """, name=base_file, cls_id=cls_id, cls_name=cls["name"], cls_docstring=cls_docstring,
                     cls_doc_embed=cls_doc_embed, cls_llm_desc=cls_llm_desc, cls_desc_embed=cls_desc_embed)

                for attr_name in cls["attributes"]:
                    session.run("""
                        MATCH (c:Class {id: $cls_id})
                        MERGE (a:Attribute {id: $attr_id})
                        SET a.name = $attr_name
                        MERGE (c)-[:has_attribute]->(a)
                    """, cls_id=cls_id, attr_id=f"{cls_id}.{attr_name}", attr_name=attr_name)

                for method in cls["methods"]:
                    m_docstring = method["docstring"]
                    
                    # 2. Construct concrete structural context for this Class Method
                    params_str = ", ".join([p["name"] for p in method["parameters"]]) or "None"
                    method_parent_context = f"Method of Class '{cls['name']}'. Parameter signature: ({params_str})."
                    
                    # Generate description with structural context
                    m_llm_desc = enricher.generate_llm_description(method["name"], method_parent_context, m_docstring)
                    
                    m_doc_embed = enricher.get_embedding(m_docstring)
                    m_desc_embed = enricher.get_embedding(m_llm_desc)
                    
                    method_id = f"{cls_id}.{method['name']}"

                    session.run("""
                        MATCH (c:Class {id: $cls_id})
                        MERGE (m:Method {id: $method_id})
                        SET m.name = $method_name, m.docstring = $m_docstring, m.doc_embedding = $m_doc_embed
                        MERGE (c)-[:has_method]->(m)
                        
                        MERGE (d:GeneratedDescription {text: $m_llm_desc})
                        SET d.desc_embedding = $m_desc_embed
                        MERGE (m)-[:has_description]->(d)
                    """, cls_id=cls_id, method_id=method_id, method_name=method["name"], m_docstring=m_docstring,
                         m_doc_embed=m_doc_embed, m_llm_desc=m_llm_desc, m_desc_embed=m_desc_embed)

                    if method["return_type"] != "Unknown":
                        session.run("""
                            MATCH (m:Method {id: $method_id})
                            MERGE (t:Type {name: $return_type})
                            MERGE (m)-[:returns_type]->(t)
                        """, method_id=method_id, return_type=method["return_type"])

                    for param in method["parameters"]:
                        param_id = f"{method_id}({param['name']})"
                        session.run("""
                            MATCH (m:Method {id: $method_id})
                            MERGE (p:Parameter {id: $param_id})
                            SET p.name = $param_name
                            MERGE (m)-[:has_parameter]->(p)
                        """, method_id=method_id, param_id=param_id, param_name=param["name"])
                        
                        types_list = unpack_types(param["type"])
                        for individual_type in types_list:
                            session.run("""
                                MATCH (p:Parameter {id: $param_id})
                                MERGE (t:Type {name: $param_type})
                                MERGE (p)-[:of_type]->(t)
                            """, param_id=param_id, param_type=individual_type)

    def process_repository(self, repo_path, enricher, exclude_dirs=None):
        """Walks directory paths recursively, executing the complete parser/ingestion pipeline."""
        python_files = find_python_files(repo_path, exclude_dirs)
        stats = {'total_files': len(python_files), 'successful': 0, 'failed': 0, 'errors': []}
        
        print(f"Targeting {len(python_files)} source files in target repository path...")
        
        for filepath in python_files:
            try:
                relative_path = os.path.relpath(filepath, repo_path)
                print(f"Processing node layer for: {relative_path}...", end=" ")
                
                parsed_ast = parse_python_file(filepath)
                self.create_file_nodes_and_relations(filepath, parsed_ast, enricher)
                
                print(f"✓")
                stats['successful'] += 1
            except Exception as e:
                error_msg = f"Ingestion runtime fail on {filepath}: {str(e)}"
                print(f"✗")
                stats['failed'] += 1
                stats['errors'].append(error_msg)
        return stats


if __name__ == "__main__":
    REPO_PATH = os.getenv("REPO_PATH")
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    print(f"Initializing Context-Aware Graph Pipeline for path: {REPO_PATH}...")
    
    try:
        print("Loading MiniLM vector transform spaces & initializing enrichment engines...")
        enricher_engine = MetadataEnricher()

        print("Opening secure transaction channels to Neo4j Instance...")
        kg_builder = KnowledgeGraphBuilder(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        print("Traversing files and launching database ingest sequences...")
        process_stats = kg_builder.process_repository(REPO_PATH, enricher_engine)
        
        kg_builder.close()
        print("\n=== Graph DB Building Complete ===")
        print(f"Successfully Configured: {process_stats['successful']} files.")
        print(f"Failed Components: {process_stats['failed']}")
        
    except Exception as general_err:
        print(f"\nCRITICAL PIPELINE EXCEPTION UNHANDLED: {str(general_err)}")