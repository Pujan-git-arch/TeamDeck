from uuid import UUID

from pydantic import BaseModel


class TaskAttachmentCreate(BaseModel):
    attachment_id: UUID


class TaskAttachmentResponse(BaseModel):
    task_id: UUID
    attachment_id: UUID

    model_config = {
        "from_attributes": True
    }