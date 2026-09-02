import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from backend.app.models.attachment import Attachment
from backend.app.models.task import Task
from backend.app.models.attachment import Attachment


class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    attachment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attachments.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    task: Mapped["Task"] = relationship(
        "Task",
        foreign_keys=[task_id],
    )

    attachment: Mapped["Attachment"] = relationship(
        "Attachment",
        foreign_keys=[attachment_id],
    )