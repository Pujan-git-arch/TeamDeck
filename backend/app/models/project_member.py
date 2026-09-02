import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import user_role_enum
from backend.app.models.user import User
from backend.app.models.project import Project


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        # No separate index needed: project_id is the leading column of the
        # composite PK, so it's already indexed for lookups on this column alone.
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,  # idx_project_members_user — needed since user_id isn't the PK's leading column
    )

    role: Mapped[str] = mapped_column(
        user_role_enum,
        nullable=False,
        default="developer",
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        "Project",
        foreign_keys=[project_id],
    )

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
    )