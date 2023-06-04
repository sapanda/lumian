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

    openai_org_id: str
    openai_api_key: str

    pinecone_api_key: str
    pinecone_region: str
    pinecone_index: str
    pinecone_dimensions: int
    pinecone_user: str = None

    line_min_size: int = 90
    chunk_min_words: int = 500
    context_max_chars: int = 6000
    examples_dir: str = 'examples'

    sentry_dsn: str = None

    debug: bool = False
    deploy_mode: ModeEnum = ModeEnum.production
