"""
Modelos de venda
"""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class PaymentMethod(str, enum.Enum):
    """Métodos de pagamento"""

    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    PIX = "pix"


class SaleStatus(str, enum.Enum):
    """Status da venda"""

    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Sale(BaseModel):
    """Venda"""

    __tablename__ = "sales"

    # Cliente (opcional)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)

    # Funcionário responsável
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Valores
    subtotal_amount = Column(Float, default=0, nullable=False)
    discount_amount = Column(Float, default=0, nullable=False)
    bulk_discount_amount = Column(Float, default=0, nullable=False)
    final_amount = Column(Float, default=0, nullable=False)

    # Pagamento
    payment_method = Column(Enum(PaymentMethod), nullable=False)

    # Status
    status = Column(Enum(SaleStatus), default=SaleStatus.PENDING, nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )


class SaleItem(BaseModel):
    """Item de venda"""

    __tablename__ = "sale_items"

    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Float, nullable=False)
    weight = Column(Float, nullable=True)  # Para produtos por peso

    unit_price = Column(Float, nullable=False)
    original_total_price = Column(Float, nullable=False)
    discount_applied = Column(Float, default=0, nullable=False)
    bulk_discount_applied = Column(Float, default=0, nullable=False)
    final_total_price = Column(Float, nullable=False)

    # Relacionamentos
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
