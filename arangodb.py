import os
from arango import ArangoClient
from .base import GraphAdapter

class ArangoDBAdapter(GraphAdapter):
    name = "ArangoDB"
    def __init__(self):
        self.url=os.getenv("ARANGO_URL")
        self.user=os.getenv("ARANGO_USER")
        self.password=os.getenv("ARANGO_PASSWORD")
        self.dbname=os.getenv("ARANGO_DB","benchmark")
        self.client=self.db=self.v=self.e=None

    def connect(self):
        if not self.url or not self.password:
            raise RuntimeError("Missing ArangoDB connection environment variables")
        self.client=ArangoClient(hosts=self.url)
        self.db=self.client.db(self.dbname, username=self.user, password=self.password)
        if not self.db.has_collection("users"):
            self.db.create_collection("users")
        if not self.db.has_collection("votes"):
            self.db.create_collection("votes", edge=True)
        self.v=self.db.collection("users"); self.e=self.db.collection("votes")
        if not self.db.has_graph("benchmark_graph"):
            self.db.create_graph("benchmark_graph", edge_definitions=[
                {"edge_collection":"votes","from_vertex_collections":["users"],"to_vertex_collections":["users"]}])
        self.g=self.db.graph("benchmark_graph")

    def close(self):
        if self.client: self.client.close()

    def reset(self):
        for c in ("votes","users"):
            if self.db.has_collection(c):
                self.db.collection(c).truncate()

    def load_edges(self, edges, batch_size):
        for i in range(0,len(edges),batch_size):
            rows=edges[i:i+batch_size]
            verts={x for r in rows for x in (str(r[0]),str(r[1]))}
            self.v.insert_many([{"_key":x,"id":x} for x in verts], overwrite=True)
            self.e.insert_many([{"_from":"users/"+str(a),"_to":"users/"+str(b)} for a,b in rows], overwrite=False, overwrite_mode="ignore")

    def one_hop(self,node):
        return self._aql("""FOR v,e,p IN 1..1 OUTBOUND @start GRAPH 'benchmark_graph' RETURN v.id""", {"start":"users/"+str(node)})

    def two_hop(self,node):
        return self._aql("""FOR v,e,p IN 2..2 OUTBOUND @start GRAPH 'benchmark_graph' LIMIT 100 RETURN v.id""", {"start":"users/"+str(node)})

    def three_hop(self,node):
        return self._aql("""FOR v,e,p IN 3..3 OUTBOUND @start GRAPH 'benchmark_graph' LIMIT 100 RETURN v.id""", {"start":"users/"+str(node)})

    def point_lookup(self,node):
        return self._aql("RETURN DOCUMENT('users/'+@id).id", {"id":str(node)})

    def indexed_lookup(self,node):
        return self._aql("FOR u IN users FILTER u.id == @id RETURN u.id", {"id":str(node)})

    def aggregation(self):
        return self._aql("""FOR e IN votes COLLECT src=e._from WITH COUNT INTO c RETURN {src:src,c:c} LIMIT 100""")

    def mixed_read(self,node):
        return self.point_lookup(node)

    def mixed_write(self,src,dst,token):
        return self.e.insert({"_from":"users/"+str(src),"_to":"users/"+str(dst),"token":token})

    def mixed_delete(self,token):
        self.e.delete_match({"token":token})

    def footprint(self):
        try:
            return str(self.db.collection("users").statistics())
        except Exception:
            return "not observable"

    def _aql(self,query,bind=None):
        return list(self.db.aql.execute(query, bind_vars=bind or {}))
