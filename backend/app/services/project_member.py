from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember
from app.repositories.project_member import ProjectMemberRepository
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberUpdate,
)


class ProjectMemberService:
    def __init__(self, db: Session):
        self.db = db
        self.project_member_repository = ProjectMemberRepository(db)

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
    ) -> ProjectMember:
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

        return self.project_member_repository.create(member)

    def update_member(
        self,
        project_id: UUID,
        user_id: UUID,
        member_data: ProjectMemberUpdate,
    ) -> ProjectMember:
        member = self.get_member(
            project_id,
            user_id,
        )

        member.role = member_data.role

        return self.project_member_repository.update(member)

    def remove_member(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> None:
        member = self.get_member(
            project_id,
            user_id,
        )

        self.project_member_repository.delete(member)