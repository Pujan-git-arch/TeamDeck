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