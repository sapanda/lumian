from sqlalchemy import create_engine, DDL, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import Settings


SCHEMA = 'synthesis'

settings = Settings()
url = URL.create(
    drivername="postgresql",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name
)

engine = create_engine(url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

event.listen(
    Base.metadata,
    'before_create',
    DDL(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
)
