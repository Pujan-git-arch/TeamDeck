from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import(
    require_admin,
    require_project_access,
    require_manager,
)
from app.models.user import User
from app.schemas.project_member import(
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectMemberUpdate,
)
from app.services.project_member import ProjectMemberService

router = APIRouter(
    prefix="/projects/{project_id}/members",
    tags=["Project Members"],
)

@router.get(
    "/",
    response_model= list[ProjectMemberResponse],
)
def get_project_membres(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_User: User = Depends(require_project_access),
):
    service = ProjectMemberService(db)
    
    return service.get_project_members(
        project_id
    )
    
    
@router.post(
    "/",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_project_member(
    project_id:UUID,
    member_data: ProjectMemberCreate,
    db:Session =Depends(get_db),
    current_user:User = Depends(require_manager),
):
    service = ProjectMemberService(db)
    
    try:
        member = service.add_member(
            project_id,
            member_data,
        )
        
        db.commit()
        
        return member
    
    except ValueError as error:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
        

@router.patch(
    "/{user_id}",
    response_model=ProjectMemberResponse,
)
def update_project_member(
    project_id: UUID,
    user_id: UUID,
    member_data: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    service = ProjectMemberService(db)
    
    try:
        member = service.update_member(
            project_id,
            user_id,
            member_data,
        )

        db.commit()

        return member

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    
  
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    service = ProjectMemberService(db)

    try:
        service.remove_member(
            project_id,
            user_id,
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )