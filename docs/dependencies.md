# Dependency Files Reference

This file contains the actual code for each dependency file under `backend/app/dependencies/`.

## File: `backend/app/dependencies/__init__.py`

```python
from app.dependencies.auth import (
    get_current_user,
    require_admin,
    require_super_admin,
    require_manager,
)

from app.dependencies.project import (
    require_project_access,
    require_project_manager,
    require_project_creator,
)

from app.dependencies.task import (
    require_task_access,
    require_task_creator,
    require_task_creator_for_project,
)

from app.dependencies.comment import (
    require_comment_access,
    require_comment_author,
)


__all__ = [
    "get_current_user",
    "require_admin",
    "require_super_admin",
    "require_manager",
    "require_project_access",
    "require_project_manager",
    "require_project_creator",
    "require_task_access",
    "require_task_creator",
    "require_comment_access",
    "require_comment_author",
    "require_task_creator_for_project",
]
```


## File: `backend/app/dependencies/auth.py`

```python
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user import UserRepository
from app.core.security import decode_access_token

from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
    )

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = decode_access_token(token)
        
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
        
    try:
        user_uuid = UUID(user_id)
        
    except ValueError:
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
        
    repository = UserRepository(db)
    user = repository.get_by_id(user_uuid)
    
    if not user:
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
        
    if user.account_status != "active":
        raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is not active",
                )
        
    return user



def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role not in {"admin", "super_admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
        
    return current_user

def require_super_admin(
    current_user: User = Depends(get_current_user),
)-> User :
    if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )
            
    return current_user

def require_manager(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "manager":     # adjust to your model
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can perform this action",
        )
    return current_user
```


## File: `backend/app/dependencies/project.py`

```python
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

    project_repository = ProjectRepository(db)

    project = project_repository.get_by_id(
        project_id
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Project owner always has access
    if project.owner_id == current_user.id:
        return current_user

    # Check project membership
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


def require_project_creator(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role not in {
        "super_admin",
        "admin",
        "manager",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create projects",
        )

    return current_user
```


## File: `backend/app/dependencies/task.py`

```python
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.project import require_project_access
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.repositories.project_member import ProjectMemberRepository
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
    
def require_task_creator_for_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:

    # Admins can create tasks in any project
    if current_user.role in {"admin", "super_admin"}:
        return current_user

    # Find the user's membership in this project
    project_member_repository = ProjectMemberRepository(db)

    member = project_member_repository.get(
        project_id=project_id,
        user_id=current_user.id,
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )

    # Only the project manager can create tasks
    if member.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project manager can create tasks",
        )

    return current_user
```


## File: `backend/app/dependencies/comment.py`

```python
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.project import require_project_access
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository


def require_comment_access(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:

    comment = CommentRepository(db).get_by_id(comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    task = TaskRepository(db).get_by_id(comment.task_id)

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


def require_comment_author(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:

    comment = CommentRepository(db).get_by_id(comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Admin and Super Admin can modify any comment
    if current_user.role in {"admin", "super_admin"}:
        return current_user

    # Comment author can modify their own comment
    if comment.author_id == current_user.id:
        return current_user

    # Project owner can modify comments in their project
    task = TaskRepository(db).get_by_id(comment.task_id)

    if task:
        project = ProjectRepository(db).get_by_id(task.project_id)

        if project and project.owner_id == current_user.id:
            return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to modify this comment",
    )
```


