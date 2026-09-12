from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.project import require_project_access
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository


def require_task_access(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    task = TaskRepository(db).get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    require_project_access(
        project_id=task.project_id,
        db=db,
        current_user=current_user,
    )

    return current_user


def require_task_creator(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    task = TaskRepository(db).get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if current_user.role in {"admin", "super_admin"}:
        return current_user

    if task.created_by_id == current_user.id:
        return current_user

    project = ProjectRepository(db).get_by_id(task.project_id)

    if project and project.owner_id == current_user.id:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to modify this task",
    )