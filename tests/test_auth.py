import pytest
from backend.app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from backend.app.models.user import User, UserRole

def test_password_hashing():
    pw = "SecretBanking123!"
    hashed = get_password_hash(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_flow():
    token = create_access_token(subject="analyst@finguard.ai", extra_claims={"role": "ANALYST"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "analyst@finguard.ai"
    assert payload["role"] == "ANALYST"

def test_user_creation_model(db):
    user = User(
        email="compliance_officer@finguard.ai",
        full_name="Lead Officer",
        hashed_password=get_password_hash("LeadPass@123"),
        role=UserRole.ANALYST,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.id is not None
    assert user.email == "compliance_officer@finguard.ai"
    assert verify_password("LeadPass@123", user.hashed_password) is True
