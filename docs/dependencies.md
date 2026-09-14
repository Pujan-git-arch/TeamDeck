# Dependency Layer

This document describes the FastAPI dependency functions in `backend/app/dependencies/`. These dependencies centralize authentication, authorization, and project-level access checks. They are used by the routers to enforce permission rules before a service or database operation runs.

## Conventions

- Dependencies are defined as functions that receive request data through FastAPI `Depends(...)`.
- Authentication dependencies read the JWT token, validate it, and load the current user from the database.
- Authorization dependencies raise `HTTPException` with a `403` status when the current user is not allowed to proceed.
- Project access dependencies check both the user role and the project relationship before allowing access to a project-scoped endpoint.
- Dependency functions do not commit or mutate the database directly; they only validate access.

## Dependency Overview

| Dependency | Source file | Purpose |
| --- | --- | --- |
| `get_current_user` | `auth.py` | Validate JWT token and return the authenticated user. |
| `require_admin` | `auth.py` | Allow only `admin` or `super_admin` users. |
| `require_super_admin` | `auth.py` | Allow only `super_admin` users. |
| `require_manager` | `auth.py` | Allow only `manager` users. |
| `require_project_access` | `project.py` | Allow access to a project if the user is admin, owner, or project member. |
| `require_project_manager` | `project.py` | Allow project management only to owners with manager-level permission. |
| `require_project_creator` | `project.py` | Allow project creation only to users with creator-capable roles. |

## Dependency Reference

### `auth.py`

| Dependency | Result | Purpose |
| --- | --- | --- |
| `get_current_user(token, db)` | `User` | Decode the access token, validate the user, and ensure the account is active. |
| `require_admin(current_user)` | `User` | Enforce admin-level access. |
| `require_super_admin(current_user)` | `User` | Enforce super-admin-only access. |
| `require_manager(current_user)` | `User` | Enforce manager-level access. |

### `project.py`

| Dependency | Result | Purpose |
| --- | --- | --- |
| `require_project_access(project_id, db, current_user)` | `User` | Allow access if the user is admin, project owner, or project member. |
| `require_project_manager(project_id, db, current_user)` | `User` | Allow project updates/deletes only for owner managers. |
| `require_project_creator(current_user)` | `User` | Restrict project creation to admin, super_admin, and manager roles. |

## Complete Source Code

### `auth.py`

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

### `project.py`

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

### `__init__.py`

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


__all__ = [
    "get_current_user",
    "require_admin",
    "require_super_admin",
    "require_manager",
    "require_project_access",
    "require_project_manager",
    "require_project_creator",
]
```

## Notes

- The current dependency layer is focused on authentication and project-level access control.
- Project membership is enforced through the `project_members` table, but the access dependency does not currently inspect the member role beyond existence.
- The dependency structure is centralized and easy to reuse across routers, which is the intended pattern for the backend.
