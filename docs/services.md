# Service Layer

This document describes the service classes in `backend/app/services/`. Services contain application-level rules, construct and update model instances, validate business conditions, and delegate persistence to repositories. They receive an active SQLAlchemy `Session`; transaction commit and rollback remain the responsibility of the service or request boundary.

## Conventions

- Each service is initialized with a SQLAlchemy `Session` and creates the corresponding repository.
- Services raise `ValueError` for missing entities and business-rule violations.
- Create and update operations use Pydantic request schemas where applicable.
- Services do not commit transactions. Repository flushes make changes available within the current transaction.
- Passwords are hashed before storage and verified before authentication or password changes.

## Service Overview

| Service | Model or concern | Main responsibilities |
| --- | --- | --- |
| `AuthService` | Authentication and `User` registration | Register users, authenticate credentials, and issue access tokens. |
| `UserService` | `User` | Retrieve, list, update, approve/reject, change passwords, and delete users. |
| `ProjectService` | `Project` | Create, retrieve, list, update, and delete projects. |
| `ProjectMemberService` | `ProjectMember` | Retrieve memberships, add members, update roles, and remove members. |
| `TaskService` | `Task` | Retrieve, list, create, update, and delete tasks. |
| `CommentService` | `Comment` | Retrieve, list, create, update, and delete comments. |
| `AttachmentService` | `Attachment` | Retrieve, list by owning entity, create, and delete attachments. |
| `TaskAttachmentService` | `TaskAttachment` | Retrieve links, list task links, add links, and remove links. |
| `NotificationService` | `Notification` | Retrieve, list, mark as read, and delete notifications. |
| `ActivityService` | `Activity` | Retrieve, list by project, and create activity records. |

## Method Reference

### `AuthService`

| Method | Result | Purpose |
| --- | --- | --- |
| `register_user(user_data)` | `User` | Reject duplicate email addresses, hash the password, and create a user. |
| `authenticate_user(login_data)` | `str` | Verify email, password, and active account status, then return an access token. |

### `UserService`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_user(user_id)` | `User` | Return a user or raise `ValueError` when it does not exist. |
| `get_all_users()` | `list[User]` | Return all users. |
| `update_user(user_id, user_data)` | `User` | Update the supplied name or email after duplicate checks. |
| `change_password(user_id, password_data)` | `User` | Verify the current password, hash the new password, and update the user. |
| `approve_or_reject_user(user_id, approver_id, approval_data)` | `User` | Set account status, rejection reason, approver, and approval time. |
| `delete_user(user_id)` | `None` | Find and delete a user. |

### `ProjectService`

| Method | Result | Purpose |
| --- | --- | --- |
| `create_project(owner_id, project_data)` | `Project` | Construct and persist a project owned by the supplied user. |
| `get_project(project_id)` | `Project` | Return a project or raise `ValueError` when it does not exist. |
| `get_user_projects(owner_id)` | `list[Project]` | Return projects owned by a user. |
| `get_all_projects()` | `list[Project]` | Return all projects. |
| `update_project(project_id, project_data)` | `Project` | Update supplied project fields. |
| `delete_project(project_id)` | `None` | Find and delete a project. |

### `ProjectMemberService`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_member(project_id, user_id)` | `ProjectMember` | Return a membership or raise `ValueError` when it does not exist. |
| `get_project_members(project_id)` | `list[ProjectMember]` | Return all members in a project. |
| `get_user_projects(user_id)` | `list[ProjectMember]` | Return all project memberships for a user. |
| `add_member(project_id, member_data)` | `ProjectMember` | Reject duplicate membership and add a user to a project. |
| `update_member(project_id, user_id, member_data)` | `ProjectMember` | Update a member's role. |
| `remove_member(project_id, user_id)` | `None` | Find and remove a project membership. |

