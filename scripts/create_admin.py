# =============================================================================
# SISTEMA DE AUTENTICAÇÃO COMPLETO
# Sistema de Gestão de Supermercado
# =============================================================================

# -----------------------------------------------------------------------------
# 1. SEGURANÇA E CRIPTOGRAFIA - app/core/security.py
# -----------------------------------------------------------------------------

"""
Módulo de segurança - JWT, hash de senhas e autenticação
"""

from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Configuração do hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT de acesso"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# Exceções de autenticação
class AuthenticationError(HTTPException):
    """Erro de autenticação"""

    def __init__(self, detail: str = "Credenciais inválidas"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionError(HTTPException):
    """Erro de permissão"""

    def __init__(self, detail: str = "Permissão insuficiente"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


# -----------------------------------------------------------------------------
# 2. ESQUEMAS PYDANTIC - app/presentation/schemas/auth.py
# -----------------------------------------------------------------------------

"""
Schemas para autenticação
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from app.infrastructure.database.models.user import UserRole


class UserBase(BaseModel):
    """Schema base do usuário"""

    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.CASHIER
    is_active: bool = True


class UserCreate(UserBase):
    """Schema para criação de usuário"""

    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter pelo menos um número")
        if not any(c.isalpha() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra")
        return v

    @validator("username")
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username deve ter pelo menos 3 caracteres")
        if not v.isalnum():
            raise ValueError("Username deve conter apenas letras e números")
        return v.lower()


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema de resposta do usuário"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema para login"""

    username: str
    password: str


class Token(BaseModel):
    """Schema do token de acesso"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema dos dados do token"""

    username: Optional[str] = None
    user_id: Optional[int] = None


class ChangePassword(BaseModel):
    """Schema para mudança de senha"""

    current_password: str
    new_password: str

    @validator("new_password")
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Nova senha deve ter pelo menos 8 caracteres")
        return v


# -----------------------------------------------------------------------------
# 3. REPOSITÓRIO DE USUÁRIOS - app/infrastructure/repositories/user_repository.py
# -----------------------------------------------------------------------------

"""
Repositório de usuários
"""

from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.infrastructure.database.models.user import User
from app.presentation.schemas.auth import UserCreate, UserUpdate


class UserRepository:
    """Repositório para operações com usuários"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Busca usuário por username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista todos os usuários"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, user_data: UserCreate) -> User:
        """Cria novo usuário"""
        # Verificar se username já existe
        if self.get_by_username(user_data.username):
            raise ValueError("Username já existe")

        # Verificar se email já existe
        if self.get_by_email(user_data.email):
            raise ValueError("Email já existe")

        # Criar usuário
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
            is_active=user_data.is_active,
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Erro ao criar usuário - dados duplicados")

    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Atualiza usuário"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Erro ao atualizar usuário")

    def delete(self, user_id: int) -> bool:
        """Remove usuário (soft delete)"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False

        db_user.is_active = False
        self.db.commit()
        return True

    def change_password(self, user_id: int, new_password: str) -> bool:
        """Altera senha do usuário"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False

        db_user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        return True


# -----------------------------------------------------------------------------
# 4. SERVIÇO DE AUTENTICAÇÃO - app/application/services/auth_service.py
# -----------------------------------------------------------------------------

"""
Serviço de autenticação
"""

from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import AuthenticationError, create_access_token, verify_password
from app.infrastructure.repositories.user_repository import UserRepository
from app.presentation.schemas.auth import ChangePassword, Token, UserLogin, UserResponse


class AuthService:
    """Serviço de autenticação"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate_user(self, username: str, password: str) -> Optional[UserResponse]:
        """Autentica usuário"""
        user = self.user_repo.get_by_username(username)

        if not user:
            return None

        if not user.is_active:
            raise AuthenticationError("Usuário inativo")

        if not verify_password(password, user.hashed_password):
            return None

        return UserResponse.model_validate(user)

    def login(self, login_data: UserLogin) -> Token:
        """Realiza login e retorna token"""
        user = self.authenticate_user(login_data.username, login_data.password)

        if not user:
            raise AuthenticationError("Username ou senha incorretos")

        # Criar token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires,
        )

        return Token(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user,
        )

    def get_current_user(self, token: str) -> UserResponse:
        """Obtém usuário atual do token"""
        from app.core.security import verify_token

        payload = verify_token(token)
        if payload is None:
            raise AuthenticationError("Token inválido")

        username: str = payload.get("sub")
        if username is None:
            raise AuthenticationError("Token inválido")

        user = self.user_repo.get_by_username(username)
        if user is None:
            raise AuthenticationError("Usuário não encontrado")

        if not user.is_active:
            raise AuthenticationError("Usuário inativo")

        return UserResponse.model_validate(user)

    def change_password(self, user_id: int, password_data: ChangePassword) -> bool:
        """Altera senha do usuário"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("Usuário não encontrado")

        # Verificar senha atual
        if not verify_password(password_data.current_password, user.hashed_password):
            raise AuthenticationError("Senha atual incorreta")

        # Alterar senha
        return self.user_repo.change_password(user_id, password_data.new_password)


# -----------------------------------------------------------------------------
# 5. DEPENDENCIES - app/presentation/api/dependencies.py
# -----------------------------------------------------------------------------

"""
Dependencies para autenticação e autorização
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.core.security import PermissionError
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models.user import UserRole
from app.presentation.schemas.auth import UserResponse

# Security scheme
security = HTTPBearer()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency para obter serviço de autenticação"""
    return AuthService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Dependency para obter usuário atual"""
    return auth_service.get_current_user(credentials.credentials)


def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Dependency para usuário ativo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo"
        )
    return current_user


