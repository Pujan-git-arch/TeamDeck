from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task_attachment import TaskAttachment
from app.repositories.task_attachment import TaskAttachmentRepository
from app.schemas.task_attachment import TaskAttachmentCreate


class TaskAttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.task_attachment_repository = TaskAttachmentRepository(db)

    def get_task_attachment(
        self,
        task_id: UUID,
        attachment_id: UUID,
    ) -> TaskAttachment:
        task_attachment = self.task_attachment_repository.get(
            task_id,
            attachment_id,
        )

        if not task_attachment:
            raise ValueError("Task attachment not found")

        return task_attachment

    def get_task_attachments(
        self,
        task_id: UUID,
    ) -> list[TaskAttachment]:
        return self.task_attachment_repository.get_task_attachments(
            task_id
        )

    def add_attachment(
        self,
        task_id: UUID,
        attachment_data: TaskAttachmentCreate,
    ) -> TaskAttachment:
        existing = self.task_attachment_repository.get(
            task_id,
            attachment_data.attachment_id,
        )

        if existing:
            raise ValueError(
                "Attachment is already linked to this task"
            )

        task_attachment = TaskAttachment(
            task_id=task_id,
            attachment_id=attachment_data.attachment_id,
        )

        return self.task_attachment_repository.create(
            task_attachment
        )

    def remove_attachment(
        self,
        task_id: UUID,
        attachment_id: UUID,
    ) -> None:
        task_attachment = self.get_task_attachment(
            task_id,
            attachment_id,
        )

        self.task_attachment_repository.delete(task_attachment)