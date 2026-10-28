from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db, get_current_admin
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserResponse, UserCreate
from backend.app.core.security import get_password_hash
from backend.app.services.audit_service import audit_service

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(User).offset(skip).limit(limit).all()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User email already exists")
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    audit_service.log(
        db=db,
        event_type="ADMIN_USER_CREATED",
        actor=admin,
        entity_type="USER",
        entity_id=str(user.id),
        description=f"Admin created user {user.email} ({user.role.value})"
    )
    return user
