import os
import redis
from .base import GraphAdapter

class FalkorDBAdapter(GraphAdapter):
    name = "FalkorDB"
    def __init__(self):
        self.host = os.getenv("FALKORDB_HOST")
        self.port = int(os.getenv("FALKORDB_PORT", "6379"))
        self.password = os.getenv("FALKORDB_PASSWORD")
        self.r = None
        self.graph = "benchmark"

    def connect(self):
        if not self.host:
            raise RuntimeError("Missing FALKORDB_HOST")
        self.r = redis.Redis(host=self.host, port=self.port, password=self.password,
                             decode_responses=True, socket_timeout=30)
        self.r.ping()

    def close(self):
        if self.r: self.r.close()

    def reset(self):
        self.r.execute_command("GRAPH.DELETE", self.graph)

    def load_edges(self, edges, batch_size):
        # FalkorDB accepts Cypher via GRAPH.QUERY. One query per batch keeps
        # network overhead bounded and makes the load procedure reproducible.
        for i in range(0, len(edges), batch_size):
            rows = edges[i:i+batch_size]
            statements = []
            for src, dst in rows:
                s = str(src).replace("\\","\\\\").replace("'","\\'")
                d = str(dst).replace("\\","\\\\").replace("'","\\'")
                statements.append(f"MERGE (a:User {{id:'{s}'}}) MERGE (b:User {{id:'{d}'}}) MERGE (a)-[:VOTED_FOR]->(b)")
            self._query(" ".join(statements))

    def one_hop(self, node):
        return self._query("MATCH (a:User {id:$id})-[:VOTED_FOR]->(b) RETURN b.id", {"id":str(node)})

    def two_hop(self, node):
        return self._query("MATCH (a:User {id:$id})-[:VOTED_FOR]->()-[:VOTED_FOR]->(b) RETURN b.id LIMIT 100", {"id":str(node)})

    def three_hop(self, node):
        return self._query("MATCH (a:User {id:$id})-[:VOTED_FOR]->()-[:VOTED_FOR]->()-[:VOTED_FOR]->(b) RETURN b.id LIMIT 100", {"id":str(node)})

    def point_lookup(self, node):
        return self._query("MATCH (a:User {id:$id}) RETURN a.id", {"id":str(node)})

    def indexed_lookup(self, node):
        return self._query("MATCH (a:User {id:$id}) RETURN a.id", {"id":str(node)})

    def aggregation(self):
        return self._query("MATCH (a:User)-[:VOTED_FOR]->() RETURN a.id, count(*) AS c LIMIT 100")

    def mixed_read(self, node):
        return self.point_lookup(node)

    def mixed_write(self, src, dst, token):
        q = "MATCH (a:User {id:$src}), (b:User {id:$dst}) CREATE (a)-[:BENCHMARK_WRITE {token:$token}]->(b)"
        return self._query(q, {"src":str(src), "dst":str(dst), "token":token})

    def mixed_delete(self, token):
        return self._query("MATCH ()-[r:BENCHMARK_WRITE {token:$token}]->() DELETE r", {"token":token})

    def footprint(self):
        return "not observable from generic driver; record provider dashboard/instance specs manually"

    def _query(self, cypher, params=None):
        # Parameter passing support varies by RedisGraph/FalkorDB versions.
        # Literalized read queries are used below for compatibility.
        if params:
            for k,v in params.items():
                cypher = cypher.replace("$"+k, "'" + str(v).replace("'","\\'") + "'")
        return self.r.execute_command("GRAPH.QUERY", self.graph, cypher)
