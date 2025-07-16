"""
Endpoints de gestão de vendas
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.services.sale_service import SaleService
from app.infrastructure.database.connection import get_db
from app.presentation.api.dependencies import (
    get_current_active_user,
    require_supervisor,
)
from app.presentation.schemas.auth import UserResponse
from app.presentation.schemas.sale import SaleResponse, SaleSummary

router = APIRouter(prefix="/sales", tags=["Vendas"])


def get_sale_service(db: Session = Depends(get_db)) -> SaleService:
    return SaleService(db)


@router.get("/", response_model=List[SaleSummary])
async def list_sales(
    start_date: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    user_id: Optional[int] = Query(None, description="ID do usuário/operador"),
    status: Optional[str] = Query(None, description="Status da venda"),
    skip: int = Query(0, ge=0, description="Pular registros"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    sale_service: SaleService = Depends(get_sale_service),
    _: UserResponse = Depends(get_current_active_user),
):
    return sale_service.list_sales(
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    sale_service: SaleService = Depends(get_sale_service),
    _: UserResponse = Depends(get_current_active_user),
):
    sale = sale_service.get_sale(sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Venda não encontrada"
        )
    return sale


@router.post("/{sale_id}/cancel")
async def cancel_sale(
    sale_id: int,
    current_user: UserResponse = Depends(require_supervisor),
    sale_service: SaleService = Depends(get_sale_service),
):
    success = sale_service.cancel_sale(sale_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível cancelar a venda",
        )
    return {"message": "Venda cancelada com sucesso"}


@router.get("/summary/period")
async def get_sales_summary(
    start_date: date = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data final (YYYY-MM-DD)"),
    sale_service: SaleService = Depends(get_sale_service),
    _: UserResponse = Depends(get_current_active_user),
):
    summary = sale_service.sale_repo.get_sales_summary(start_date, end_date)
    return summary
