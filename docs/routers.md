# Router Layer

This document reflects the FastAPI route modules currently implemented under `backend/app/routers/` and the registrations in `backend/app/main.py`.

## Conventions

- Each route file uses one or more `APIRouter` instances with a prefix and tag.
- Request validation is handled by Pydantic schemas and FastAPI dependency injection.
- Database sessions are injected with `Depends(get_db)`.
- Business logic is delegated to service classes.
- Route handlers convert `ValueError` exceptions into HTTP responses and call `db.commit()` or `db.rollback()` around mutations.
- Authorization is enforced by dependencies in `backend/app/dependencies/`.

## Router Overview

| File | Router object(s) | Prefix | Main responsibility |
| --- | --- | --- | --- |
| `auth.py` | `router` | `/auth` | User registration and login |
| `users.py` | `router` | `/users` | User profile, admin user management, approvals, password changes |
| `projects.py` | `router` | `/projects` | Project CRUD and project access flows |
| `project_members.py` | `router` | `/projects/{project_id}/members` | Project membership management |
| `tasks.py` | `project_tasks_router`, `tasks_router` | `/projects/{project_id}/tasks`, `/tasks` | Project-scoped and task-scoped task routes |
| `comments.py` | `task_comments_router`, `comments_router` | `/tasks/{task_id}/comments`, `/comments` | Task-scoped and comment-scoped comment routes |
| `notifications.py` | `router` | `/notifications` | Notification listing and state updates |
| `activities.py` | `router` | `/activities` | Activity listing and creation |
| `attachments.py` | `router`, `project_attachments_router`, `task_attachments_files_router`, `comment_attachments_router` | `/attachments`, `/projects/{project_id}/attachments`, `/tasks/{task_id}/attachments/files`, `/comments/{comment_id}/attachments` | Attachment listing and upload/delete flows |
| `task_attachments.py` | `project_attachments_router`, `task_attachments_files_router`, `comment_attachments_router` | `/projects/{project_id}/attachments`, `/tasks/{task_id}/attachments/files`, `/comments/{comment_id}/attachments` | Extra scoped attachment-listing routers |

## Endpoint Reference

### `auth.py`

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a new user account |
| `POST` | `/auth/login` | Authenticate a user and return a bearer token |

### `users.py`

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/users/me` | Return the authenticated user's profile |
| `GET` | `/users/` | Return all users; admin-only |
| `GET` | `/users/{user_id}` | Return one user; admin-only |
| `PATCH` | `/users/{user_id}` | Update a user profile; admin-only |
| `PATCH` | `/users/me/password` | Change the current user's password |
| `PATCH` | `/users/{user_id}/approval` | Approve or reject a user account; admin-only |
| `DELETE` | `/users/{user_id}` | Delete a user; admin-only |

### `projects.py`

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/projects/` | Create a new project |
| `GET` | `/projects/` | Return projects accessible to the current user |
| `GET` | `/projects/owned` | Return projects owned by the current user |
| `GET` | `/projects/all` | Return all projects; admin-only |
| `GET` | `/projects/{project_id}` | Return a single project if the user has access |
| `PATCH` | `/projects/{project_id}` | Update an existing project |
| `DELETE` | `/projects/{project_id}` | Delete a project |

### `project_members.py`

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/projects/{project_id}/members/` | Return all members of a project |
| `POST` | `/projects/{project_id}/members/` | Add a user to the project |
| `PATCH` | `/projects/{project_id}/members/{user_id}` | Update a member role |
| `DELETE` | `/projects/{project_id}/members/{user_id}` | Remove a member from the project |

### `tasks.py`

This file defines two router instances, not one combined router.

| Router | Method | Endpoint | Purpose |
| --- | --- | --- | --- |
| `project_tasks_router` | `POST` | `/projects/{project_id}/tasks/` | Create a task in a project |
| `project_tasks_router` | `GET` | `/projects/{project_id}/tasks/` | List tasks in a project |
| `tasks_router` | `GET` | `/tasks/assigned` | List tasks assigned to the current user |
| `tasks_router` | `GET` | `/tasks/{task_id}` | Return one task |
| `tasks_router` | `PATCH` | `/tasks/{task_id}` | Update a task |
| `tasks_router` | `DELETE` | `/tasks/{task_id}` | Delete a task |

### `comments.py`

This file also defines split routers for task-scoped and comment-scoped endpoints.

| Router | Method | Endpoint | Purpose |
| --- | --- | --- | --- |
| `task_comments_router` | `POST` | `/tasks/{task_id}/comments/` | Create a comment on a task |
| `task_comments_router` | `GET` | `/tasks/{task_id}/comments/` | List comments for a task |
| `comments_router` | `GET` | `/comments/{comment_id}` | Return one comment |
| `comments_router` | `PATCH` | `/comments/{comment_id}` | Update a comment |
| `comments_router` | `DELETE` | `/comments/{comment_id}` | Delete a comment |

### `notifications.py`

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/notifications/` | Return all notifications for the current user |
| `GET` | `/notifications/unread` | Return unread notifications |
| `GET` | `/notifications/{notification_id}` | Return one notification if it belongs to the user |
| `PATCH` | `/notifications/{notification_id}/read` | Mark a notification as read |
| `DELETE` | `/notifications/{notification_id}` | Delete a notification |

