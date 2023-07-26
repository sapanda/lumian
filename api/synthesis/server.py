import logging

from .interfaces import (
    OpenAIClientInterface, EmbedsClientInterface, SynthesisInterface
)
from .openai_client import OpenAIClient
from .pinecone_client import PineconeClient
from .synthesis import Synthesis
from app import settings


logger = logging.getLogger(__name__)

openai_client = None
embeds_client = None


def get_openai_client() -> OpenAIClientInterface:
    """OpenAI client provider"""
    global openai_client
    if openai_client is None:
        openai_client = OpenAIClient(
            completions_api_type=settings.OPENAI_COMPLETIONS_API_TYPE,
            completions_api_key=settings.OPENAI_COMPLETIONS_API_KEY,
            completions_api_base=settings.OPENAI_COMPLETIONS_API_BASE,
            completions_api_version=settings.OPENAI_COMPLETIONS_API_VERSION,
            completions_model=settings.OPENAI_COMPLETIONS_MODEL,
            embeddings_api_type=settings.OPENAI_EMBEDDINGS_API_TYPE,
            embeddings_api_key=settings.OPENAI_EMBEDDINGS_API_KEY,
            embeddings_api_base=settings.OPENAI_EMBEDDINGS_API_BASE,
            embeddings_api_version=settings.OPENAI_EMBEDDINGS_API_VERSION,
            embeddings_model=settings.OPENAI_EMBEDDINGS_MODEL
        )
    return openai_client


def get_embeds_client() -> EmbedsClientInterface:
    """Embeds client provider"""

    # TODO: This is annoying. Currently all our prod & dev users
    #       are using a namespace starting with "dev-"
    if settings.PINECONE_USER:
        namespace = f'dev-{settings.PINECONE_USER}'
    else:
        namespace = 'dev'

    global embeds_client
    if embeds_client is None:
        embeds_client = PineconeClient(
            api_key=settings.PINECONE_API_KEY,
            index_name=settings.PINECONE_INDEX,
            region=settings.PINECONE_REGION,
            dimensions=settings.PINECONE_DIMENSIONS,
            namespace=namespace
        )
    return embeds_client


def get_synthesis(
    openai_client: OpenAIClientInterface = get_openai_client(),
    embeds_client: EmbedsClientInterface = get_embeds_client()
) -> SynthesisInterface:
    """Synthesis instance provider"""
    return Synthesis(
        openai_client=openai_client,
        embeds_client=embeds_client
    )
