import pinecone

from .interfaces import EmbedsClientInterface


# TODO: Add error handling
class PineconeClient(EmbedsClientInterface):
    def __init__(
            self,
            api_key: str,
            index_name: str,
            region: str,
            dimensions: int,
            namespace: str
            ):
        pinecone.init(api_key=api_key, environment=region)
        self.index_name = index_name
        self.index = self._create_index(dimensions)
        self.namespace = namespace

    def _create_index(self, dimensions: int) -> pinecone.Index:
        """Create the index if it doesn't exist."""
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                self.index_name,
                dimension=dimensions
            )
        return pinecone.Index(self.index_name)

    def upsert(self, vectors: 'list[dict]'):
        """Upsert the vectors into the index."""
        self.index.upsert(vectors=vectors, namespace=self.namespace)

    def search(self, id: int, embedding: 'list[int]', limit: int = 5) -> dict:
        """Retrieve the closest embeds for the input embedding"""
        query_result = self.index.query(
            [embedding],
            filter={"object_id": {"$eq": id}},
            top_k=limit,
            include_metadata=True,
            namespace=self.namespace,
        )
        return query_result

    def delete(self, id: int):
        """Delete all embeds for the input id."""
        self.index.delete(filter={"object_id": {"$eq": id}},
                          namespace=self.namespace)