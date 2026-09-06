from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        activity_id: UUID,
    ) -> Activity | None:
        statement = select(Activity).where(
            Activity.id == activity_id
        )

        return self.db.scalar(statement)

    def get_project_activity(
        self,
        project_id: UUID,
    ) -> list[Activity]:
        statement = select(Activity).where(
            Activity.project_id == project_id
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        activity: Activity,
    ) -> Activity:
        self.db.add(activity)
        self.db.flush()
        self.db.refresh(activity)
        return activity