### `TaskService`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_task(task_id)` | `Task` | Return a task or raise `ValueError` when it does not exist. |
| `get_project_tasks(project_id)` | `list[Task]` | Return tasks belonging to a project. |
| `get_assigned_tasks(user_id)` | `list[Task]` | Return tasks assigned to a user. |
| `create_task(project_id, created_by_id, task_data)` | `Task` | Construct and persist a task. |
| `update_task(task_id, task_data)` | `Task` | Update supplied task fields. |
| `delete_task(task_id)` | `None` | Find and delete a task. |

### `CommentService`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_comment(comment_id)` | `Comment` | Return a comment or raise `ValueError` when it does not exist. |
| `get_task_comments(task_id)` | `list[Comment]` | Return comments belonging to a task. |
| `create_comment(task_id, author_id, comment_data)` | `Comment` | Construct and persist a comment. |
| `update_comment(comment_id, comment_data)` | `Comment` | Update a comment body. |
| `delete_comment(comment_id)` | `None` | Find and delete a comment. |

### `AttachmentService`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_attachment(attachment_id)` | `Attachment` | Return an attachment or raise `ValueError` when it does not exist. |
| `get_project_attachments(project_id)` | `list[Attachment]` | Return attachments associated with a project. |
| `get_task_attachments(task_id)` | `list[Attachment]` | Return attachments associated with a task. |
| `get_comment_attachments(comment_id)` | `list[Attachment]` | Return attachments associated with a comment. |
| `create_attachment(attachment)` | `Attachment` | Persist an attachment. |
| `delete_attachment(attachment_id)` | `None` | Find and delete an attachment. |

### `TaskAttachmentService`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_task_attachment(task_id, attachment_id)` | `TaskAttachment` | Return a task-attachment link or raise `ValueError`. |
| `get_task_attachments(task_id)` | `list[TaskAttachment]` | Return links for a task. |
| `add_attachment(task_id, attachment_data)` | `TaskAttachment` | Reject duplicate links and create a task-attachment link. |
| `remove_attachment(task_id, attachment_id)` | `None` | Find and remove a task-attachment link. |

### `NotificationService`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_notification(notification_id)` | `Notification` | Return a notification or raise `ValueError` when it does not exist. |
| `get_user_notifications(user_id)` | `list[Notification]` | Return notifications addressed to a user. |
| `get_unread_notifications(user_id)` | `list[Notification]` | Return unread notifications for a user. |
| `mark_as_read(notification_id)` | `Notification` | Set `read_at` to the current UTC time. |
| `delete_notification(notification_id)` | `None` | Find and delete a notification. |

### `ActivityService`

| Method | Result | Purpose |
| --- | --- | --- |
| `get_activity(activity_id)` | `Activity` | Return an activity or raise `ValueError` when it does not exist. |
| `get_project_activity(project_id)` | `list[Activity]` | Return activity records for a project. |
| `create_activity(activity)` | `Activity` | Persist an activity record. |

## Complete Source Code

The following sections preserve the complete current source for every file in `backend/app/services/`.

### `__init__.py`

```python
from app.services.activity import ActivityService
from app.services.attachment import AttachmentService
from app.services.auth import AuthService
from app.services.comment import CommentService
from app.services.notification import NotificationService
from app.services.project import ProjectService
from app.services.project_member import ProjectMemberService
from app.services.task import TaskService
from app.services.task_attachment import TaskAttachmentService
from app.services.user import UserService


__all__ = [
    "AuthService",
    "UserService",
    "ProjectService",
    "ProjectMemberService",
    "TaskService",
    "CommentService",
    "AttachmentService",
    "TaskAttachmentService",
    "NotificationService",
    "ActivityService",
]
```

### `activity.py`

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.repositories.activity import ActivityRepository


class ActivityService:
    def __init__(self, db: Session):
        self.db = db
        self.activity_repository = ActivityRepository(db)

    def get_activity(
        self,
        activity_id: UUID,
    ) -> Activity:
        activity = self.activity_repository.get_by_id(
            activity_id
        )

        if not activity:
            raise ValueError("Activity not found")

        return activity

    def get_project_activity(
        self,
        project_id: UUID,
    ) -> list[Activity]:
        return self.activity_repository.get_project_activity(
            project_id
        )

    def create_activity(
        self,
        activity: Activity,
    ) -> Activity:
        return self.activity_repository.create(activity)
```

### `attachment.py`

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.repositories.attachment import AttachmentRepository


class AttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.attachment_repository = AttachmentRepository(db)

    def get_attachment(
        self,
        attachment_id: UUID,
    ) -> Attachment:
        attachment = self.attachment_repository.get_by_id(
            attachment_id
        )

        if not attachment:
            raise ValueError("Attachment not found")

        return attachment

    def get_project_attachments(
        self,
        project_id: UUID,
    ) -> list[Attachment]:
        return self.attachment_repository.get_project_attachments(
            project_id
        )

    def get_task_attachments(
        self,
        task_id: UUID,
    ) -> list[Attachment]:
        return self.attachment_repository.get_task_attachments(
            task_id
        )

    def get_comment_attachments(
        self,
        comment_id: UUID,
    ) -> list[Attachment]:
        return self.attachment_repository.get_comment_attachments(
            comment_id
        )

    def create_attachment(
        self,
        attachment: Attachment,
    ) -> Attachment:
        return self.attachment_repository.create(attachment)

    def delete_attachment(
        self,
        attachment_id: UUID,
    ) -> None:
        attachment = self.get_attachment(attachment_id)

        self.attachment_repository.delete(attachment)
```

### `auth.py`

```python
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> User:
        existing_user = self.user_repository.get_by_email(
            user_data.email
        )

        if existing_user:
            raise ValueError("Email is already registered")

        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
        )

        return self.user_repository.create(user)

    def authenticate_user(self, login_data: UserLogin) -> str:
        user = self.user_repository.get_by_email(
            login_data.email
        )

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(
            login_data.password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        if user.account_status != "active":
            raise ValueError("User account is not active")

        return create_access_token(str(user.id))
```

### `comment.py`

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.repositories.comment import CommentRepository
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.comment_repository = CommentRepository(db)

    def get_comment(
        self,
        comment_id: UUID,
    ) -> Comment:
        comment = self.comment_repository.get_by_id(
            comment_id
        )

        if not comment:
            raise ValueError("Comment not found")

        return comment

    def get_task_comments(
        self,
        task_id: UUID,
    ) -> list[Comment]:
        return self.comment_repository.get_task_comments(
            task_id
        )

    def create_comment(
        self,
        task_id: UUID,
        author_id: UUID,
        comment_data: CommentCreate,
    ) -> Comment:
        comment = Comment(
            task_id=task_id,
            author_id=author_id,
            body=comment_data.body,
        )

        return self.comment_repository.create(comment)

    def update_comment(
        self,
        comment_id: UUID,
        comment_data: CommentUpdate,
    ) -> Comment:
        comment = self.get_comment(comment_id)

        comment.body = comment_data.body

        return self.comment_repository.update(comment)

    def delete_comment(
        self,
        comment_id: UUID,
    ) -> None:
        comment = self.get_comment(comment_id)

        self.comment_repository.delete(comment)
```

### `notification.py`

```python
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.notification import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_repository = NotificationRepository(db)

    def get_notification(
        self,
        notification_id: UUID,
    ) -> Notification:
        notification = self.notification_repository.get_by_id(
            notification_id
        )

        if not notification:
            raise ValueError("Notification not found")

        return notification

    def get_user_notifications(
        self,
        user_id: UUID,
    ) -> list[Notification]:
        return self.notification_repository.get_user_notifications(
            user_id
        )

    def get_unread_notifications(
        self,
        user_id: UUID,
    ) -> list[Notification]:
        return self.notification_repository.get_unread(
            user_id
        )

    def mark_as_read(
        self,
        notification_id: UUID,
    ) -> Notification:
        notification = self.get_notification(notification_id)

        notification.read_at = datetime.now(timezone.utc)

        return self.notification_repository.update(notification)

    def delete_notification(
        self,
        notification_id: UUID,
    ) -> None:
        notification = self.get_notification(notification_id)

        self.notification_repository.delete(notification)
```

### `project.py`

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repository = ProjectRepository(db)

    def create_project(
        self,
        owner_id: UUID,
        project_data: ProjectCreate,
    ) -> Project:
        project = Project(
            owner_id=owner_id,
            name=project_data.name,
            description=project_data.description,
        )

        return self.project_repository.create(project)

    def get_project(
        self,
        project_id: UUID,
    ) -> Project:
        project = self.project_repository.get_by_id(project_id)

        if not project:
            raise ValueError("Project not found")

        return project

    def get_user_projects(
        self,
        owner_id: UUID,
    ) -> list[Project]:
        return self.project_repository.get_by_owner(owner_id)

    def get_all_projects(self) -> list[Project]:
        return self.project_repository.get_all()

    def update_project(
        self,
        project_id: UUID,
        project_data: ProjectUpdate,
    ) -> Project:
        project = self.get_project(project_id)

        if project_data.name is not None:
            project.name = project_data.name

        if project_data.description is not None:
            project.description = project_data.description

        if project_data.status is not None:
            project.status = project_data.status

        return self.project_repository.update(project)

    def delete_project(
        self,
        project_id: UUID,
    ) -> None:
        project = self.get_project(project_id)

        self.project_repository.delete(project)
```

### `project_member.py`

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember
from app.repositories.project_member import ProjectMemberRepository
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberUpdate,
)


class ProjectMemberService:
    def __init__(self, db: Session):
        self.db = db
        self.project_member_repository = ProjectMemberRepository(db)

    def get_member(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> ProjectMember:
        member = self.project_member_repository.get(
            project_id,
            user_id,
        )

        if not member:
            raise ValueError("Project member not found")

        return member

    def get_project_members(
        self,
        project_id: UUID,
    ) -> list[ProjectMember]:
        return self.project_member_repository.get_project_members(
            project_id
        )

    def get_user_projects(
        self,
        user_id: UUID,
    ) -> list[ProjectMember]:
        return self.project_member_repository.get_user_projects(
            user_id
        )

    def add_member(
        self,
        project_id: UUID,
        member_data: ProjectMemberCreate,
    ) -> ProjectMember:
        existing_member = self.project_member_repository.get(
            project_id,
            member_data.user_id,
        )

        if existing_member:
            raise ValueError("User is already a project member")

        member = ProjectMember(
            project_id=project_id,
            user_id=member_data.user_id,
            role=member_data.role,
        )

        return self.project_member_repository.create(member)

    def update_member(
        self,
        project_id: UUID,
        user_id: UUID,
        member_data: ProjectMemberUpdate,
    ) -> ProjectMember:
        member = self.get_member(
            project_id,
            user_id,
        )

        member.role = member_data.role

        return self.project_member_repository.update(member)

    def remove_member(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> None:
        member = self.get_member(
            project_id,
            user_id,
        )

        self.project_member_repository.delete(member)
```

### `task.py`

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repository = TaskRepository(db)

    def get_task(
        self,
        task_id: UUID,
    ) -> Task:
        task = self.task_repository.get_by_id(task_id)

        if not task:
            raise ValueError("Task not found")

        return task

    def get_project_tasks(
        self,
        project_id: UUID,
    ) -> list[Task]:
        return self.task_repository.get_project_tasks(
            project_id
        )

    def get_assigned_tasks(
        self,
        user_id: UUID,
    ) -> list[Task]:
        return self.task_repository.get_assigned_tasks(
            user_id
        )

    def create_task(
        self,
        project_id: UUID,
        created_by_id: UUID,
        task_data: TaskCreate,
    ) -> Task:
        task = Task(
            project_id=project_id,
            created_by_id=created_by_id,
            title=task_data.title,
            description=task_data.description,
            assignee_id=task_data.assignee_id,
            priority=task_data.priority,
            due_date=task_data.due_date,
        )

        return self.task_repository.create(task)

    def update_task(
        self,
        task_id: UUID,
        task_data: TaskUpdate,
    ) -> Task:
        task = self.get_task(task_id)

        if task_data.title is not None:
            task.title = task_data.title

        if task_data.description is not None:
            task.description = task_data.description

        if task_data.assignee_id is not None:
            task.assignee_id = task_data.assignee_id

        if task_data.priority is not None:
            task.priority = task_data.priority

        if task_data.status is not None:
            task.status = task_data.status

        if task_data.due_date is not None:
            task.due_date = task_data.due_date

        return self.task_repository.update(task)

    def delete_task(
        self,
        task_id: UUID,
    ) -> None:
        task = self.get_task(task_id)

        self.task_repository.delete(task)
```

### `task_attachment.py`

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task_attachment import TaskAttachment
from app.repositories.task_attachment import TaskAttachmentRepository
from app.schemas.task_attachment import TaskAttachmentCreate


class TaskAttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.task_attachment_repository = TaskAttachmentRepository(db)

    def get_task_attachment(
        self,
        task_id: UUID,
        attachment_id: UUID,
    ) -> TaskAttachment:
        task_attachment = self.task_attachment_repository.get(
            task_id,
            attachment_id,
        )

        if not task_attachment:
            raise ValueError("Task attachment not found")

        return task_attachment

    def get_task_attachments(
        self,
        task_id: UUID,
    ) -> list[TaskAttachment]:
        return self.task_attachment_repository.get_task_attachments(
            task_id
        )

    def add_attachment(
        self,
        task_id: UUID,
        attachment_data: TaskAttachmentCreate,
    ) -> TaskAttachment:
        existing = self.task_attachment_repository.get(
            task_id,
            attachment_data.attachment_id,
        )

        if existing:
            raise ValueError(
                "Attachment is already linked to this task"
            )

        task_attachment = TaskAttachment(
            task_id=task_id,
            attachment_id=attachment_data.attachment_id,
        )

        return self.task_attachment_repository.create(
            task_attachment
        )

    def remove_attachment(
        self,
        task_id: UUID,
        attachment_id: UUID,
    ) -> None:
        task_attachment = self.get_task_attachment(
            task_id,
            attachment_id,
        )

        self.task_attachment_repository.delete(task_attachment)
```

### `user.py`

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.repositories.user import UserRepository
from app.schemas.user import (
    PasswordChange,
    UserApproval,
    UserUpdate,
)


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def get_user(self, user_id: UUID):
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        return user

    def get_all_users(self):
        return self.user_repository.get_all()

    def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate,
    ):
        user = self.get_user(user_id)

        if user_data.name is not None:
            user.name = user_data.name

        if user_data.email is not None:
            existing_user = self.user_repository.get_by_email(
                user_data.email
            )

            if existing_user and existing_user.id != user.id:
                raise ValueError("Email is already registered")

            user.email = user_data.email

        return self.user_repository.update(user)

    def change_password(
        self,
        user_id: UUID,
        password_data: PasswordChange,
    ):
        user = self.get_user(user_id)

        if not verify_password(
            password_data.current_password,
            user.password_hash,
        ):
            raise ValueError("Current password is incorrect")

        user.password_hash = hash_password(
            password_data.new_password
        )

        return self.user_repository.update(user)

    def approve_or_reject_user(
        self,
        user_id: UUID,
        approver_id: UUID,
        approval_data: UserApproval,
    ):
        user = self.get_user(user_id)

        if approval_data.approved:
            user.account_status = "active"
            user.rejection_reason = None
        else:
            user.account_status = "rejected"
            user.rejection_reason = approval_data.rejection_reason

        user.approved_by = approver_id

        from datetime import datetime, timezone

        user.approved_at = datetime.now(timezone.utc)

        return self.user_repository.update(user)

    def delete_user(self, user_id: UUID):
        user = self.get_user(user_id)

        self.user_repository.delete(user)
```
