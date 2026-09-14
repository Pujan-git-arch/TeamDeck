from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    get_current_user,
    require_project_access,
    require_task_access,
    require_comment_access,
)
from app.models.attachment import Attachment
from app.models.user import User
from app.schemas.attachment import AttachmentResponse
from app.services.attachment import AttachmentService


# Parent-scoped listing routers
project_attachments_router = APIRouter(
    prefix="/projects/{project_id}/attachments",
    tags=["Attachments"],
)

task_attachments_files_router = APIRouter(
    prefix="/tasks/{task_id}/attachments/files",
    tags=["Attachments"],
)

comment_attachments_router = APIRouter(
    prefix="/comments/{comment_id}/attachments",
    tags=["Attachments"],
)



# ---------------------------------------------------------
# PROJECT-SCOPED: LIST ATTACHMENT FILES
# ---------------------------------------------------------

@project_attachments_router.get(
    "/",
    response_model=list[AttachmentResponse],
)
def get_project_attachments(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = AttachmentService(db)

    return service.get_project_attachments(project_id)


# ---------------------------------------------------------
# TASK-SCOPED: LIST ATTACHMENT FILES
# ---------------------------------------------------------

@task_attachments_files_router.get(
    "/",
    response_model=list[AttachmentResponse],
)
def get_task_attachment_files(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = AttachmentService(db)

    return service.get_task_attachments(task_id)


# ---------------------------------------------------------
# COMMENT-SCOPED: LIST ATTACHMENT FILES
# ---------------------------------------------------------

@comment_attachments_router.get(
    "/",
    response_model=list[AttachmentResponse],
)
def get_comment_attachments(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_access),
):
    service = AttachmentService(db)

    return service.get_comment_attachments(comment_id)



__all__ = [
    "project_attachments_router",
    "task_attachments_files_router",
    "comment_attachments_router",
    
]