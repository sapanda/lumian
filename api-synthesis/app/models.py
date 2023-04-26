from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base, SCHEMA


class Transcript(Base):
    __tablename__ = "transcript"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSONB)