### `activities.py`

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/activities/project/{project_id}` | Return activity records for a project |
| `GET` | `/activities/{activity_id}` | Return one activity record |
| `POST` | `/activities/` | Create an activity record |

### `attachments.py`

This file is the main attachment router layer and includes both generic and scoped route groups.

| Router | Method | Endpoint | Purpose |
| --- | --- | --- | --- |
| `router` | `GET` | `/attachments/{attachment_id}` | Return one attachment by ID |
| `router` | `GET` | `/attachments/project/{project_id}` | Return attachments for a project |
| `router` | `GET` | `/attachments/task/{task_id}` | Return attachments for a task |
| `router` | `GET` | `/attachments/comment/{comment_id}` | Return attachments for a comment |
| `router` | `POST` | `/attachments/upload` | Upload and store an attachment |
| `router` | `DELETE` | `/attachments/{attachment_id}` | Delete an attachment |
| `project_attachments_router` | `GET` | `/projects/{project_id}/attachments/` | List project attachment files |
| `task_attachments_files_router` | `GET` | `/tasks/{task_id}/attachments/files/` | List task attachment files |
| `comment_attachments_router` | `GET` | `/comments/{comment_id}/attachments/` | List comment attachment files |

### `task_attachments.py`

This module defines the same scoped attachment-listing routers separately and is included in the application startup.

| Router | Method | Endpoint | Purpose |
| --- | --- | --- | --- |
| `project_attachments_router` | `GET` | `/projects/{project_id}/attachments/` | List project attachment files |
| `task_attachments_files_router` | `GET` | `/tasks/{task_id}/attachments/files/` | List task attachment files |
| `comment_attachments_router` | `GET` | `/comments/{comment_id}/attachments/` | List comment attachment files |

## Actual startup registration

The application in `backend/app/main.py` registers the following routers:

- `auth_router`
- `users_router`
- `projects_router`
- `project_members_router`
- `project_tasks_router`
- `tasks_router`
- `task_comments_router`
- `comments_router`
- `notifications_router`
- `activities_router`
- `project_attachments_router`
- `task_attachments_files_router`
- `comment_attachments_router`
- `task_attachments_router`
- `attachments_router`

This is the current, code-based source of truth for the API surface.

## Notes on the current codebase

There are two separate attachment route modules involved in the current implementation:

- `backend/app/routers/attachments.py` defines the generic attachment endpoints and the nested attachment-listing routers.
- `backend/app/routers/task_attachments.py` defines the project/task/comment attachment-listing routers as standalone `APIRouter` instances.

The route documentation should therefore be interpreted as a reflection of the actual backend code, not a single simplified `attachments.py` file.

## Complete Source Code

The sections below contain the full Python source for each router module in `backend/app/routers/`.

### `auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    
    try:
        user = service.register_user(user_data)
        db.commit()
        return user
    
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post("/login",
             response_model=TokenResponse,
             )
def login(
    form_data: OAuth2PasswordRequestForm=Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    login_data = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    try:
        access_token = service.authenticate_user(login_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"}
        )
```

### `users.py`

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import (
    PasswordChange,
    UserApproval,
    UserResponse,
    UserUpdate,
)
from app.services.user import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)

    return service.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)

    try:
        return service.get_user(user_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)

    try:
        user = service.update_user(
            user_id,
            user_data,
        )

        db.commit()

        return user

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)

    try:
        service.change_password(
            current_user.id,
            password_data,
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.patch(
    "/{user_id}/approval",
    response_model=UserResponse,
)
def approve_user(
    user_id: UUID,
    approval_data: UserApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)

    try:
        user = service.approve_or_reject_user(
            user_id,
            current_user.id,
            approval_data,
        )

        db.commit()

        return user

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)

    try:
        service.delete_user(
            user_id,
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
```

### `projects.py`

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    require_manager,
    require_admin,
    get_current_user,
    require_project_access,
    require_project_manager,
    require_project_creator,
)
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_creator),
):
    service = ProjectService(db)

    try:
        project = service.create_project(
            current_user.id,
            project_data,
        )

        db.commit()

        return project

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/",
    response_model=list[ProjectResponse],
)
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProjectService(db)
    return service.get_user_accessible_projects(current_user.id)


