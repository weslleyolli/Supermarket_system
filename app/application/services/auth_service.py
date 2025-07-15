"""
Serviço de autenticação para usuários
"""
from app.core.security import AuthenticationError, create_access_token, verify_password
from app.infrastructure.database.models.user import User
from app.infrastructure.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, username: str, password: str):
        user = self.user_repository.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Usuário ou senha inválidos")
        return user

    def create_token_for_user(self, user: User):
        data = {"sub": user.username, "user_id": user.id}
        token = create_access_token(data)
        return token
