from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    require_task_access,
    require_comment_access,
    require_comment_author,
)
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment import CommentService


# Task-scoped comment routes: /tasks/{task_id}/comments
task_comments_router = APIRouter(
    prefix="/tasks/{task_id}/comments",
    tags=["Comments"],
)

# Comment-scoped routes: /comments
comments_router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


# ---------------------------------------------------------
# TASK-SCOPED: CREATE COMMENT
# ---------------------------------------------------------

@task_comments_router.post(
    "/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    task_id: UUID,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = CommentService(db)

    try:
        comment = service.create_comment(
            task_id=task_id,
            author_id=current_user.id,
            comment_data=comment_data,
        )

        db.commit()

        return comment

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# ---------------------------------------------------------
# TASK-SCOPED: LIST COMMENTS
# ---------------------------------------------------------

@task_comments_router.get(
    "/",
    response_model=list[CommentResponse],
)
def get_task_comments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = CommentService(db)

    return service.get_task_comments(task_id)


# ---------------------------------------------------------
# COMMENT-SCOPED: GET ONE
# ---------------------------------------------------------

@comments_router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
def get_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_access),
):
    service = CommentService(db)

    try:
        return service.get_comment(comment_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# COMMENT-SCOPED: UPDATE
# ---------------------------------------------------------

@comments_router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: UUID,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_author),
):
    service = CommentService(db)

    try:
        comment = service.update_comment(
            comment_id=comment_id,
            comment_data=comment_data,
        )

        db.commit()

        return comment

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# COMMENT-SCOPED: DELETE
# ---------------------------------------------------------

@comments_router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_author),
):
    service = CommentService(db)

    try:
        service.delete_comment(comment_id)

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


__all__ = ["task_comments_router", "comments_router"]