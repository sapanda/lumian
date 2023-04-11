from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class Transcript(Base):
    __tablename__ = "transcript"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSONB)
