import traceback

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import (  # noqa: F401
    Category,
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    Sale,
    StockMovement,
    Supplier,
    User,
)
from app.presentation.api.v1 import api_router

app = FastAPI(
    title="Sistema de Supermercado",
    description="API para gerenciamento de supermercado com autenticação e produtos",
    version="1.0.0",
    debug=True,  # Habilitar modo debug
)


# Exception handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para capturar exceções não tratadas"""
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "traceback": traceback.format_exc(),
    }
    print(f"❌ Erro não tratado: {error_detail}")
    return JSONResponse(status_code=500, content=error_detail)


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

        # 🔍 MELHORAR: Buscar produtos com estoque baixo e seus detalhes
        low_stock_products = (
            db.query(Product)
            .filter(
                Product.is_active, Product.stock_quantity <= Product.min_stock_level
            )
            .all()
        )

        # 📋 Criar lista detalhada dos produtos com estoque baixo
        low_stock_details = []
        for product in low_stock_products:
            low_stock_details.append(
                {
                    "name": product.name,
                    "current_stock": float(product.stock_quantity),
                    "min_level": float(product.min_stock_level),
                    "difference": float(
                        product.min_stock_level - product.stock_quantity
                    ),
                    "urgency": "critical" if product.stock_quantity <= 0 else "warning",
                }
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
                "low_stock_products": len(low_stock_products),
            },
            "alerts": {
                "low_stock": len(low_stock_products) > 0,
                "low_stock_details": low_stock_details,  # 👈 NOVO: Detalhes dos produtos
            },
            "pdv_status": {
                "barcode_reader": "ready",
                "scale": "ready",
                "printer": "ready",
            },
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
