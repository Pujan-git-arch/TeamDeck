from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> User:
        existing_user = self.user_repository.get_by_email(
            user_data.email
        )

        if existing_user:
            raise ValueError("Email is already registered")

        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
        )

        return self.user_repository.create(user)

    def authenticate_user(self, login_data: UserLogin) -> str:
        user = self.user_repository.get_by_email(
            login_data.email
        )

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(
            login_data.password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        if user.account_status != "active":
            raise ValueError("User account is not active")

        return create_access_token(str(user.id))