# Permissões por role
def require_role(required_role: UserRole):
    """Factory para criar dependency de role"""

    def role_dependency(
        current_user: UserResponse = Depends(get_current_active_user),
    ) -> UserResponse:
        role_hierarchy = {
            UserRole.ADMIN: 4,
            UserRole.MANAGER: 3,
            UserRole.SUPERVISOR: 2,
            UserRole.CASHIER: 1,
        }

        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        if user_level < required_level:
            raise PermissionError(f"Requer permissão de {required_role.value}")

        return current_user

    return role_dependency


# Aliases para facilitar uso
require_admin = require_role(UserRole.ADMIN)
require_manager = require_role(UserRole.MANAGER)
require_supervisor = require_role(UserRole.SUPERVISOR)

# -----------------------------------------------------------------------------
# 6. ENDPOINTS DE AUTENTICAÇÃO - app/presentation/api/v1/auth.py
# -----------------------------------------------------------------------------

"""
Endpoints de autenticação
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.presentation.api.dependencies import (
    get_current_active_user,
    require_admin,
    require_manager,
)
from app.presentation.schemas.auth import (
    ChangePassword,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login de usuário

    - **username**: Nome de usuário
    - **password**: Senha

    Retorna token JWT para autenticação
    """
    auth_service = AuthService(db)
    return auth_service.login(login_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user),
):
    """
    Obtém informações do usuário atual
    """
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Altera senha do usuário atual
    """
    auth_service = AuthService(db)
    success = auth_service.change_password(current_user.id, password_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao alterar senha"
        )

    return {"message": "Senha alterada com sucesso"}


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _: UserResponse = Depends(require_manager),  # Só manager+ pode criar usuários
):
    """
    Cria novo usuário (apenas managers e admins)
    """
    user_repo = UserRepository(db)

    try:
        user = user_repo.create(user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: UserResponse = Depends(require_manager),
):
    """
    Lista usuários (apenas managers e admins)
    """
    user_repo = UserRepository(db)
    users = user_repo.get_all(skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    _: UserResponse = Depends(require_admin),  # Só admin pode editar usuários
):
    """
    Atualiza usuário (apenas admins)
    """
    user_repo = UserRepository(db)

    try:
        user = user_repo.update(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_admin),
):
    """
    Remove usuário (apenas admins)
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover seu próprio usuário",
        )

    user_repo = UserRepository(db)
    success = user_repo.delete(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    return {"message": "Usuário removido com sucesso"}


# -----------------------------------------------------------------------------
# 7. SCRIPT DE INICIALIZAÇÃO - scripts/create_admin.py
# -----------------------------------------------------------------------------

"""
Script para criar usuário administrador inicial
"""

import asyncio
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.repositories.user_repository import UserRepository
from app.presentation.schemas.auth import UserCreate


def create_admin_user():
    """Cria usuário administrador inicial"""
    db: Session = SessionLocal()
    user_repo = UserRepository(db)

    try:
        # Verificar se já existe admin
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"✅ Admin já existe: {existing_admin.username}")
            return

        # Criar admin
        admin_data = UserCreate(
            username="admin",
            email="admin@supermercado.com",
            full_name="Administrador do Sistema",
            password="admin123",
            role=UserRole.ADMIN,
        )

        admin_user = user_repo.create(admin_data)
        print(f"✅ Usuário admin criado com sucesso!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role.value}")
        print(f"   ID: {admin_user.id}")

    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()

