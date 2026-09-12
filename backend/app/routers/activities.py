from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    require_admin,
    require_project_access,
)
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityResponse
from app.services.activity import ActivityService


router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


# ---------------------------------------------------------
# GET PROJECT ACTIVITY
# ---------------------------------------------------------

@router.get(
    "/project/{project_id}",
    response_model=list[ActivityResponse],
)
def get_project_activity(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = ActivityService(db)

    return service.get_project_activity(project_id)


# ---------------------------------------------------------
# GET SINGLE ACTIVITY
# ---------------------------------------------------------

@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
)
def get_activity(
    activity_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = ActivityService(db)

    try:
        return service.get_activity(activity_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# CREATE ACTIVITY
# ---------------------------------------------------------

@router.post(
    "/",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    activity_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = ActivityService(db)

    try:
        activity = Activity(
            project_id=activity_data.get("project_id"),
            actor_id=current_user.id,
            action=activity_data["action"],
            entity_type=activity_data["entity_type"],
            entity_id=activity_data["entity_id"],
            extra_data=activity_data.get("metadata", {}),
        )

        activity = service.create_activity(activity)

        db.commit()

        return activity

    except (KeyError, ValueError) as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )