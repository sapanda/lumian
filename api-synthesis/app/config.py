from enum import Enum
from pydantic import BaseSettings


class ModeEnum(str, Enum):
    local = 'local'
    github = 'github'
    development = 'dev'
    production = 'prod'


class Settings(BaseSettings):
    """Global settings model"""
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str

    openai_completions_api_type: str = "open_ai"
    openai_completions_api_key: str
    openai_completions_api_base: str = None
    openai_completions_api_version: str = None
    openai_completions_model: str = None

    openai_embeddings_api_type: str = "open_ai"
    openai_embeddings_api_key: str
    openai_embeddings_api_base: str = None
    openai_embeddings_api_version: str = None
    openai_embeddings_model: str = None

    pinecone_api_key: str
    pinecone_region: str
    pinecone_index: str
    pinecone_dimensions: int
    pinecone_user: str = None

    indexed_line_min_chars: int = 90
    chunk_min_tokens_summary: int = 2000
    chunk_min_tokens_query: int = 400
    max_input_tokens_summary: int = 2500
    max_input_tokens_query: int = 3400
    max_input_tokens_metadata: int = 3600

    sentry_dsn: str = None

    debug: bool = False
    synthesis_log_level: str = 'INFO'
    deploy_mode: ModeEnum = ModeEnum.production
