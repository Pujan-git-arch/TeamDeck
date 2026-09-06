# Pydantic Schemas

This document contains the Pydantic schema source code from `backend/app/schemas/`.

The schemas define request and response contracts for the FastAPI API. Response schemas use `from_attributes=True` so they can be created from SQLAlchemy model instances. Fields such as owner, author, creator, uploader, and timestamps are returned by the API but are assigned by the server rather than accepted from clients.

## `__init__.py`

```python
from app.schemas.activity import ActivityResponse
from app.schemas.attachment import AttachmentResponse
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.schemas.notification import NotificationResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectMemberUpdate,
)
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.schemas.task_attachment import (
    TaskAttachmentCreate,
    TaskAttachmentResponse,
)
from app.schemas.user import (
    PasswordChange,
    UserApproval,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "PasswordChange",
    "UserApproval",
    "UserResponse",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectMemberCreate",
    "ProjectMemberUpdate",
    "ProjectMemberResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "AttachmentResponse",
    "TaskAttachmentCreate",
    "TaskAttachmentResponse",
    "NotificationResponse",
    "ActivityResponse",
]
```

## `user.py`

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class UserApproval(BaseModel):
    approved: bool
    rejection_reason: str | None = Field(default=None, max_length=500)


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    account_status: str
    rejection_reason: str | None = None
    avatar_attachment_id: UUID | None = None
    requested_at: datetime
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
```

## `project.py`

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    status: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    cover_attachment_id: UUID | None
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
```

## `project_member.py`

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectMemberCreate(BaseModel):
    user_id: UUID
    role: str = Field(default="developer", max_length=50)


class ProjectMemberUpdate(BaseModel):
    role: str = Field(..., max_length=50)


class ProjectMemberResponse(BaseModel):
    project_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime

    model_config = {
        "from_attributes": True
    }
```

## `task.py`

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    description: str | None = None
    assignee_id: UUID | None = None
    priority: str = Field(default="medium", max_length=20)
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = None
    assignee_id: UUID | None = None
    priority: str | None = None
    status: str | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    assignee_id: UUID | None
    created_by_id: UUID
    title: str
    description: str | None
    status: str
    priority: str
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
```

## `comment.py`

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1)


class CommentUpdate(BaseModel):
    body: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    id: UUID
    task_id: UUID
    author_id: UUID
    body: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
```

## `attachment.py`

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AttachmentResponse(BaseModel):
    id: UUID
    uploader_id: UUID
    project_id: UUID | None
    task_id: UUID | None
    comment_id: UUID | None
    original_name: str = Field(max_length=255)
    stored_name: str = Field(max_length=255)
    mime_type: str = Field(max_length=100)
    size_bytes: int
    kind: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
```

File uploads are handled by FastAPI's `UploadFile`; the uploaded file itself is not represented in a JSON Pydantic schema.

## `task_attachment.py`

```python
from uuid import UUID

from pydantic import BaseModel


class TaskAttachmentCreate(BaseModel):
    attachment_id: UUID


class TaskAttachmentResponse(BaseModel):
    task_id: UUID
    attachment_id: UUID

    model_config = {
        "from_attributes": True
    }
```

## `notification.py`

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    id: UUID
    recipient_id: UUID
    type: str = Field(max_length=50)
    message: str
    entity_type: str = Field(max_length=50)
    entity_id: UUID
    read_at: datetime | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
```

Notifications are generated by the system, so this module does not define a notification create schema.

## `activity.py`

```python
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ActivityResponse(BaseModel):
    id: UUID
    project_id: UUID | None
    actor_id: UUID
    action: str = Field(max_length=100)
    entity_type: str = Field(max_length=50)
    entity_id: UUID
    metadata: dict[str, Any]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
```

Activities are generated by the system, so this module does not define an activity create schema.
