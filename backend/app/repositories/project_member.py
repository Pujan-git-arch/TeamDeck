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