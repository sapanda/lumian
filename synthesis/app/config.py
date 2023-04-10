from pydantic import BaseSettings


class Settings(BaseSettings):
    """Global settings model"""
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    openai_org_id: str
    openai_api_key: str
    max_summary_size: int = 400
    line_min_size: int = 90
    chunk_min_words: int = 500
    examples_file: str = 'examples.json'
    debug: bool = False
