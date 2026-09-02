import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import user_role_enum, account_status_enum
from backend.app.models.attachment import Attachment


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,  # unique=True already creates a unique index — no need for index=True too
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        user_role_enum,
        nullable=False,
        default="viewer",
        index=True,  # idx_users_role
    )

    account_status: Mapped[str] = mapped_column(
        account_status_enum,
        nullable=False,
        default="pending",
        index=True,  # idx_users_account_status
    )

    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Deferred FK to attachments.id — use_alter breaks the users<->attachments
    # circular dependency (attachments.uploader_id -> users.id) exactly like
    # the ALTER TABLE approach described in the design doc.
    avatar_attachment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "attachments.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_users_avatar",
        ),
        nullable=True,
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),  # now actually updates on UPDATE
        nullable=False,
    )

    # Self-referential FK — the admin who approved this user
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    approver: Mapped["User | None"] = relationship(
        "User",
        remote_side="User.id",
        foreign_keys=[approved_by],
    )

    avatar: Mapped["Attachment | None"] = relationship(
        "Attachment",
        foreign_keys=[avatar_attachment_id],
    )