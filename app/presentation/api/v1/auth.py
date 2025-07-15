"""
Rotas de autenticação da API v1
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.application.services.auth_service import AuthService
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.presentation.api.dependencies import get_current_active_user, require_admin
from app.presentation.schemas.auth import ChangePassword, Token, UserCreate, UserLogin, UserResponse, UserUpdate

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Endpoint para login de usuário"""
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)

    try:
        user = auth_service.authenticate_user(login_data.username, login_data.password)
        token = auth_service.create_token_for_user(user)

        return Token(
            access_token=token,
            token_type="bearer",
            expires_in=3600,
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user=Depends(get_current_active_user)):
    """Endpoint para obter dados do usuário atual"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Endpoint para mudança de senha"""
    # Implementação da mudança de senha
    pass


# ============================================================================
# ROTAS DE GERENCIAMENTO DE USUÁRIOS
# ============================================================================


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Criar novo usuário (Admin apenas)"""
    user_repo = UserRepository(db)

    try:
        new_user = user_repo.create(user_data)
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Listar usuários (Admin apenas)"""
    user_repo = UserRepository(db)
    users = user_repo.get_all(skip=skip, limit=limit)
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ) for user in users
    ]


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Editar usuário (Admin apenas)"""
    user_repo = UserRepository(db)

    try:
        updated_user = user_repo.update(user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            full_name=updated_user.full_name,
            role=updated_user.role,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int, current_user=Depends(require_admin), db: Session = Depends(get_db)
):
    """Remover usuário (Admin apenas)"""
    user_repo = UserRepository(db)

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar seu próprio usuário",
        )

    success = user_repo.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    return {"message": "Usuário removido com sucesso"}
