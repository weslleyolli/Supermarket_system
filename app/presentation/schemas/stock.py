"""
Schemas para sistema de estoque
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# ==================== ENUMS ====================


class MovementTypeEnum(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"
    PERDA = "perda"
    DEVOLUCAO = "devolucao"
    TRANSFERENCIA = "transferencia"


class AlertLevelEnum(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"


# ==================== FORNECEDORES ====================


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    document: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=255)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    document: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== MOVIMENTAÇÕES DE ESTOQUE ====================
class StockMovementBase(BaseModel):
    product_id: int
    movement_type: MovementTypeEnum
    quantity: int
    unit_cost: Optional[Decimal] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    supplier_id: Optional[int] = None


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementResponse(StockMovementBase):
    id: int
    previous_quantity: int
    new_quantity: int
    total_cost: Optional[Decimal] = None
    user_id: int
    sale_id: Optional[int] = None
    created_at: datetime

    # Relacionamentos
    product_name: Optional[str] = None
    user_name: Optional[str] = None
    supplier_name: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== ENTRADA DE ESTOQUE ====================


class StockEntryCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantidade deve ser maior que 0")
    unit_cost: Decimal = Field(
        ..., gt=0, description="Custo unitário deve ser maior que 0"
    )
    supplier_id: Optional[int] = None
    reason: Optional[str] = "Entrada de estoque"
    notes: Optional[str] = None


# ==================== AJUSTE DE ESTOQUE ====================


class StockAdjustmentCreate(BaseModel):
    product_id: int
    new_quantity: int = Field(..., ge=0, description="Nova quantidade deve ser >= 0")
    reason: Optional[str] = "Ajuste de estoque"
    notes: Optional[str] = None


# =================== PURCHASE ORDER SCHEMAS ===================
class PurchaseOrderItemBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity_ordered: int = Field(..., gt=0)
    unit_cost: Decimal = Field(..., gt=0)


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    id: int
    quantity_received: int = 0
    total_cost: Decimal

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    supplier_id: int = Field(..., gt=0)
    order_number: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = None
    expected_delivery: Optional[datetime] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate] = Field(..., min_items=1)


class PurchaseOrderUpdate(BaseModel):
    status: Optional[str] = Field(
        None, pattern="^(pending|confirmed|delivered|cancelled)$"
    )
    notes: Optional[str] = None
    expected_delivery: Optional[datetime] = None
    delivery_date: Optional[datetime] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    status: str
    total_amount: Decimal
    user_id: int
    order_date: datetime
    delivery_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PurchaseOrderItemResponse] = []

    class Config:
        from_attributes = True


# =================== STOCK REPORT SCHEMAS ===================
class StockReportItem(BaseModel):
    product_id: int
    product_name: str
    barcode: Optional[str]
    category_name: str
    supplier_name: Optional[str]
    current_stock: int
    min_stock: int
    max_stock: Optional[int]
    reorder_point: Optional[int]
    cost_price: Optional[Decimal]
    sale_price: Decimal
    stock_value: Decimal
    location: Optional[str]
    last_movement_date: Optional[datetime]
    movement_count: int
    status: str  # "ok", "low_stock", "out_of_stock", "overstock"


class StockSummary(BaseModel):
    total_products: int
    total_stock_value: Decimal
    low_stock_items: int
    out_of_stock_items: int
    overstocked_items: int
    total_movements_today: int
    total_movements_week: int


class StockReportResponse(BaseModel):
    summary: StockSummary
    items: List[StockReportItem]
    generated_at: datetime


# =================== STOCK ALERT SCHEMAS ===================
class StockAlertResponse(BaseModel):
    product_id: int
    product_name: str
    current_quantity: int
    min_stock: int
    reorder_point: Optional[int] = None
    alert_level: AlertLevelEnum
    days_without_stock: Optional[int] = None

    class Config:
        from_attributes = True


# =================== STOCK ENTRY SCHEMAS (ORIGINAL) ===================
class StockEntryCreateOriginal(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_cost: Decimal = Field(..., gt=0)
    supplier_id: Optional[int] = Field(None, gt=0)
    reason: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


# =================== STOCK ADJUSTMENT SCHEMAS (ORIGINAL) ===================
class StockAdjustmentRequest(BaseModel):
    new_quantity: int = Field(..., ge=0)
    reason: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None
    unit_cost: Optional[Decimal] = Field(None, gt=0)


class StockAdjustmentResponse(BaseModel):
    message: str
    movement: StockMovementResponse


class StockAdjustmentCreateOriginal(BaseModel):
    product_id: int = Field(..., gt=0)
    new_quantity: int = Field(..., ge=0)
    reason: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


# ==================== RELATÓRIOS ====================


class ProductStockSummary(BaseModel):
    name: str
    quantity: int
    value: float


class TopSellingProduct(BaseModel):
    name: str
    quantity_sold: int


class StockReportResponseNew(BaseModel):
    total_products: int
    products_in_stock: int
    products_out_of_stock: int
    low_stock_alerts: int
    total_stock_value: float
    stock_turnover: float
    top_products_by_quantity: List[ProductStockSummary]
    top_selling_products: List[TopSellingProduct]


# ==================== DASHBOARD ====================


class StockSummaryNew(BaseModel):
    total_products: int
    products_in_stock: int
    products_out_of_stock: int
    low_stock_alerts: int
    total_stock_value: float
    stock_turnover: float


class StockDashboardResponse(BaseModel):
    summary: StockSummaryNew
    alerts: List[StockAlertResponse]
    recent_movements: List[StockMovementResponse]
    top_products: List[ProductStockSummary]
    top_selling: List[TopSellingProduct]


# ==================== PRODUTOS EXTENDIDOS ====================


class ProductStockBase(BaseModel):
    name: str
    description: Optional[str] = None
    barcode: str
    price: Decimal
    quantity: int
    min_stock: int
    category_id: int
    supplier_id: Optional[int] = None
    cost_price: Optional[Decimal] = None
    profit_margin: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    location: Optional[str] = None
    reorder_point: Optional[int] = None
    max_stock: Optional[int] = None


class ProductStockCreate(ProductStockBase):
    pass


class ProductStockResponse(ProductStockBase):
    id: int
    is_active: bool
    created_at: datetime
    last_purchase_date: Optional[datetime] = None
    last_sale_date: Optional[datetime] = None

    # Campos calculados
    stock_status: Optional[str] = None  # "ok", "low", "critical", "out"
    days_until_stockout: Optional[int] = None
    category_name: Optional[str] = None
    supplier_name: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== FILTROS E CONSULTAS ====================


class StockMovementFilter(BaseModel):
    product_id: Optional[int] = None
    movement_type: Optional[MovementTypeEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[int] = None
    supplier_id: Optional[int] = None


class ProductStockFilter(BaseModel):
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    stock_status: Optional[str] = None  # "ok", "low", "critical", "out"
    search: Optional[str] = None


# ==================== VALIDAÇÕES CUSTOMIZADAS ====================


class BulkStockOperation(BaseModel):
    """Para operações em lote no estoque"""

    operations: List[StockMovementCreate] = Field(..., min_items=1, max_items=100)

    class Config:
        json_schema_extra = {
            "example": {
                "operations": [
                    {
                        "product_id": 1,
                        "movement_type": "entrada",
                        "quantity": 50,
                        "unit_cost": 10.50,
                        "reason": "Reposição de estoque",
                        "supplier_id": 1,
                    },
                    {
                        "product_id": 2,
                        "movement_type": "ajuste",
                        "quantity": 25,
                        "reason": "Ajuste por inventário",
                    },
                ]
            }
        }
