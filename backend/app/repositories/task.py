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