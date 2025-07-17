"""
Dependências compartilhadas do FastAPI
"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.user_repository import UserRepository

security = HTTPBearer()


# Reexporta a função get_db do connection.py
get_db = get_db


async def get_current_user(
    token: str = Depends(security), db: Session = Depends(get_db)
):
    """Obter usuário atual baseado no token JWT"""
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
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    """Verificar se o usuário está ativo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
