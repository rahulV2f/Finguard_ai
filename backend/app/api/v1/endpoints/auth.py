from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db, get_current_user
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from backend.app.services.audit_service import audit_service

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists"
        )
    
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role or UserRole.ANALYST,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    client_ip = request.client.host if request.client else None
    audit_service.log(
        db=db,
        event_type="USER_REGISTERED",
        actor=user,
        entity_type="USER",
        entity_id=str(user.id),
        description=f"New user registered: {user.email} with role {user.role.value}",
        ip_address=client_ip
    )
    return user

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is disabled")

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(
        subject=user.email,
        extra_claims={"role": user.role.value, "name": user.full_name, "id": user.id}
    )

    client_ip = request.client.host if request.client else None
    audit_service.log(
        db=db,
        event_type="USER_LOGIN",
        actor=user,
        entity_type="AUTH",
        entity_id=str(user.id),
        description=f"User {user.email} authenticated successfully",
        ip_address=client_ip
    )

    return {"access_token": token, "token_type": "bearer", "user": user}

@router.post("/token", response_model=Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None, db: Session = Depends(get_db)):
    return login(UserLogin(email=form_data.username, password=form_data.password), request, db)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
