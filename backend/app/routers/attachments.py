import uuid
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
from fastapi.responses import FileResponse

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


@router.get("/{attachment_id}/file")
def get_attachment_file(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttachmentService(db)

    try:
        attachment = service.get_attachment(attachment_id)

        if attachment.kind == "project_cover":
            if attachment.project_id:
                require_project_access(
                    project_id=attachment.project_id,
                    db=db,
                    current_user=current_user,
                )

        elif attachment.kind == "task_attachment":
            if attachment.task_id:
                require_task_access(
                    task_id=attachment.task_id,
                    db=db,
                    current_user=current_user,
                )

        elif attachment.kind == "comment_attachment":
            if attachment.comment_id:
                require_comment_access(
                    comment_id=attachment.comment_id,
                    db=db,
                    current_user=current_user,
                )

        elif attachment.kind == "avatar":
            if (
                attachment.uploader_id != current_user.id
                and current_user.role not in {"admin", "super_admin"}
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this file",
                )

        file_path = service.get_file_path(attachment_id)

        return FileResponse(
            path=file_path,
            media_type=attachment.mime_type,
            filename=attachment.original_name,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
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
    project_id: UUID | None = Form(...),
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


    # ---------------------------------------------------------
    # AVATAR
    # ---------------------------------------------------------

    if kind == "avatar":
        if project_id or task_id or comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Avatar attachments cannot belong to a project, task, or comment",
            )


    # ---------------------------------------------------------
    # PROJECT COVER
    # ---------------------------------------------------------

    elif kind == "project_cover":
        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="project_id is required for project_cover attachments",
            )

        if task_id or comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project cover attachments cannot belong to a task or comment",
            )

        require_project_access(
            project_id=project_id,
            db=db,
            current_user=current_user,
        )


    # ---------------------------------------------------------
    # TASK ATTACHMENT
    # ---------------------------------------------------------

    elif kind == "task_attachment":
        if not task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="task_id is required for task_attachment attachments",
            )

        if project_id or comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task attachments cannot directly belong to a project or comment",
            )

        require_task_access(
            task_id=task_id,
            db=db,
            current_user=current_user,
        )


    # ---------------------------------------------------------
    # COMMENT ATTACHMENT
    # ---------------------------------------------------------

    elif kind == "comment_attachment":
        if not comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="comment_id is required for comment_attachment attachments",
            )

        if project_id or task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment attachments cannot belong to a project or task",
            )

        require_comment_access(
            comment_id=comment_id,
            db=db,
            current_user=current_user,
        )

    service = AttachmentService(db)

    try:
        import uuid as uuid_lib

        stored_name = f"{uuid_lib.uuid4()}_{file.filename}"
        
        file.file.seek(0)
        
        file_path = service.file_storage.save_file(
            file,
            stored_name,
        )
        size_bytes = file_path.stat().st_size

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