# -----------------------------------------------------------------------------
# 8. ATUALIZAÇÃO DO MAIN.PY - app/main.py
# -----------------------------------------------------------------------------

"""
Atualizar main.py para incluir rotas de autenticação
"""

# Adicionar estas linhas ao app/main.py existente:

# from app.presentation.api.v1.auth import router as auth_router

# Incluir router de autenticação
# app.include_router(auth_router, prefix="/api/v1")

# Atualizar endpoint de health check para mostrar autenticação
# @app.get("/health")
# async def health_check(db: Session = Depends(get_db)):
#     """Health check - verifica se API e banco estão funcionando"""
#     try:
#         users_count = db.query(User).count()
#         products_count = db.query(Product).count()
#         categories_count = db.query(Category).count()
#
#         return {
#             "status": "healthy",
#             "database": "connected",
#             "features": {
#                 "authentication": "✅ Enabled",
#                 "jwt_tokens": "✅ Enabled",
#                 "role_permissions": "✅ Enabled",
#                 "password_hash": "✅ BCrypt"
#             },
#             "counts": {
#                 "users": users_count,
#                 "products": products_count,
#                 "categories": categories_count
#             }
#         }
#     except Exception as e:
#         return {
#             "status": "unhealthy",
#             "database": "disconnected",
#             "error": str(e)
#         }

print(
    """
🔐 SISTEMA DE AUTENTICAÇÃO IMPLEMENTADO!

📁 Arquivos criados:
   ✅ app/core/security.py - Hash e JWT
   ✅ app/presentation/schemas/auth.py - Schemas
   ✅ app/infrastructure/repositories/user_repository.py - Repositório
   ✅ app/application/services/auth_service.py - Serviços
   ✅ app/presentation/api/dependencies.py - Dependencies
   ✅ app/presentation/api/v1/auth.py - Endpoints
   ✅ scripts/create_admin.py - Admin inicial

🚀 COMO TESTAR:
   1. pip install python-jose[cryptography] passlib[bcrypt]
   2. python scripts/create_admin.py
   3. uvicorn app.main:app --reload
   4. Acessar: http://localhost:8000/docs

🔑 LOGIN PADRÃO:
   Username: admin
   Password: admin123

📚 ENDPOINTS DISPONÍVEIS:
   POST /api/v1/auth/login - Login
   GET  /api/v1/auth/me - Perfil atual
   POST /api/v1/auth/change-password - Alterar senha
   POST /api/v1/auth/users - Criar usuário (manager+)
   GET  /api/v1/auth/users - Listar usuários (manager+)
   PUT  /api/v1/auth/users/{id} - Editar usuário (admin)
   DELETE /api/v1/auth/users/{id} - Remover usuário (admin)

🛡️ PERMISSÕES:
   CASHIER: Operações básicas
   SUPERVISOR: + Cancelamentos, descontos
   MANAGER: + Gestão de usuários, relatórios
   ADMIN: + Configurações do sistema
"""
)
