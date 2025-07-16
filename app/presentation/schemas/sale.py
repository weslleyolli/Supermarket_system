"""
Schemas para vendas e PDV
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.infrastructure.database.models.sale import PaymentMethod, SaleStatus


class SaleItemBase(BaseModel):
    product_id: int = Field(..., gt=0, description="ID do produto")
    quantity: float = Field(..., gt=0, description="Quantidade")
    weight: Optional[float] = Field(
        None, ge=0, description="Peso (para produtos por peso)"
    )


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemResponse(SaleItemBase):
    id: int
    unit_price: float
    original_total_price: float
    discount_applied: float = 0
    bulk_discount_applied: float = 0
    final_total_price: float
    product_name: str
    product_barcode: str

    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    customer_id: Optional[int] = Field(None, description="ID do cliente (opcional)")
    payment_method: PaymentMethod = Field(..., description="Método de pagamento")


class SaleCreate(SaleBase):
    items: List[SaleItemCreate] = Field(..., min_items=1, description="Itens da venda")

    @validator("items")
    def validate_items(cls, v):
        if not v:
            raise ValueError("Venda deve ter pelo menos um item")
        return v


class SaleUpdate(BaseModel):
    status: Optional[SaleStatus] = None
    customer_id: Optional[int] = None


class SaleResponse(SaleBase):
    id: int
    user_id: int
    subtotal_amount: float
    discount_amount: float
    bulk_discount_amount: float
    final_amount: float
    status: SaleStatus
    created_at: datetime
    items: List[SaleItemResponse]
    total_items: int = 0
    total_quantity: float = 0
    total_savings: float = 0

    class Config:
        from_attributes = True


class SaleSummary(BaseModel):
    id: int
    final_amount: float
    payment_method: PaymentMethod
    status: SaleStatus
    total_items: int
    created_at: datetime
    cashier_name: str


class BarcodeInput(BaseModel):
    barcode: str = Field(..., min_length=8, max_length=50)
    quantity: float = Field(1.0, gt=0, description="Quantidade padrão")
    weight: Optional[float] = Field(
        None, ge=0, description="Peso (se produto por peso)"
    )


class CartItem(BaseModel):
    product_id: int
    product_name: str
    product_barcode: str
    unit_price: float
    quantity: float
    weight: Optional[float] = None
    requires_weighing: bool
    original_total: float
    discount_applied: float = 0
    bulk_discount_applied: float = 0
    final_total: float
    has_promotion: bool = False
    promotion_description: str = ""


class Cart(BaseModel):
    items: List[CartItem] = []
    subtotal: float = 0
    total_discount: float = 0
    bulk_discount: float = 0
    final_total: float = 0
    total_items: int = 0
    total_quantity: float = 0


class CartOperation(BaseModel):
    operation: str = Field(..., description="add, remove, update, clear")
    product_id: Optional[int] = None
    quantity: Optional[float] = None
    weight: Optional[float] = None


class PaymentRequest(BaseModel):
    payment_method: PaymentMethod
    amount_received: float = Field(..., gt=0, description="Valor recebido")
    customer_id: Optional[int] = None


class PaymentResponse(BaseModel):
    sale_id: int
    final_amount: float
    amount_received: float
    change_amount: float
    payment_method: PaymentMethod
    receipt_data: dict
