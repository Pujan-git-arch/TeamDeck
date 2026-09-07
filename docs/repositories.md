# Repository Layer

This document describes the SQLAlchemy repository classes in `backend/app/repositories/`. The repositories encapsulate database queries and persistence operations for the model layer. They receive an active SQLAlchemy `Session`; transaction commit and rollback remain the responsibility of the service or request boundary.

## Conventions

- Each repository is initialized with a SQLAlchemy `Session`.
- Read methods build `select(...)` statements and execute them through `Session.scalar()` or `Session.scalars()`.
- Collection methods return concrete lists rather than SQLAlchemy result objects.
- Create methods add an entity, flush the session, refresh the entity, and return it, except `TaskAttachmentRepository.create`, which returns the association after flushing without a refresh.
- Update methods flush and refresh the supplied entity before returning it.
- Delete methods call `Session.delete()` followed by `flush()` and return `None`.
- Repository methods do not commit transactions. This allows callers to group multiple operations in one transaction.

## Repository Overview

| Repository | Model | Main responsibilities |
| --- | --- | --- |
| `UserRepository` | `User` | Find users by ID or email, list users, and perform CRUD operations. |
| `ProjectRepository` | `Project` | Find projects by ID or owner, list projects, and perform CRUD operations. |
| `ProjectMemberRepository` | `ProjectMember` | Find a membership, list project members or a user’s projects, and perform CRUD operations. |
| `TaskRepository` | `Task` | Find tasks by ID, project, or assignee, and perform CRUD operations. |
| `CommentRepository` | `Comment` | Find comments by ID or task, and perform CRUD operations. |
| `AttachmentRepository` | `Attachment` | Find attachments by ID or owning entity, create attachments, and delete them. |
| `TaskAttachmentRepository` | `TaskAttachment` | Find task-attachment links, list links for a task, create links, and delete them. |
| `NotificationRepository` | `Notification` | Find notifications by ID or recipient, list unread notifications, and perform CRUD operations. |
| `ActivityRepository` | `Activity` | Find activities by ID or project and create activity records. |

## Method Reference

### `UserRepository`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_by_id(user_id)` | `User | None` | Find one user by primary key. |
| `get_by_email(email)` | `User | None` | Find one user by email address. |
| `get_all()` | `list[User]` | Return all users. |
| `create(user)` | `User` | Persist and refresh a new user. |
| `update(user)` | `User` | Flush and refresh an existing user. |
| `delete(user)` | `None` | Mark a user for deletion and flush. |

### `ProjectRepository`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_by_id(project_id)` | `Project | None` | Find one project by primary key. |
| `get_by_owner(owner_id)` | `list[Project]` | Return projects owned by a user. |
| `get_all()` | `list[Project]` | Return all projects. |
| `create(project)` | `Project` | Persist and refresh a new project. |
| `update(project)` | `Project` | Flush and refresh an existing project. |
| `delete(project)` | `None` | Mark a project for deletion and flush. |

### `ProjectMemberRepository`

| Method | Result | Purpose |
| --- | --- | --- |
| `get(project_id, user_id)` | `ProjectMember | None` | Find a membership by its composite key. |
| `get_project_members(project_id)` | `list[ProjectMember]` | Return all members of a project. |
| `get_user_projects(user_id)` | `list[ProjectMember]` | Return all project memberships for a user. |
| `create(member)` | `ProjectMember` | Persist and refresh a membership. |
| `update(member)` | `ProjectMember` | Flush and refresh an existing membership. |
| `delete(member)` | `None` | Mark a membership for deletion and flush. |

### `TaskRepository`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_by_id(task_id)` | `Task | None` | Find one task by primary key. |
| `get_project_tasks(project_id)` | `list[Task]` | Return tasks belonging to a project. |
| `get_assigned_tasks(user_id)` | `list[Task]` | Return tasks assigned to a user. |
| `create(task)` | `Task` | Persist and refresh a new task. |
| `update(task)` | `Task` | Flush and refresh an existing task. |
| `delete(task)` | `None` | Mark a task for deletion and flush. |

### `CommentRepository`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_by_id(comment_id)` | `Comment | None` | Find one comment by primary key. |
| `get_task_comments(task_id)` | `list[Comment]` | Return comments belonging to a task. |
| `create(comment)` | `Comment` | Persist and refresh a new comment. |
| `update(comment)` | `Comment` | Flush and refresh an existing comment. |
| `delete(comment)` | `None` | Mark a comment for deletion and flush. |

