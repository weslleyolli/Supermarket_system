"""
Modelos de produto e categoria
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class Category(BaseModel):
    """Categoria de produtos"""

    __tablename__ = "categories"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    products = relationship("Product", back_populates="category")


class Product(BaseModel):
    """Produto"""

    __tablename__ = "products"

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    barcode = Column(String(50), unique=True, index=True, nullable=False)

    # Categoria
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Preços
    price = Column(Float, nullable=False)  # Preço de venda
    cost_price = Column(Float, nullable=False)  # Preço de custo

    # Estoque
    stock_quantity = Column(Float, default=0, nullable=False)
    min_stock_level = Column(Float, default=0, nullable=False)

    # Tipo de produto
    unit_type = Column(
        String(20), default="unidade", nullable=False
    )  # unidade, peso, volume
    requires_weighing = Column(Boolean, default=False, nullable=False)
    tare_weight = Column(Float, default=0)  # Peso da embalagem

    # Promoções
    bulk_discount_enabled = Column(Boolean, default=False, nullable=False)
    bulk_min_quantity = Column(Float, default=10)
    bulk_discount_percentage = Column(Float, default=5.0)

    # ✅ NOVAS COLUNAS PARA ESTOQUE:
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    profit_margin = Column(Float, nullable=True)  # Margem de lucro %
    weight = Column(Float, nullable=True)  # Peso em kg
    dimensions = Column(String(100), nullable=True)  # Dimensões
    location = Column(String(100), nullable=True)  # Localização no estoque
    reorder_point = Column(Integer, nullable=True)  # Ponto de reposição
    max_stock = Column(Integer, nullable=True)  # Estoque máximo
    last_purchase_date = Column(DateTime(timezone=True), nullable=True)
    last_sale_date = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    category = relationship("Category", back_populates="products")
    # supplier = relationship("Supplier", back_populates="products", lazy="select")  # Comentado temporariamente
    sale_items = relationship("SaleItem", back_populates="product")
