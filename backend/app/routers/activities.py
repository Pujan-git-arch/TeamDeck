from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    require_admin,
    require_project_access,
)
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

