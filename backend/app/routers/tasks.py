from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    get_current_user,
    require_project_access,
    require_task_access,
    require_task_creator,
)
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task import TaskService


# Project-scoped task routes: /projects/{project_id}/tasks
project_tasks_router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["Tasks"],
)

# Task-scoped routes: /tasks
tasks_router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ---------------------------------------------------------
# PROJECT-SCOPED: CREATE TASK
# ---------------------------------------------------------

@project_tasks_router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: UUID,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = TaskService(db)

    try:
        task = service.create_task(
            project_id=project_id,
            created_by_id=current_user.id,
            task_data=task_data,
        )

        db.commit()

        return task

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# ---------------------------------------------------------
# PROJECT-SCOPED: LIST TASKS
# ---------------------------------------------------------

@project_tasks_router.get(
    "/",
    response_model=list[TaskResponse],
)
def get_project_tasks(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = TaskService(db)

    return service.get_project_tasks(project_id)


# ---------------------------------------------------------
# TASK-SCOPED: MY ASSIGNED TASKS
# ---------------------------------------------------------
# Literal route BEFORE dynamic route.

@tasks_router.get(
    "/assigned",
    response_model=list[TaskResponse],
)
def get_assigned_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)

    return service.get_assigned_tasks(current_user.id)


# ---------------------------------------------------------
# TASK-SCOPED: GET ONE TASK
# ---------------------------------------------------------

@tasks_router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = TaskService(db)

    try:
        return service.get_task(task_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# TASK-SCOPED: UPDATE TASK
# ---------------------------------------------------------

@tasks_router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_creator),
):
    service = TaskService(db)

    try:
        task = service.update_task(
            task_id=task_id,
            task_data=task_data,
        )

        db.commit()

        return task

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# TASK-SCOPED: DELETE TASK
# ---------------------------------------------------------

@tasks_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_creator),
):
    service = TaskService(db)

    try:
        service.delete_task(task_id)

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


__all__ = ["project_tasks_router", "tasks_router"]