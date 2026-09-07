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