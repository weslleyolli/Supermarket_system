from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models.user import User
from app.presentation.api.v1.auth import router as auth_router

app = FastAPI(
    title="Sistema de Supermercado",
    description="API para gerenciamento de supermercado com autenticação",
    version="1.0.0",
)

# Incluir router de autenticação
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "API do Supermercado funcionando!"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check - verifica se API e banco estão funcionando"""
    try:
        users_count = db.query(User).count()

        return {
            "status": "healthy",
            "database": "connected",
            "features": {
                "authentication": "✅ Enabled",
                "jwt_tokens": "✅ Enabled",
                "role_permissions": "✅ Enabled",
                "password_hash": "✅ BCrypt",
            },
            "counts": {"users": users_count},
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
