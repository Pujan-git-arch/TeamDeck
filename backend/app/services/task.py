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