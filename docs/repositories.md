# repositories

Complete source catalog for backend/app/repositories.

## backend/app/repositories/__init__.py

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


## backend/app/repositories/activity.py

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
        ).order_by(Activity.created_at.desc())

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


## backend/app/repositories/attachment.py

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


## backend/app/repositories/comment.py

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
        ).order_by(Comment.created_at.asc())

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


## backend/app/repositories/notification.py

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
        ).order_by(
            Notification.created_at.desc()
        )

        return list(self.db.scalars(statement).all())

    def get_unread(
        self,
        user_id: UUID,
    ) -> list[Notification]:
        statement = select(Notification).where(
            Notification.recipient_id == user_id,
            Notification.read_at.is_(None),
        ).order_by(
            Notification.created_at.desc()
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


## backend/app/repositories/project.py

```python
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember


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
        
    def get_by_member_or_owner(self, user_id: UUID) -> list[Project]:
        statement = (
            select(Project)
            .outerjoin(
                ProjectMember,
                ProjectMember.project_id == Project.id,
            )
            .where(
                or_(
                    Project.owner_id == user_id,
                    ProjectMember.user_id == user_id,
                )
            )
            .distinct()
        )
        return list(self.db.scalars(statement).all())
```


## backend/app/repositories/project_member.py

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


## backend/app/repositories/task.py

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


## backend/app/repositories/task_attachment.py

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


## backend/app/repositories/user.py

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


