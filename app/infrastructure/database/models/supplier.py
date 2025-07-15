"""
Modelo de fornecedor
"""

from sqlalchemy import Column, String

from .base import BaseModel


class Supplier(BaseModel):
    """Fornecedor"""

    __tablename__ = "suppliers"

    name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    cnpj = Column(String(18), unique=True, index=True)
    address = Column(String(500))
