from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember
from app.repositories.project_member import ProjectMemberRepository
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberUpdate,
)
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.models.activity import Activity
from app.services.activity import ActivityService
from app.services.notification import NotificationService


class ProjectMemberService:
    def __init__(self, db: Session):
        self.db = db
        self.project_member_repository = ProjectMemberRepository(db)
        self.activity_service = ActivityService(db)
        self.user_repository = UserRepository(db)
        self.project_repository = ProjectRepository(db)
        self.notification_service = NotificationService(db)
    
    def get_member(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> ProjectMember:
        member = self.project_member_repository.get(
            project_id,
            user_id,
        )

        if not member:
            raise ValueError("Project member not found")

        return member

    def get_project_members(
        self,
        project_id: UUID,
    ) -> list[ProjectMember]:
        return self.project_member_repository.get_project_members(
            project_id
        )

    def get_user_projects(
        self,
        user_id: UUID,
    ) -> list[ProjectMember]:
        return self.project_member_repository.get_user_projects(
            user_id
        )

    def add_member(
        self,
        project_id: UUID,
        member_data: ProjectMemberCreate,
        actor_id: UUID,
    ) -> ProjectMember:
        project = self.project_repository.get_by_id(project_id)
        
        if not project:
            raise ValueError("Project not found")
        
        user = self.user_repository.get_by_id(
            member_data.user_id
        )

        if not user:
            raise ValueError("User not found")

        if user.account_status != "active":
            raise ValueError(
                "User account is not active"
            )    
        
        
        existing_member = self.project_member_repository.get(
            project_id,
            member_data.user_id,
        )

        if existing_member:
            raise ValueError("User is already a project member")

        member = ProjectMember(
            project_id=project_id,
            user_id=member_data.user_id,
            role=member_data.role,
        )

        member = self.project_member_repository.create(member)

        activity = Activity(
            project_id=project_id,
            actor_id=actor_id,
            action="member_added",
            entity_type="project_member",
            entity_id=member.user_id,
            extra_data={
                "user_id": str(member.user_id),
                "role": member.role,
            },
        )

        self.activity_service.create_activity(activity)
        
        self.notification_service.create_notification(
            recipient_id=member.user_id,
            notification_type="member_added",
            message=f"You were added to project {project.name}",
            entity_type="project",
            entity_id=project_id,
        )

        return member
    
    
    def update_member(
        self,
        project_id: UUID,
        user_id: UUID,
        member_data: ProjectMemberUpdate,
        actor_id: UUID,
    ) -> ProjectMember:
        project = self.project_repository.get_by_id(project_id)

        if not project:
            raise ValueError("Project not found")
        
        member = self.get_member(
            project_id,
            user_id,
        )

        old_role = member.role

        member.role = member_data.role

        member = self.project_member_repository.update(member)

        activity = Activity(
            project_id=project_id,
            actor_id=actor_id,
            action="member_role_updated",
            entity_type="project_member",
            entity_id=member.user_id,
            extra_data={
                "user_id": str(member.user_id),
                "old_role": old_role,
                "new_role": member.role,
            },
        )
        

        self.activity_service.create_activity(activity)
        
        
        self.notification_service.create_notification(
            recipient_id=member.user_id,
            notification_type="member_role_updated",
            message=f"Your role in project {project.name} was changed from {old_role} to {member.role}",
            entity_type="project",
            entity_id=project_id,
        )

        return member


    def remove_member(
        self,
        project_id: UUID,
        user_id: UUID,
        actor_id: UUID,
    ) -> None:
        project = self.project_repository.get_by_id(project_id)

        if not project:
            raise ValueError("Project not found")
        
        member = self.get_member(
            project_id,
            user_id,
        )

        removed_role = member.role
        removed_user_id = member.user_id

        self.project_member_repository.delete(member)

        activity = Activity(
            project_id=project_id,
            actor_id=actor_id,
            action="member_removed",
            entity_type="project_member",
            entity_id=user_id,
            extra_data={
                "user_id": str(removed_user_id),
                "role": removed_role,
            },
        )

        self.activity_service.create_activity(activity)
        
        self.notification_service.create_notification(
            recipient_id=removed_user_id,
            notification_type="member_removed",
            message=f"You were removed from project {project.name}",
            entity_type="project",
            entity_id=project_id,
        )