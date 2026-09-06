from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        notification_id: UUID,
    ) -> Notification | None:
        statement = select(Notification).where(
            Notification.id == notification_id
        )

        return self.db.scalar(statement)

    def get_user_notifications(
        self,
        user_id: UUID,
    ) -> list[Notification]:
        statement = select(Notification).where(
            Notification.recipient_id == user_id
        )

        return list(self.db.scalars(statement).all())

    def get_unread(
        self,
        user_id: UUID,
    ) -> list[Notification]:
        statement = select(Notification).where(
            Notification.recipient_id == user_id,
            Notification.read_at.is_(None),
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        notification: Notification,
    ) -> Notification:
        self.db.add(notification)
        self.db.flush()
        self.db.refresh(notification)
        return notification

    def update(
        self,
        notification: Notification,
    ) -> Notification:
        self.db.flush()
        self.db.refresh(notification)
        return notification

    def delete(
        self,
        notification: Notification,
    ) -> None:
        self.db.delete(notification)
        self.db.flush()