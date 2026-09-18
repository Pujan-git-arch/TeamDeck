from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.repositories.activity import ActivityRepository


class ActivityService:
    def __init__(self, db: Session):
        self.db = db
        self.activity_repository = ActivityRepository(db)

    def get_activity(
        self,
        activity_id: UUID,
    ) -> Activity:
        activity = self.activity_repository.get_by_id(
            activity_id
        )

        if not activity:
            raise ValueError("Activity not found")

        return activity

    def get_project_activity(
        self,
        project_id: UUID,
    ) -> list[Activity]:
        return self.activity_repository.get_project_activity(
            project_id
        )

    def create_activity(
        self,
        activity: Activity,
    ) -> Activity:
        return self.activity_repository.create(activity)