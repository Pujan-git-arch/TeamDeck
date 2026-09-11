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