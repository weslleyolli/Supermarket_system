"""
API v1 - Módulo de rotas da versão 1 da API
"""

from fastapi import APIRouter

from app.presentation.api.v1 import auth, pdv, products, reports, sales

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(sales.router)
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(pdv.router, prefix="/pdv", tags=["PDV"])
