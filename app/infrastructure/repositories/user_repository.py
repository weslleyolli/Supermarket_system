"""
Repositório de usuários para operações no banco de dados
"""
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.infrastructure.database.models.user import User
from app.presentation.schemas.auth import UserCreate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user_data: UserCreate):
        # Verificar se username já existe
        if self.get_by_username(user_data.username):
            raise ValueError("Username já existe")

        # Verificar se email já existe
        if self.get_by_email(user_data.email):
            raise ValueError("Email já existe")

        # Criar instância do modelo User
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
            is_active=user_data.is_active,
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).offset(skip).limit(limit).all()

    def update(self, user_id: int, user_data):
        from app.presentation.schemas.auth import UserUpdate

        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        # Atualizar apenas os campos fornecidos
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int):
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True
