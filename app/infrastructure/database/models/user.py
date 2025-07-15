"""
Modelo de usuário
"""

import enum

from sqlalchemy import Boolean, Column, Enum, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class UserRole(str, enum.Enum):
    """Tipos de usuário"""

    ADMIN = "admin"
    CASHIER = "cashier"
    SUPERVISOR = "supervisor"


class User(BaseModel):
    """Modelo de usuário do sistema"""

    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CASHIER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    sales = relationship("Sale", back_populates="user")