### `AttachmentRepository`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_by_id(attachment_id)` | `Attachment | None` | Find one attachment by primary key. |
| `get_project_attachments(project_id)` | `list[Attachment]` | Return attachments associated with a project. |
| `get_task_attachments(task_id)` | `list[Attachment]` | Return attachments associated with a task. |
| `get_comment_attachments(comment_id)` | `list[Attachment]` | Return attachments associated with a comment. |
| `create(attachment)` | `Attachment` | Persist and refresh a new attachment. |
| `delete(attachment)` | `None` | Mark an attachment for deletion and flush. |

### `TaskAttachmentRepository`

| Method | Result | Purpose |
| --- | --- | --- |
| `get(task_id, attachment_id)` | `TaskAttachment | None` | Find one association by its composite key. |
| `get_task_attachments(task_id)` | `list[TaskAttachment]` | Return attachment links for a task. |
| `create(task_attachment)` | `TaskAttachment` | Persist a task-attachment association. |
| `delete(task_attachment)` | `None` | Mark an association for deletion and flush. |

### `NotificationRepository`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_by_id(notification_id)` | `Notification | None` | Find one notification by primary key. |
| `get_user_notifications(user_id)` | `list[Notification]` | Return notifications addressed to a user. |
| `get_unread(user_id)` | `list[Notification]` | Return notifications with no `read_at` value. |
| `create(notification)` | `Notification` | Persist and refresh a new notification. |
| `update(notification)` | `Notification` | Flush and refresh an existing notification. |
| `delete(notification)` | `None` | Mark a notification for deletion and flush. |

### `ActivityRepository`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_by_id(activity_id)` | `Activity | None` | Find one activity by primary key. |
| `get_project_activity(project_id)` | `list[Activity]` | Return activity records for a project. |
| `create(activity)` | `Activity` | Persist and refresh a new activity. |

## Complete Source Code

The following sections preserve the complete current source for every file in `backend/app/repositories/`.

### `__init__.py`

```python
from app.repositories.activity import ActivityRepository
from app.repositories.attachment import AttachmentRepository
from app.repositories.comment import CommentRepository
from app.repositories.notification import NotificationRepository
from app.repositories.project import ProjectRepository
from app.repositories.project_member import ProjectMemberRepository
from app.repositories.task import TaskRepository
from app.repositories.task_attachment import TaskAttachmentRepository
from app.repositories.user import UserRepository


__all__ = [
    "UserRepository",
    "ProjectRepository",
    "ProjectMemberRepository",
    "TaskRepository",
    "CommentRepository",
    "AttachmentRepository",
    "TaskAttachmentRepository",
    "NotificationRepository",
    "ActivityRepository",
]
```

### `activity.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        activity_id: UUID,
    ) -> Activity | None:
        statement = select(Activity).where(
            Activity.id == activity_id
        )

        return self.db.scalar(statement)

    def get_project_activity(
        self,
        project_id: UUID,
    ) -> list[Activity]:
        statement = select(Activity).where(
            Activity.project_id == project_id
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        activity: Activity,
    ) -> Activity:
        self.db.add(activity)
        self.db.flush()
        self.db.refresh(activity)
        return activity
```

### `attachment.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, attachment_id: UUID) -> Attachment | None:
        statement = select(Attachment).where(
            Attachment.id == attachment_id
        )

        return self.db.scalar(statement)

    def get_project_attachments(
        self,
        project_id: UUID,
    ) -> list[Attachment]:
        statement = select(Attachment).where(
            Attachment.project_id == project_id
        )

        return list(self.db.scalars(statement).all())

    def get_task_attachments(
        self,
        task_id: UUID,
    ) -> list[Attachment]:
        statement = select(Attachment).where(
            Attachment.task_id == task_id
        )

        return list(self.db.scalars(statement).all())

    def get_comment_attachments(
        self,
        comment_id: UUID,
    ) -> list[Attachment]:
        statement = select(Attachment).where(
            Attachment.comment_id == comment_id
        )

        return list(self.db.scalars(statement).all())

    def create(self, attachment: Attachment) -> Attachment:
        self.db.add(attachment)
        self.db.flush()
        self.db.refresh(attachment)
        return attachment

    def delete(self, attachment: Attachment) -> None:
        self.db.delete(attachment)
        self.db.flush()
```

### `comment.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, comment_id: UUID) -> Comment | None:
        statement = select(Comment).where(
            Comment.id == comment_id
        )

        return self.db.scalar(statement)

    def get_task_comments(self, task_id: UUID) -> list[Comment]:
        statement = select(Comment).where(
            Comment.task_id == task_id
        )

        return list(self.db.scalars(statement).all())

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.flush()
        self.db.refresh(comment)
        return comment

    def update(self, comment: Comment) -> Comment:
        self.db.flush()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
        self.db.flush()
