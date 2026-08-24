from .neo4j_bolt import Neo4jBoltAdapter

class Neo4jAdapter(Neo4jBoltAdapter):
    def __init__(self):
        super().__init__("Neo4j", "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD")
