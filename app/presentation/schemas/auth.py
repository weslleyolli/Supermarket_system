"""
Schemas para autenticação
"""

from datetime import datetime
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
