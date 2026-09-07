from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.notification import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_repository = NotificationRepository(db)

    def get_notification(
        self,
        notification_id: UUID,
    ) -> Notification:
        notification = self.notification_repository.get_by_id(
            notification_id
        )

        if not notification:
            raise ValueError("Notification not found")

        return notification

    def get_user_notifications(
        self,
        user_id: UUID,
    ) -> list[Notification]:
        return self.notification_repository.get_user_notifications(
            user_id
        )

    def get_unread_notifications(
        self,
        user_id: UUID,
    ) -> list[Notification]:
        return self.notification_repository.get_unread(
            user_id
        )

    def mark_as_read(
        self,
        notification_id: UUID,
    ) -> Notification:
        notification = self.get_notification(notification_id)

        notification.read_at = datetime.now(timezone.utc)

        return self.notification_repository.update(notification)

    def delete_notification(
        self,
        notification_id: UUID,
    ) -> None:
        notification = self.get_notification(notification_id)

        self.notification_repository.delete(notification)