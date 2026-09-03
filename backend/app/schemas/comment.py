from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    body: str = Field(
        ...,
        min_length=1,
    )     
    #Notice that author_id isn't part of CommentCreate. We'll set it in the route handler based on the authenticated user, rather than allowing clients to specify it directly.


class CommentUpdate(BaseModel):
    body: str = Field(
        ...,
        min_length=1,
    )


class CommentResponse(BaseModel):
    id: UUID
    task_id: UUID
    author_id: UUID
    body: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }