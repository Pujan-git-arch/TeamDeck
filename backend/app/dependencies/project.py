from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.repositories.project_member import ProjectMemberRepository


def require_project_access(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:

    # Admin and Super Admin can access every project
    if current_user.role in {
        "admin",
        "super_admin",
    }:
        return current_user

    # Check whether the user is a member of this project
    member_repository = ProjectMemberRepository(db)

    member = member_repository.get(
        project_id=project_id,
        user_id=current_user.id,
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        )

    return current_user


def require_project_manager(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:

    # Admin and Super Admin can manage every project
    if current_user.role in {
        "admin",
        "super_admin",
    }:
        return current_user

    # User must be a manager
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project manager access required",
        )

    # Find the project
    project_repository = ProjectRepository(db)

    project = project_repository.get_by_id(
        project_id
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Manager must own the project
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the manager of this project",
        )

    return current_user