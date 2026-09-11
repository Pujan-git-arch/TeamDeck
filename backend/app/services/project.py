from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repository = ProjectRepository(db)

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

        return self.project_repository.create(project)

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

        if project_data.status is not None:
            project.status = project_data.status

        return self.project_repository.update(project)

    def delete_project(
        self,
        project_id: UUID,
    ) -> None:
        project = self.get_project(project_id)

        self.project_repository.delete(project)
        
    def get_user_accessible_projects(self, user_id: UUID) -> list[Project]:
        return self.project_repository.get_by_member_or_owner(user_id)