from uuid import UUID

from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.repositories.attachment import AttachmentRepository


class AttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.attachment_repository = AttachmentRepository(db)

    def get_attachment(
        self,
        attachment_id: UUID,
    ) -> Attachment:
        attachment = self.attachment_repository.get_by_id(
            attachment_id
        )

        if not attachment:
            raise ValueError("Attachment not found")

        return attachment

    def get_project_attachments(
        self,
        project_id: UUID,
    ) -> list[Attachment]:
        return self.attachment_repository.get_project_attachments(
            project_id
        )

    def get_task_attachments(
        self,
        task_id: UUID,
    ) -> list[Attachment]:
        return self.attachment_repository.get_task_attachments(
            task_id
        )

    def get_comment_attachments(
        self,
        comment_id: UUID,
    ) -> list[Attachment]:
        return self.attachment_repository.get_comment_attachments(
            comment_id
        )

    def create_attachment(
        self,
        attachment: Attachment,
    ) -> Attachment:
        return self.attachment_repository.create(attachment)

    def delete_attachment(
        self,
        attachment_id: UUID,
    ) -> None:
        attachment = self.get_attachment(attachment_id)

        self.attachment_repository.delete(attachment)