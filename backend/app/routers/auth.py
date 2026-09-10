from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    
    try:
        user = service.register_user(user_data)
        db.commit()
        return user
    
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
        
        
@router.post("/login")
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    service= AuthService(db)
    
    try:
        access_token = service.authenticate_user(login_data)
        
        return{
            "access_token": access_token,
            "token_type": "bearer",
        }
    
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate":"Bearer"}
        )