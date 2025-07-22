"""
Modelos de estoque, fornecedores e movimentações
"""

from enum import Enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


class MovementType(str, Enum):
    """Tipos de movimentação de estoque"""

    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"
    PERDA = "perda"
    DEVOLUCAO = "devolucao"
    TRANSFERENCIA = "transferencia"


class Supplier(BaseModel):
    """Fornecedores"""

    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    document = Column(String(20), unique=True, nullable=True)  # CNPJ
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    contact_person = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    # products = relationship("Product", back_populates="supplier", lazy="select")  # Comentado temporariamente
    stock_movements = relationship("StockMovement", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


class StockMovement(BaseModel):
    """Movimentações de estoque"""

    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    movement_type = Column(SQLEnum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)  # Quantidade anterior
    new_quantity = Column(Integer, nullable=False)  # Nova quantidade
    unit_cost = Column(Numeric(10, 2), nullable=True)  # Custo unitário (para entradas)
    total_cost = Column(Numeric(10, 2), nullable=True)  # Custo total
    reason = Column(String(255), nullable=True)  # Motivo da movimentação
    notes = Column(Text, nullable=True)  # Observações
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True)  # Se foi venda
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # NOTA: Tabela não tem updated_at - por isso não incluímos

    # Relacionamentos
    supplier = relationship("Supplier", back_populates="stock_movements")
    # Remover relacionamento com Product temporariamente para evitar dependência circular


class PurchaseOrder(BaseModel):
    """Pedidos de compra"""

    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    status = Column(
        String(20), default="pending"
    )  # pending, confirmed, delivered, cancelled
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    expected_delivery = Column(DateTime(timezone=True), nullable=True)
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")


class PurchaseOrderItem(BaseModel):
    """Itens do pedido de compra"""

    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(
        Integer, ForeignKey("purchase_orders.id"), nullable=False
    )
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, default=0)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    total_cost = Column(Numeric(10, 2), nullable=False)

    # Relacionamentos
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    # Remover relacionamento com Product temporariamente para evitar dependência circular
