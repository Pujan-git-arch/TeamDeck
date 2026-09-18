from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, attachment_id: UUID) -> Attachment | None:
        statement = select(Attachment).where(
            Attachment.id == attachment_id
        )

        return self.db.scalar(statement)

    def get_project_attachments(
        self,
        project_id: UUID,
    ) -> list[Attachment]:
        statement = select(Attachment).where(
            Attachment.project_id == project_id
        )

        return list(self.db.scalars(statement).all())

    def get_task_attachments(
        self,
        task_id: UUID,
    ) -> list[Attachment]:
        statement = select(Attachment).where(
            Attachment.task_id == task_id
        )

        return list(self.db.scalars(statement).all())

    def get_comment_attachments(
        self,
        comment_id: UUID,
    ) -> list[Attachment]:
        statement = select(Attachment).where(
            Attachment.comment_id == comment_id
        )

        return list(self.db.scalars(statement).all())

    def create(self, attachment: Attachment) -> Attachment:
        self.db.add(attachment)
        self.db.flush()
        self.db.refresh(attachment)
        return attachment

    def delete(self, attachment: Attachment) -> None:
        self.db.delete(attachment)
        self.db.flush()