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


router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"],
)


@router.get(
    "/{attachment_id}",
    response_model=AttachmentResponse,
)
def get_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttachmentService(db)

    try:
        return service.get_attachment(attachment_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.get(
    "/project/{project_id}",
    response_model=list[AttachmentResponse],
)
def get_project_attachments(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = AttachmentService(db)

    return service.get_project_attachments(project_id)


@router.get(
    "/task/{task_id}",
    response_model=list[AttachmentResponse],
)
def get_task_attachments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = AttachmentService(db)

    return service.get_task_attachments(task_id)


@router.get(
    "/comment/{comment_id}",
    response_model=list[AttachmentResponse],
)
def get_comment_attachments(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_access),
):
    service = AttachmentService(db)

    return service.get_comment_attachments(comment_id)


@router.post(
    "/upload",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_attachment(
    file: UploadFile = File(...),
    kind: str = Form(...),
    project_id: UUID | None = Form(None),
    task_id: UUID | None = Form(None),
    comment_id: UUID | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    valid_kinds = {
        "avatar",
        "project_cover",
        "task_attachment",
        "comment_attachment",
    }

    if kind not in valid_kinds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid kind. Must be one of: {', '.join(valid_kinds)}",
        )

    if kind == "task_attachment" and task_id:
        require_task_access(
            task_id=task_id,
            db=db,
            current_user=current_user,
        )

    elif kind == "comment_attachment" and comment_id:
        require_comment_access(
            comment_id=comment_id,
            db=db,
            current_user=current_user,
        )

    elif kind == "project_cover" and project_id:
        require_project_access(
            project_id=project_id,
            db=db,
            current_user=current_user,
        )

    service = AttachmentService(db)

    try:
        import uuid as uuid_lib

        stored_name = f"{uuid_lib.uuid4()}_{file.filename}"
        file_content = file.file.read()
        size_bytes = len(file_content)

        attachment = Attachment(
            uploader_id=current_user.id,
            project_id=project_id,
            task_id=task_id,
            comment_id=comment_id,
            original_name=file.filename,
            stored_name=stored_name,
            mime_type=file.content_type or "application/octet-stream",
            size_bytes=size_bytes,
            kind=kind,
        )

        attachment = service.create_attachment(attachment)

        db.commit()

        return attachment

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttachmentService(db)

    try:
        attachment = service.get_attachment(attachment_id)

        if (
            attachment.uploader_id != current_user.id
            and current_user.role not in {"admin", "super_admin"}
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this attachment",
            )

        service.delete_attachment(attachment_id)

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )