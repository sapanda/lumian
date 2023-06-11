import logging
import pinecone
from retry import retry

from .errors import PineconeException
from .interfaces import EmbedsClientInterface

# Retry Params
RETRY_TRIES = 3
RETRY_DELAY = 5
RETRY_BACKOFF = 2

logger = logging.getLogger(__name__)


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
        logger.debug(f"Pinecone client initialized: "
                     f"{index_name} / {region} / {namespace}")
        self.index_name = index_name
        self.index = self._create_index(dimensions)
        self.namespace = namespace

    @retry(PineconeException, tries=RETRY_TRIES,
           delay=RETRY_DELAY, backoff=RETRY_BACKOFF)
    def _create_index(self, dimensions: int) -> pinecone.Index:
        """Create the index if it doesn't exist."""
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                self.index_name,
                dimension=dimensions
            )
            logger.debug(f'Pinecone index created: {self.index_name}')
        try:
            index = pinecone.Index(self.index_name)
        except Exception as e:
            # TODO: This is a hack to handle a random exception that
            #       occurs within the pinecone client library
            logger.exception("Exception retrieving Pinecone Index", exc_info=e)
            raise PineconeException(
                detail="Exception retrieving Pinecone Index")
        return index

    def upsert(self, vectors: 'list[dict]'):
        """Upsert the vectors into the index."""
        logger.debug(f"Upserting to Pinecone: {len(vectors)} vectors")
        self.index.upsert(vectors=vectors, namespace=self.namespace)

    def search(self, id: int, embedding: 'list[int]', limit: int = 5) -> dict:
        """Retrieve the closest embeds for the input embedding"""
        logger.debug(f"Executing Pinecone search for object with ID {id}")
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
        logger.debug(f"Deleting Pinecone object with ID {id}")
        self.index.delete(filter={"object_id": {"$eq": id}},
                          namespace=self.namespace)
