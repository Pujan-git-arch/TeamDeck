from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------
# User Registration
# ---------------------------------------------------------

class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=120,
    )
    
    email: EmailStr
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


# ---------------------------------------------------------
# User Profile Update
# ---------------------------------------------------------

class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )
    
    email: EmailStr | None = None


# ---------------------------------------------------------
# User Login
# ---------------------------------------------------------

class UserLogin(BaseModel):
    email: EmailStr
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


# ---------------------------------------------------------
# Password Change
# ---------------------------------------------------------

class PasswordChange(BaseModel):
    current_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )
    
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


# ---------------------------------------------------------
# Admin User Approval / Rejection
# ---------------------------------------------------------

class UserApproval(BaseModel):
    approved: bool
    
    rejection_reason: str | None = Field(
        default=None,
        max_length=500,
    )


# ---------------------------------------------------------
# User Response
# ---------------------------------------------------------

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    account_status: str
    rejection_reason: str | None = None
    avatar_attachment_id: UUID | None = None
    requested_at: datetime
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }