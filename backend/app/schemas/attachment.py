from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AttachmentResponse(BaseModel):
    id: UUID
    uploader_id: UUID
    project_id: UUID | None
    task_id: UUID | None
    comment_id: UUID | None
    original_name: str = Field(max_length=255)
    stored_name: str = Field(max_length=255)
    mime_type: str = Field(max_length=100)
    size_bytes: int
    kind: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
    
    #For uploads, the actual file will come through FastAPI's UploadFile, so we don't put the file itself inside a Pydantic JSON schema.