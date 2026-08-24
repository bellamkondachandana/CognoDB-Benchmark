import os
from neo4j import GraphDatabase
from .base import GraphAdapter

class Neo4jBoltAdapter(GraphAdapter):
    def __init__(self, name, uri_env, user_env, password_env):
        self.name = name
        self.uri = os.getenv(uri_env)
        self.user = os.getenv(user_env)
        self.password = os.getenv(password_env)
        self.driver = None

    def connect(self):
        if not self.uri or not self.password:
            raise RuntimeError(f"Missing {self.name} connection environment variables")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.driver.verify_connectivity()

    def close(self):
        if self.driver: self.driver.close()

    def reset(self):
        with self.driver.session() as s:
            s.run("MATCH (n) DETACH DELETE n").consume()

    def load_edges(self, edges, batch_size):
        q = """UNWIND $rows AS r
               MERGE (a:User {id:r.source})
               MERGE (b:User {id:r.target})
               MERGE (a)-[:VOTED_FOR]->(b)"""
        with self.driver.session() as s:
            for i in range(0, len(edges), batch_size):
                s.run(q, rows=edges[i:i+batch_size]).consume()

    def one_hop(self, node):
        return self._run("MATCH (a:User {id:$id})-[:VOTED_FOR]->(b) RETURN b.id", id=str(node))

    def two_hop(self, node):
        return self._run("""MATCH (a:User {id:$id})-[:VOTED_FOR]->()-[:VOTED_FOR]->(b)
                            RETURN b.id LIMIT 100""", id=str(node))

    def three_hop(self, node):
        return self._run("""MATCH (a:User {id:$id})-[:VOTED_FOR]->()-[:VOTED_FOR]->()-[:VOTED_FOR]->(b)
                            RETURN b.id LIMIT 100""", id=str(node))

    def point_lookup(self, node):
        return self._run("MATCH (a:User {id:$id}) RETURN a.id", id=str(node))

    def indexed_lookup(self, node):
        return self._run("MATCH (a:User {id:$id}) RETURN a.id", id=str(node))

    def aggregation(self):
        return self._run("MATCH (a:User)-[:VOTED_FOR]->() RETURN a.id, count(*) AS c LIMIT 100")

    def mixed_read(self, node):
        return self.point_lookup(node)

    def mixed_write(self, src, dst, token):
        return self._run("""MATCH (a:User {id:$src}), (b:User {id:$dst})
                            CREATE (a)-[:BENCHMARK_WRITE {token:$token}]->(b)""",
                         src=str(src), dst=str(dst), token=token)

    def mixed_delete(self, token):
        return self._run("MATCH ()-[r:BENCHMARK_WRITE {token:$token}]->() DELETE r", token=token)

    def _run(self, q, **params):
        with self.driver.session() as s:
            return list(s.run(q, **params))

    def footprint(self):
        return "not observable from generic driver; record provider dashboard/instance specs manually"
