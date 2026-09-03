from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    description: str | None = None
    
    #Notice that owner_id isn't part of ProjectCreate. we'll set it in the route handler based on the authenticated user, rather than allowing clients to specify it directly.


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None
    status: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    cover_attachment_id: UUID | None
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }