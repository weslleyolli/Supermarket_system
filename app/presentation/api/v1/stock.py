from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.application.services.stock_service import StockService
from app.core.deps import get_current_user, get_db
from app.infrastructure.database.models.stock import MovementType
from app.infrastructure.database.models.user import User
from app.presentation.schemas.stock import (
    StockAdjustmentCreate,
    StockAlertResponse,
    StockEntryCreate,
    StockMovementCreate,
    StockMovementResponse,
    StockReportResponse,
    SupplierCreate,
    SupplierResponse,
)

router = APIRouter()

# ==================== MOVIMENTAÇÕES DE ESTOQUE ====================


@router.post("/movements", response_model=StockMovementResponse)
def create_stock_movement(
    movement: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar movimentação de estoque"""
    stock_service = StockService(db)

    try:
        result = stock_service.create_stock_movement(
            product_id=movement.product_id,
            movement_type=movement.movement_type,
            quantity=movement.quantity,
            user_id=current_user.id,
            unit_cost=movement.unit_cost,
            reason=movement.reason,
            notes=movement.notes,
            supplier_id=movement.supplier_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/movements", response_model=List[StockMovementResponse])
def get_stock_movements(
    product_id: Optional[int] = Query(None),
    movement_type: Optional[MovementType] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar movimentações de estoque"""
    stock_service = StockService(db)

    start_datetime = (
        datetime.combine(start_date, datetime.min.time()) if start_date else None
    )
    end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None

    return stock_service.get_stock_movements(
        product_id=product_id,
        movement_type=movement_type,
        start_date=start_datetime,
        end_date=end_datetime,
        skip=skip,
        limit=limit,
    )


# ==================== ENTRADA DE ESTOQUE ====================


@router.post("/entry", response_model=StockMovementResponse)
def stock_entry(
    entry: StockEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Entrada de estoque"""
    stock_service = StockService(db)

    try:
        result = stock_service.stock_entry(
            product_id=entry.product_id,
            quantity=entry.quantity,
            unit_cost=entry.unit_cost,
            user_id=current_user.id,
            supplier_id=entry.supplier_id,
            reason=entry.reason or "Entrada de estoque",
            notes=entry.notes,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== AJUSTE DE ESTOQUE ====================


@router.post("/adjustment", response_model=StockMovementResponse)
def stock_adjustment(
    adjustment: StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ajuste de estoque"""
    stock_service = StockService(db)

    try:
        result = stock_service.stock_adjustment(
            product_id=adjustment.product_id,
            new_quantity=adjustment.new_quantity,
            user_id=current_user.id,
            reason=adjustment.reason or "Ajuste de estoque",
            notes=adjustment.notes,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ALERTAS DE ESTOQUE ====================


@router.get("/alerts", response_model=List[StockAlertResponse])
def get_stock_alerts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Obter alertas de estoque baixo"""
    stock_service = StockService(db)
    return stock_service.get_low_stock_alerts()


# ==================== RELATÓRIOS DE ESTOQUE ====================


@router.get("/report", response_model=StockReportResponse)
def get_stock_report(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Relatório geral de estoque"""
    stock_service = StockService(db)
    return stock_service.get_stock_report()


# ==================== FORNECEDORES ====================


@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar fornecedor"""
    stock_service = StockService(db)

    result = stock_service.create_supplier(
        name=supplier.name,
        company_name=supplier.company_name,
        document=supplier.document,
        email=supplier.email,
        phone=supplier.phone,
        address=supplier.address,
        contact_person=supplier.contact_person,
    )
    return result


@router.get("/suppliers", response_model=List[SupplierResponse])
def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar fornecedores"""
    stock_service = StockService(db)
    return stock_service.get_suppliers(skip=skip, limit=limit)


# ==================== PRODUTOS - GESTÃO DE ESTOQUE ====================


@router.get("/products/low-stock")
def get_products_low_stock(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Produtos com estoque baixo - visão simplificada"""
    stock_service = StockService(db)
    alerts = stock_service.get_low_stock_alerts()

    return {"count": len(alerts), "products": alerts[:10]}  # Top 10 mais críticos


@router.get("/products/{product_id}/movements")
def get_product_movements(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Histórico de movimentações de um produto específico"""
    stock_service = StockService(db)

    movements = stock_service.get_stock_movements(
        product_id=product_id, skip=skip, limit=limit
    )

    return {
        "product_id": product_id,
        "movements": movements,
        "total_movements": len(movements),
    }


# ==================== DASHBOARD DE ESTOQUE ====================


@router.get("/dashboard")
def get_stock_dashboard(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Dashboard completo de estoque"""
    stock_service = StockService(db)

    # Relatório geral
    report = stock_service.get_stock_report()

    # Alertas
    alerts = stock_service.get_low_stock_alerts()

    # Movimentações recentes
    recent_movements = stock_service.get_stock_movements(skip=0, limit=10)

    # Extrair dados do summary
    summary = report["summary"]
    items = report["items"]

    # Filtrar produtos com maior estoque para top_products
    top_products = sorted(items, key=lambda x: x["current_stock"], reverse=True)[:5]

    return {
        "summary": {
            "total_products": summary["total_products"],
            "products_in_stock": summary["total_products"]
            - summary["out_of_stock_items"],
            "products_out_of_stock": summary["out_of_stock_items"],
            "low_stock_alerts": summary["low_stock_items"],
            "total_stock_value": summary["total_stock_value"],
            "stock_turnover": 0.0,  # Será implementado depois
        },
        "alerts": alerts[:5],  # Top 5 alertas mais críticos
        "recent_movements": recent_movements,
        "top_products": top_products,
        "top_selling": [],  # Será implementado depois
    }
