from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectMemberCreate(BaseModel):
    user_id: UUID
    role: str = Field(
        default="developer",
        max_length=50,
    )


class ProjectMemberUpdate(BaseModel):
    role: str = Field(
        ...,
        max_length=50,
    )


class ProjectMemberResponse(BaseModel):
    project_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime

    model_config = {
        "from_attributes": True
    }