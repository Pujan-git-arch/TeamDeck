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