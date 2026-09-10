from uuid  import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import(
    PasswordChange,
    UserApproval,
    UserResponse,
    UserUpdate
)
from app.services.user import UserService

router= APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user



@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)
    
    return service.get_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)
    
    try:
        return service.get_user(user_id)
    
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
        
@router.patch(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db:Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)
    
    try:
        user= service.update_user(
            user_id,
            user_data,    
        )
        
        db.commit()
        
        return user
    
    except ValueError as error:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
            )
        
        
        
@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    password_data: PasswordChange,
    db:Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service= UserService(db)
    
    try:
        service.change_password(
            current_user.id,
            password_data,
        )
        
        db.commit()
    
    except ValueError as error:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
      
        
@router.patch(
    "/{user_id}/approval",
    response_model=UserResponse,
)
def approve_user(
    user_id: UUID,
    approval_data: UserApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)

    try:
        user = service.approve_or_reject_user(
            user_id,
            approval_data,
            current_user.id,
        )

        db.commit()

        return user

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    
    
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)

    try:
        service.delete_user(
            user_id,
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )