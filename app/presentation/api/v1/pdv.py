"""
Endpoints do PDV (Ponto de Venda)
"""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.services.sale_service import SaleService
from app.infrastructure.database.connection import get_db
from app.presentation.api.dependencies import get_current_active_user
from app.presentation.schemas.auth import UserResponse
from app.presentation.schemas.sale import (
    BarcodeInput,
    Cart,
    CartOperation,
    PaymentRequest,
    PaymentResponse,
)

router = APIRouter(prefix="/pdv", tags=["PDV - Ponto de Venda"])


def get_sale_service(db: Session = Depends(get_db)) -> SaleService:
    # Função modificada para receber user_id dinamicamente
    from fastapi import Request

    def _service(
        request: Request, current_user: UserResponse = Depends(get_current_active_user)
    ):
        return SaleService(db, user_id=current_user.id)

    return _service


@router.post("/add-product")
async def add_product_to_cart(
    barcode_input: BarcodeInput,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user),
):
    try:
        sale_service = SaleService(db, user_id=current_user.id)
        result = sale_service.add_product_by_barcode(barcode_input)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/cart", response_model=Cart)
async def get_current_cart(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user),
):
    sale_service = SaleService(db, user_id=current_user.id)
    return sale_service.get_current_cart()


@router.post("/cart/update", response_model=Cart)
async def update_cart(
    operation: CartOperation,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user),
):
    try:
        sale_service = SaleService(db, user_id=current_user.id)
        return sale_service.update_cart_item(operation)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/payment", response_model=PaymentResponse)
async def process_payment(
    payment_request: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user),
):
    try:
        sale_service = SaleService(db, user_id=current_user.id)
        return sale_service.process_payment(payment_request, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