```

### `notification.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        notification_id: UUID,
    ) -> Notification | None:
        statement = select(Notification).where(
            Notification.id == notification_id
        )

        return self.db.scalar(statement)

    def get_user_notifications(
        self,
        user_id: UUID,
    ) -> list[Notification]:
        statement = select(Notification).where(
            Notification.recipient_id == user_id
        )

        return list(self.db.scalars(statement).all())

    def get_unread(
        self,
        user_id: UUID,
    ) -> list[Notification]:
        statement = select(Notification).where(
            Notification.recipient_id == user_id,
            Notification.read_at.is_(None),
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        notification: Notification,
    ) -> Notification:
        self.db.add(notification)
        self.db.flush()
        self.db.refresh(notification)
        return notification

    def update(
        self,
        notification: Notification,
    ) -> Notification:
        self.db.flush()
        self.db.refresh(notification)
        return notification

    def delete(
        self,
        notification: Notification,
    ) -> None:
        self.db.delete(notification)
        self.db.flush()
```

### `project.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: UUID) -> Project | None:
        statement = select(Project).where(Project.id == project_id)
        return self.db.scalar(statement)

    def get_by_owner(self, owner_id: UUID) -> list[Project]:
        statement = select(Project).where(Project.owner_id == owner_id)
        return list(self.db.scalars(statement).all())

    def get_all(self) -> list[Project]:
        statement = select(Project)
        return list(self.db.scalars(statement).all())

    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.flush()
        self.db.refresh(project)
        return project

    def update(self, project: Project) -> Project:
        self.db.flush()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.flush()
```

### `project_member.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember


class ProjectMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> ProjectMember | None:
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )

        return self.db.scalar(statement)

    def get_project_members(
        self,
        project_id: UUID,
    ) -> list[ProjectMember]:
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id
        )

        return list(self.db.scalars(statement).all())

    def get_user_projects(
        self,
        user_id: UUID,
    ) -> list[ProjectMember]:
        statement = select(ProjectMember).where(
            ProjectMember.user_id == user_id
        )

        return list(self.db.scalars(statement).all())

    def create(self, member: ProjectMember) -> ProjectMember:
        self.db.add(member)
        self.db.flush()
        self.db.refresh(member)
        return member

    def update(self, member: ProjectMember) -> ProjectMember:
        self.db.flush()
        self.db.refresh(member)
        return member

    def delete(self, member: ProjectMember) -> None:
        self.db.delete(member)
        self.db.flush()
```

### `task.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: UUID) -> Task | None:
        statement = select(Task).where(Task.id == task_id)
        return self.db.scalar(statement)

    def get_project_tasks(self, project_id: UUID) -> list[Task]:
        statement = select(Task).where(
            Task.project_id == project_id
        )

        return list(self.db.scalars(statement).all())

    def get_assigned_tasks(self, user_id: UUID) -> list[Task]:
        statement = select(Task).where(
            Task.assignee_id == user_id
        )

        return list(self.db.scalars(statement).all())

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task

    def update(self, task: Task) -> Task:
        self.db.flush()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.flush()
```

### `task_attachment.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task_attachment import TaskAttachment


class TaskAttachmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(
        self,
        task_id: UUID,
        attachment_id: UUID,
    ) -> TaskAttachment | None:
        statement = select(TaskAttachment).where(
            TaskAttachment.task_id == task_id,
            TaskAttachment.attachment_id == attachment_id,
        )

        return self.db.scalar(statement)

    def get_task_attachments(
        self,
        task_id: UUID,
    ) -> list[TaskAttachment]:
        statement = select(TaskAttachment).where(
            TaskAttachment.task_id == task_id
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        task_attachment: TaskAttachment,
    ) -> TaskAttachment:
        self.db.add(task_attachment)
        self.db.flush()
        return task_attachment

    def delete(
        self,
        task_attachment: TaskAttachment,
    ) -> None:
        self.db.delete(task_attachment)
        self.db.flush()
```

### `user.py`

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User

class UserRepository:
    def __init__(self, db:Session):
        self.db = db
        
    def get_by_id(self, user_id: UUID) -> User |None:
        statement = select(User).where(User.id == user_id)
        
        return self.db.scalar(statement)
    
    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        
        return self.db.scalar(statement)
    
    def get_all(self) -> list[User]:
        statement = select(User)
        
        return list(self.db.scalars(statement))
    
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        
        return user
    
    def update(self, user: User) -> User:
        self.db.flush()
        self.db.refresh(user)
        
        return user
    
    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.flush()
        
```
