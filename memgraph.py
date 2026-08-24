from .neo4j_bolt import Neo4jBoltAdapter

class MemgraphAdapter(Neo4jBoltAdapter):
    def __init__(self):
        super().__init__("Memgraph", "MEMGRAPH_URI", "MEMGRAPH_USER", "MEMGRAPH_PASSWORD")
