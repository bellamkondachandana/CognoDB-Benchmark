from .neo4j_bolt import Neo4jBoltAdapter

class CognoDBAdapter(Neo4jBoltAdapter):
    def __init__(self):
        super().__init__("CognoDB", "COGNODB_URI", "COGNODB_USER", "COGNODB_PASSWORD")
