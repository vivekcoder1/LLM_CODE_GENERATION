from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()
driver = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')))

with driver.session() as session:
    result = session.run("""
        MATCH (n:Function {name: 'make_incompressible'})
        RETURN n.name, n.is_public_api, n.import_path, n.docstring
    """)
    records = result.data()
    if records:
        for record in records:
            print(f"Name: {record['n.name']}")
            print(f"Is Public: {record['n.is_public_api']}")
            print(f"Import Path: {record['n.import_path']}")
            print(f"Doc: {record['n.docstring'][:200] if record['n.docstring'] else 'None'}")
    else:
        print("make_incompressible not found")
        
    # Also check what functions ARE public in fluid.py module
    print("\n\nPublic functions in fluid module:")
    result2 = session.run("""
        MATCH (n:Function) WHERE n.import_path CONTAINS 'fluid'
        RETURN n.name, n.is_public_api, n.import_path
        LIMIT 20
    """)
    for record in result2:
        print(f"  {record['n.name']}: public={record['n.is_public_api']}, path={record['n.import_path']}")

driver.close()
