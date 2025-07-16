"""
Dependências para as rotas da API
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.core.security import ALGORITHM, SECRET_KEY
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models.user import User
from app.infrastructure.repositories.user_repository import UserRepository


def get_database_session():
    """Dependência para obter sessão do banco de dados"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


def get_user_repository(db: Session = None):
    """Dependência para obter repositório de usuários"""
    if db is None:
        db = next(get_db())
    return UserRepository(db)


def get_auth_service(db: Session = None):
    """Dependência para obter serviço de autenticação"""
    user_repo = get_user_repository(db)
    return AuthService(user_repo)


security = HTTPBearer()


def get_current_active_user(
    token: str = Depends(security), db: Session = Depends(get_database_session)
):
    """Dependência para obter usuário atual via JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = get_user_repository(db)
    user = user_repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_active_user)):
    """Dependência para verificar se o usuário atual é administrador"""
    from app.infrastructure.database.models.user import UserRole

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges required",
        )
    return current_user


def require_supervisor(current_user: User = Depends(get_current_active_user)):
    """Dependência para verificar se o usuário atual é supervisor ou admin"""
    from app.infrastructure.database.models.user import UserRole

    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Supervisor or Admin privileges required",
        )
    return current_user
