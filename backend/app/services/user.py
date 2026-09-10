from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.repositories.user import UserRepository
from app.schemas.user import (
    PasswordChange,
    UserApproval,
    UserUpdate,
)


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def get_user(self, user_id: UUID):
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        return user

    def get_all_users(self):
        return self.user_repository.get_all()

    def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate,
    ):
        user = self.get_user(user_id)

        if user_data.name is not None:
            user.name = user_data.name

        if user_data.email is not None:
            existing_user = self.user_repository.get_by_email(
                user_data.email
            )

            if existing_user and existing_user.id != user.id:
                raise ValueError("Email is already registered")

            user.email = user_data.email

        return self.user_repository.update(user)

    def change_password(
        self,
        user_id: UUID,
        password_data: PasswordChange,
    ):
        user = self.get_user(user_id)

        if not verify_password(
            password_data.current_password,
            user.password_hash,
        ):
            raise ValueError("Current password is incorrect")

        user.password_hash = hash_password(
            password_data.new_password
        )

        return self.user_repository.update(user)

    def approve_or_reject_user(
        self,
        user_id: UUID,
        approver_id: UUID,
        approval_data: UserApproval,
    ):
        user = self.get_user(user_id)

        if approval_data.approved:
            user.account_status = "active"
            user.rejection_reason = None
        else:
            user.account_status = "rejected"
            user.rejection_reason = approval_data.rejection_reason

        user.approved_by = approver_id

        from datetime import datetime, timezone

        user.approved_at = datetime.now(timezone.utc)

        return self.user_repository.update(user)

    def delete_user(self, user_id: UUID):
        user = self.get_user(user_id)

        self.user_repository.delete(user)
        
