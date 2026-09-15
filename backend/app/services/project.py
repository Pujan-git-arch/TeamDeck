from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.activity import Activity
from app.services.activity import ActivityService
from app.repositories.project import ProjectRepository
from app.repositories.project_member import ProjectMemberRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.project_member_repository = ProjectMemberRepository(db)
        self.activity_Service = ActivityService(db)

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
        
        project = self.project_repository.create(project)
        
        manager_member = ProjectMember(
            project_id = project.id,
            user_id=owner_id,
            role="manager",
        )

        self.project_member_repository.create(manager_member)
        
        activity = Activity(
            project_id=project.id,
            actor_id=owner_id,
            action="project_created",
            entity_type="project",
            entity_id=project.id,
            extra_data={
                "project_name": project.name,
            },
        )

        self.activity_Service.create_activity(activity)
        
        return project
    

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

        if project_data.is_archived is not None:
            project.is_archived = project_data.is_archived

        return self.project_repository.update(project)

    def delete_project(
        self,
        project_id: UUID,
    ) -> None:
        project = self.get_project(project_id)

        self.project_repository.delete(project)
        
    def get_user_accessible_projects(self, user_id: UUID) -> list[Project]:
        return self.project_repository.get_by_member_or_owner(user_id)