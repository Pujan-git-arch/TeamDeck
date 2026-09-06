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