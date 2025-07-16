"""
Schemas para produtos e categorias
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.infrastructure.database.models.product import Product as ProductModel


class CategoryBase(BaseModel):
    """Schema base de categoria"""

    name: str = Field(
        ..., min_length=2, max_length=100, description="Nome da categoria"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Descrição da categoria"
    )
    is_active: bool = Field(True, description="Categoria ativa")


class CategoryCreate(CategoryBase):
    """Schema para criação de categoria"""

    pass


class CategoryUpdate(BaseModel):
    """Schema para atualização de categoria"""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema de resposta de categoria"""

    id: int
    created_at: datetime
    updated_at: datetime
    products_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Schema base de produto"""

    name: str = Field(..., min_length=2, max_length=200, description="Nome do produto")
    description: Optional[str] = Field(
        None, max_length=1000, description="Descrição detalhada"
    )
    barcode: str = Field(
        ..., min_length=8, max_length=50, description="Código de barras"
    )
    category_id: int = Field(..., gt=0, description="ID da categoria")

    # Preços
    price: float = Field(..., gt=0, description="Preço de venda")
    cost_price: float = Field(..., gt=0, description="Preço de custo")

    # Estoque
    stock_quantity: float = Field(0, ge=0, description="Quantidade em estoque")
    min_stock_level: float = Field(0, ge=0, description="Estoque mínimo")

    # Tipo de produto
    unit_type: str = Field(
        "unidade", description="Tipo de unidade (unidade, peso, volume)"
    )
    requires_weighing: bool = Field(False, description="Produto requer pesagem")
    tare_weight: float = Field(0, ge=0, description="Peso da embalagem")

    # Promoções
    bulk_discount_enabled: bool = Field(
        False, description="Desconto por quantidade habilitado"
    )
    bulk_min_quantity: float = Field(
        10, gt=0, description="Quantidade mínima para desconto"
    )
    bulk_discount_percentage: float = Field(
        5.0, ge=0, le=100, description="Percentual de desconto"
    )

    # Status
    is_active: bool = Field(True, description="Produto ativo")

    @validator("unit_type")
    def validate_unit_type(cls, v):
        allowed_types = ["unidade", "peso", "volume"]
        if v not in allowed_types:
            raise ValueError(f"Tipo deve ser um de: {allowed_types}")
        return v

    @validator("barcode")
    def validate_barcode(cls, v):
        # Remover espaços e verificar se é numérico
        v = v.strip().replace(" ", "")
        if not v.isdigit():
            raise ValueError("Código de barras deve conter apenas números")

        # Verificar comprimento para EAN-13, EAN-8, UPC-A
        valid_lengths = [8, 12, 13, 14]
        if len(v) not in valid_lengths:
            raise ValueError(f"Código de barras deve ter {valid_lengths} dígitos")

        return v

    @validator("price")
    def validate_price(cls, v, values):
        cost_price = values.get("cost_price", 0)
        if cost_price > 0 and v < cost_price:
            raise ValueError("Preço de venda não pode ser menor que o preço de custo")
        return v


class ProductCreate(ProductBase):
    """Schema para criação de produto"""

    pass


class ProductUpdate(BaseModel):
    """Schema para atualização de produto"""

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    barcode: Optional[str] = Field(None, min_length=8, max_length=50)
    category_id: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[float] = Field(None, ge=0)
    min_stock_level: Optional[float] = Field(None, ge=0)
    unit_type: Optional[str] = None
    requires_weighing: Optional[bool] = None
    tare_weight: Optional[float] = Field(None, ge=0)
    bulk_discount_enabled: Optional[bool] = None
    bulk_min_quantity: Optional[float] = Field(None, gt=0)
    bulk_discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema de resposta de produto"""

    id: int
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse

    # Campos calculados
    profit_margin: float = Field(0, description="Margem de lucro (%)")
    stock_status: str = Field("", description="Status do estoque")
    has_promotion: bool = Field(False, description="Tem promoção ativa")

    class Config:
        from_attributes = True


class ProductSummary(BaseModel):
    """Resumo do produto para listagens"""

    id: int
    name: str
    barcode: str
    price: float
    stock_quantity: float
    category_name: str
    is_active: bool
    stock_status: str


class BarcodeSearch(BaseModel):
    """Schema para busca por código de barras"""

    barcode: str


class StockAdjustment(BaseModel):
    """Schema para ajuste de estoque"""

    product_id: int
    quantity_change: float = Field(
        ..., description="Quantidade a adicionar/remover (negativo para remoção)"
    )
    reason: str = Field(
        ..., min_length=5, max_length=200, description="Motivo do ajuste"
    )


class BulkPriceUpdate(BaseModel):
    """Schema para atualização de preços em lote"""

    category_id: Optional[int] = None
    price_change_percentage: float = Field(
        ..., ge=-50, le=100, description="Percentual de mudança no preço"
    )
    apply_to_cost_price: bool = Field(
        False, description="Aplicar também ao preço de custo"
    )
