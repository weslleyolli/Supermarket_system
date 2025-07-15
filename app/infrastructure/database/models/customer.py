"""
Modelo de cliente
"""

from sqlalchemy import Column, Float, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class Customer(BaseModel):
    """Cliente"""

    __tablename__ = "customers"

    name = Column(String(200), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    cpf = Column(String(14), unique=True, index=True)
    address = Column(String(500))

    # Programa de fidelidade
    loyalty_points = Column(Float, default=0, nullable=False)

    # Relacionamentos
    sales = relationship("Sale", back_populates="customer")
