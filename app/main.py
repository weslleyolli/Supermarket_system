from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import (  # noqa: F401
    Category,
    Product,
    Sale,
    User,
)
from app.presentation.api.v1 import api_router

app = FastAPI(
    title="Sistema de Supermercado",
    description="API para gerenciamento de supermercado com autenticação e produtos",
    version="1.0.0",
)

# 🔧 ADICIONAR CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",  # 👈 ADICIONAR esta linha!
    ],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 👈 INCLUIR OPTIONS!
    allow_headers=["*"],
)

# Incluir apenas o router central da v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "API do Supermercado funcionando!"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check completo com PDV"""
    try:
        from app.infrastructure.database.models import Category, Product, Sale, User

        users_count = db.query(User).count()
        products_count = db.query(Product).filter(Product.is_active).count()
        categories_count = db.query(Category).filter(Category.is_active).count()
        sales_count = db.query(Sale).count()
        low_stock_count = (
            db.query(Product)
            .filter(
                Product.is_active, Product.stock_quantity <= Product.min_stock_level
            )
            .count()
        )
        return {
            "status": "healthy",
            "database": "connected",
            "features": {
                "authentication": "✅ Enabled",
                "products": "✅ Enabled",
                "categories": "✅ Enabled",
                "pdv": "✅ Enabled",
                "sales": "✅ Enabled",
                "barcode_reader": "✅ Simulation",
                "scale": "✅ Simulation",
                "thermal_printer": "✅ Simulation",
                "bulk_promotions": "✅ Enabled",
                "stock_control": "✅ Enabled",
            },
            "counts": {
                "users": users_count,
                "products": products_count,
                "categories": categories_count,
                "sales": sales_count,
                "low_stock_products": low_stock_count,
            },
            "alerts": {"low_stock": low_stock_count > 0},
            "pdv_status": {
                "barcode_reader": "ready",
                "scale": "ready",
                "printer": "ready",
            },
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
