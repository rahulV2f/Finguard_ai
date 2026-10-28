from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from backend.app.models.user import UserRole

class UserBase(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    full_name: str
    role: UserRole = UserRole.ANALYST
    is_active: bool = True

class UserCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    full_name: str
    password: str
    role: UserRole = UserRole.ANALYST

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
