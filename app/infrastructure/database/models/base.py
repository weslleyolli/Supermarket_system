"""
Modelo base para todos os modelos da aplicação
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """
    Modelo base com campos comuns
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