@router.get(
    "/owned",
    response_model=list[ProjectResponse],
)
def get_my_owned_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProjectService(db)

    return service.get_user_projects(
        current_user.id,
    )


@router.get(
    "/all",
    response_model=list[ProjectResponse],
)
def get_all_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = ProjectService(db)

    return service.get_all_projects()


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = ProjectService(db)

    try:
        return service.get_project(
            project_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_manager),
):
    service = ProjectService(db)

    try:
        project = service.update_project(
            project_id,
            project_data,
        )

        db.commit()

        return project

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_manager),
):
    service = ProjectService(db)

    try:
        service.delete_project(
            project_id
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
```

### `project_members.py`

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    require_project_access,
    require_project_manager,
    require_manager,
)
from app.models.user import User
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectMemberUpdate,
)
from app.services.project_member import ProjectMemberService

router = APIRouter(
    prefix="/projects/{project_id}/members",
    tags=["Project Members"],
)

@router.get(
    "/",
    response_model=list[ProjectMemberResponse],
)
def get_project_membres(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_User: User = Depends(require_project_access),
):
    service = ProjectMemberService(db)

    return service.get_project_members(
        project_id
    )


@router.post(
    "/",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_project_member(
    project_id: UUID,
    member_data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_manager),
):
    service = ProjectMemberService(db)

    try:
        member = service.add_member(
            project_id,
            member_data,
        )

        db.commit()

        return member

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.patch(
    "/{user_id}",
    response_model=ProjectMemberResponse,
)
def update_project_member(
    project_id: UUID,
    user_id: UUID,
    member_data: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_manager),
):
    service = ProjectMemberService(db)

    try:
        member = service.update_member(
            project_id,
            user_id,
            member_data,
        )

        db.commit()

        return member

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_manager),
):
    service = ProjectMemberService(db)

    try:
        service.remove_member(
            project_id,
            user_id,
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
```

### `tasks.py`

```python
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
```

### `comments.py`

```python
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
```

### `notifications.py`

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "/",
    response_model=list[NotificationResponse],
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    return service.get_user_notifications(current_user.id)


@router.get(
    "/unread",
    response_model=list[NotificationResponse],
)
def get_my_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    return service.get_unread_notifications(current_user.id)


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    try:
        notification = service.get_notification(notification_id)

        if notification.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )

        return notification

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    try:
        notification = service.get_notification(notification_id)

        if notification.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )

        notification = service.mark_as_read(notification_id)

        db.commit()

        return notification

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    try:
        notification = service.get_notification(notification_id)

        if notification.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )

        service.delete_notification(notification_id)

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
```

### `activities.py`

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    require_admin,
    require_project_access,
)
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityResponse
from app.services.activity import ActivityService


router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


@router.get(
    "/project/{project_id}",
    response_model=list[ActivityResponse],
)
def get_project_activity(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = ActivityService(db)

    return service.get_project_activity(project_id)


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
)
def get_activity(
    activity_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = ActivityService(db)

    try:
        return service.get_activity(activity_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.post(
    "/",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    activity_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = ActivityService(db)

    try:
        activity = Activity(
            project_id=activity_data.get("project_id"),
            actor_id=current_user.id,
            action=activity_data["action"],
            entity_type=activity_data["entity_type"],
            entity_id=activity_data["entity_id"],
            extra_data=activity_data.get("metadata", {}),
        )

        activity = service.create_activity(activity)

        db.commit()

        return activity

    except (KeyError, ValueError) as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
```

### `attachments.py`

```python
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
```

### `task_attachments.py`

```python
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
```

## Summary

The router layer is organized around these main concerns:

- Authentication and user administration: `auth.py`, `users.py`
- Project and membership management: `projects.py`, `project_members.py`
- Task and comment workflows: `tasks.py`, `comments.py`
- Notifications and activity tracking: `notifications.py`, `activities.py`
- File and attachment handling: `attachments.py`, `task_attachments.py`

This document matches the current implementation of the backend router code.
