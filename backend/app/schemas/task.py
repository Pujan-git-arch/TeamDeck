from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=120,
    )

    description: str | None = None

    assignee_id: UUID | None = None

    priority: str = Field(
        default="medium",
        max_length=20,
    )

    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=120,
    )

    description: str | None = None
    assignee_id: UUID | None = None
    priority: str | None = None
    status: str | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    assignee_id: UUID | None
    created_by_id: UUID
    title: str
    description: str | None
    status: str
    priority: str
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }