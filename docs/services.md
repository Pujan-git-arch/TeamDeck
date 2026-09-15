# services

Complete source catalog for backend/app/services.

## backend/app/services/__init__.py

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


## backend/app/services/activity.py

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


## backend/app/services/attachment.py

```python
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.repositories.attachment import AttachmentRepository
from app.services.file_storage import FileStorageService


class AttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.attachment_repository = AttachmentRepository(db)
        self.file_storage = FileStorageService()

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

    def get_file_path(
        self,
        attachment_id: UUID,
    ) -> Path:
        attachment = self.get_attachment(attachment_id)

        file_path = self.file_storage.get_file_path(
            attachment.stored_name
        )

        if not file_path.exists():
            raise ValueError("Attachment file not found")

        return file_path

    def delete_attachment(
        self,
        attachment_id: UUID,
    ) -> None:
        attachment = self.get_attachment(attachment_id)

        self.file_storage.delete_file(
            attachment.stored_name
        )

        self.attachment_repository.delete(attachment)
```


## backend/app/services/auth.py

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


## backend/app/services/comment.py

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.repositories.comment import CommentRepository
from app.schemas.comment import CommentCreate, CommentUpdate
from app.models.activity import Activity
from app.services.activity import ActivityService
from app.repositories.task import TaskRepository
from app.services.notification import NotificationService

class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.comment_repository = CommentRepository(db)
        self.task_repository = TaskRepository(db)
        self.activity_service = ActivityService(db)

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
        actor_id: UUID,
        comment_data: CommentCreate,
    ) -> Comment:
        comment = Comment(
            task_id=task_id,
            author_id=actor_id,
            body=comment_data.body,
        )

        comment = self.comment_repository.create(comment)
        
        task = self.task_repository.get_by_id(comment.task_id)

        if not task:
            raise ValueError("Task not found")
        
        activity = Activity(
            project_id=task.project_id,
            actor_id=actor_id,
            action="comment_created",
            entity_type="comment",
            entity_id=comment.id,
            extra_data={
                "task_id": str(comment.task_id),
            },
        )
        
        

        self.activity_service.create_activity(activity)
        
        notification_recipients = set()

        # Notify task creator
        if task.created_by_id != actor_id:
            notification_recipients.add(
                task.created_by_id
            )

        # Notify task assignee
        if (
            task.assignee_id is not None
            and task.assignee_id != actor_id
        ):
            notification_recipients.add(
                task.assignee_id
            )

        # Create notifications
        for recipient_id in notification_recipients:

            self.notification_service.create_notification(
                recipient_id=recipient_id,
                notification_type="comment_created",
                message=f"New comment on task: {task.title}",
                entity_type="comment",
                entity_id=comment.id,
            )

        return comment
        
        

    def update_comment(
        self,
        comment_id: UUID,
        comment_data: CommentUpdate,
        actor_id:UUID
    ) -> Comment:
        comment = self.get_comment(comment_id)

        comment.body = comment_data.body

        comment =self.comment_repository.update(comment)
        
        task = self.task_repository.get_by_id(comment.task_id)

        if not task:
            raise ValueError("Task not found")

        activity = Activity(
            project_id=task.project_id,
            actor_id=actor_id,
            action="comment_updated",
            entity_type="comment",
            entity_id=comment.id,
            extra_data={
                "task_id": str(comment.task_id),
            },
        )

        self.activity_service.create_activity(activity)

        return comment    

    def delete_comment(
        self,
        comment_id: UUID,
        actor_id: UUID,
    ) -> None:

        comment = self.get_comment(comment_id)

        task = self.task_repository.get_by_id(comment.task_id)

        if not task:
            raise ValueError("Task not found")

        project_id = task.project_id
        task_id = comment.task_id

        self.comment_repository.delete(comment)

        activity = Activity(
            project_id=project_id,
            actor_id=actor_id,
            action="comment_deleted",
            entity_type="comment",
            entity_id=comment_id,
            extra_data={
                "task_id": str(task_id),
            },
        )

        self.activity_service.create_activity(activity)
```


## backend/app/services/file_storage.py

```python
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class FileStorageService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, file: UploadFile, stored_name: str) -> Path:
        file_path = self.upload_dir / stored_name

        with file_path.open("wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                buffer.write(chunk)

        return file_path

    def get_file_path(self, stored_name: str) -> Path:
        return self.upload_dir / stored_name

    def delete_file(self, stored_name: str) -> None:
        file_path = self.get_file_path(stored_name)

        if file_path.exists():
            file_path.unlink()
```


## backend/app/services/notification.py

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
        
    def create_notification(
        self,
        recipient_id: UUID,
        notification_type: str,
        message: str,
        entity_type: str,
        entity_id: UUID,
    ) -> Notification:
        notification = Notification(
            recipient_id=recipient_id,
            type=notification_type,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        return self.notification_repository.create(notification)
```


## backend/app/services/project.py

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.activity import Activity
from app.services.activity import ActivityService
from app.repositories.project import ProjectRepository
from app.repositories.project_member import ProjectMemberRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.project_member_repository = ProjectMemberRepository(db)
        self.activity_Service = ActivityService(db)

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
        
        project = self.project_repository.create(project)
        
        manager_member = ProjectMember(
            project_id = project.id,
            user_id=owner_id,
            role="manager",
        )

        self.project_member_repository.create(manager_member)
        
        activity = Activity(
            project_id=project.id,
            actor_id=owner_id,
            action="project_created",
            entity_type="project",
            entity_id=project.id,
            extra_data={
                "project_name": project.name,
            },
        )

        self.activity_Service.create_activity(activity)
        
        return project
    

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

        if project_data.is_archived is not None:
            project.is_archived = project_data.is_archived

        return self.project_repository.update(project)

    def delete_project(
        self,
        project_id: UUID,
    ) -> None:
        project = self.get_project(project_id)

        self.project_repository.delete(project)
        
    def get_user_accessible_projects(self, user_id: UUID) -> list[Project]:
        return self.project_repository.get_by_member_or_owner(user_id)
```


## backend/app/services/project_member.py

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember
from app.repositories.project_member import ProjectMemberRepository
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberUpdate,
)
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.models.activity import Activity
from app.services.activity import ActivityService
from app.services.notification import NotificationService


class ProjectMemberService:
    def __init__(self, db: Session):
        self.db = db
        self.project_member_repository = ProjectMemberRepository(db)
        self.activity_service = ActivityService(db)
        self.user_repository = UserRepository(db)
        self.project_repository = ProjectRepository(db)
        self.notification_service = NotificationService(db)
    
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
        actor_id: UUID,
    ) -> ProjectMember:
        project = self.project_repository.get_by_id(project_id)
        
        if not project:
            raise ValueError("Project not found")
        
        user = self.user_repository.get_by_id(
            member_data.user_id
        )

        if not user:
            raise ValueError("User not found")

        if user.account_status != "active":
            raise ValueError(
                "User account is not active"
            )    
        
        
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

        member = self.project_member_repository.create(member)

        activity = Activity(
            project_id=project_id,
            actor_id=actor_id,
            action="member_added",
            entity_type="project_member",
            entity_id=member.user_id,
            extra_data={
                "user_id": str(member.user_id),
                "role": member.role,
            },
        )

        self.activity_service.create_activity(activity)
        
        self.notification_service.create_notification(
            recipient_id=member.user_id,
            notification_type="member_added",
            message=f"You were added to project {project.name}",
            entity_type="project",
            entity_id=project_id,
        )

        return member
    
    
    def update_member(
        self,
        project_id: UUID,
        user_id: UUID,
        member_data: ProjectMemberUpdate,
        actor_id: UUID,
    ) -> ProjectMember:
        project = self.project_repository.get_by_id(project_id)

        if not project:
            raise ValueError("Project not found")
        
        member = self.get_member(
            project_id,
            user_id,
        )

        old_role = member.role

        member.role = member_data.role

        member = self.project_member_repository.update(member)

        activity = Activity(
            project_id=project_id,
            actor_id=actor_id,
            action="member_role_updated",
            entity_type="project_member",
            entity_id=member.user_id,
            extra_data={
                "user_id": str(member.user_id),
                "old_role": old_role,
                "new_role": member.role,
            },
        )
        

        self.activity_service.create_activity(activity)
        
        
        self.notification_service.create_notification(
            recipient_id=member.user_id,
            notification_type="member_role_updated",
            message=f"Your role in project {project.name} was changed from {old_role} to {member.role}",
            entity_type="project",
            entity_id=project_id,
        )

        return member


    def remove_member(
        self,
        project_id: UUID,
        user_id: UUID,
        actor_id: UUID,
    ) -> None:
        project = self.project_repository.get_by_id(project_id)

        if not project:
            raise ValueError("Project not found")
        
        member = self.get_member(
            project_id,
            user_id,
        )

        removed_role = member.role
        removed_user_id = member.user_id

        self.project_member_repository.delete(member)

        activity = Activity(
            project_id=project_id,
            actor_id=actor_id,
            action="member_removed",
            entity_type="project_member",
            entity_id=user_id,
            extra_data={
                "user_id": str(removed_user_id),
                "role": removed_role,
            },
        )

        self.activity_service.create_activity(activity)
        
        self.notification_service.create_notification(
            recipient_id=removed_user_id,
            notification_type="member_removed",
            message=f"You were removed from project {project.name}",
            entity_type="project",
            entity_id=project_id,
        )
```


## backend/app/services/task.py

```python
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task import TaskRepository
from app.repositories.project_member import ProjectMemberRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.activity import Activity
from app.services.activity import ActivityService
from app.services.notification import NotificationService


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repository = TaskRepository(db)
        self.project_member_repository = ProjectMemberRepository(db)
        self.activity_service = ActivityService(db)
        self.notification_service = NotificationService(db)
    
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
        task_data: TaskCreate,
        actor_id:UUID,
    ) -> Task:
        
        if task_data.assignee_id is not None:
            member = self.project_member_repository.get(
                project_id=project_id,
                user_id=task_data.assignee_id,
            )

            if not member:
                raise ValueError(
                    "Assignee must be a member of this project"
                )
        
        
        task = Task(
            project_id=project_id,
            created_by_id=actor_id,
            title=task_data.title,
            description=task_data.description,
            assignee_id=task_data.assignee_id,
            priority=task_data.priority,
            due_date=task_data.due_date,
        )

        task = self.task_repository.create(task)
        
        activity = Activity(
            project_id=project_id,
            actor_id=actor_id,
            action="task_created",
            entity_type="task",
            entity_id=task.id,
            extra_data={
                "title": task.title,
            },
        )
        
        self.activity_service.create_activity(activity)
        
        if task.assignee_id is not None:

            self.notification_service.create_notification(
                recipient_id=task.assignee_id,
                notification_type="task_created",
                message=f"You were assigned a new task: {task.title}",
                entity_type="task",
                entity_id=task.id,
            )
        
        return task
    
    

    def update_task(
        self,
        task_id: UUID,
        task_data: TaskUpdate,
        actor_id:UUID
    ) -> Task:
        task = self.get_task(task_id)

        if task_data.title is not None:
            task.title = task_data.title

        if task_data.description is not None:
            task.description = task_data.description

        if task_data.assignee_id is not None:
            member = self.project_member_repository.get(
                project_id=task.project_id,
                user_id=task_data.assignee_id,
            )

            if not member:
                raise ValueError(
                    "Assignee must be a member of this project"
                )

            task.assignee_id = task_data.assignee_id

        if task_data.priority is not None:
            task.priority = task_data.priority

        if task_data.status is not None:
            task.status = task_data.status

        if task_data.due_date is not None:
            task.due_date = task_data.due_date

        task = self.task_repository.update(task)
        
        activity = Activity(
            project_id=task.project_id,
            actor_id=actor_id,
            action="task_updated",
            entity_type="task",
            entity_id=task.id,
            extra_data={
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
            },
        )

        self.activity_service.create_activity(activity)
        
        if task.assignee_id is not None:

            self.notification_service.create_notification(
                recipient_id=task.assignee_id,
                notification_type="task_updated",
                message=f"Your assigned task was updated: {task.title}",
                entity_type="task",
                entity_id=task.id,
            )

        return task

        

    def delete_task(
        self,
        task_id: UUID,
        actor_id: UUID,
    ) -> None:
        task = self.get_task(task_id)
        
        project_id = task.project_id
        task_title = task.title

        self.task_repository.delete(task)
        
        activity = Activity(
            project_id=project_id,
            actor_id=actor_id,
            action="task_deleted",
            entity_type="task",
            entity_id=task_id,
            extra_data={
                "title": task_title,
            },
        )

        self.activity_service.create_activity(activity)
```


## backend/app/services/task_attachment.py

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


## backend/app/services/user.py

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


