from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task_attachment import TaskAttachment


class TaskAttachmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(
        self,
        task_id: UUID,
        attachment_id: UUID,
    ) -> TaskAttachment | None:
        statement = select(TaskAttachment).where(
            TaskAttachment.task_id == task_id,
            TaskAttachment.attachment_id == attachment_id,
        )

        return self.db.scalar(statement)

    def get_task_attachments(
        self,
        task_id: UUID,
    ) -> list[TaskAttachment]:
        statement = select(TaskAttachment).where(
            TaskAttachment.task_id == task_id
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        task_attachment: TaskAttachment,
    ) -> TaskAttachment:
        self.db.add(task_attachment)
        self.db.flush()
        return task_attachment

    def delete(
        self,
        task_attachment: TaskAttachment,
    ) -> None:
        self.db.delete(task_attachment)
        self.db.flush()