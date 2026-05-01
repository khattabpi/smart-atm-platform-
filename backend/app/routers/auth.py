"""Registration & login endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.auth.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Username from email prefix
    username = payload.email.split("@")[0]

    user = User(
        username=username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = UserProfile(
        user_id=user.id,
        full_name=payload.full_name,
        bank=payload.bank,
        simulated_balance=1000.0,
    )
    db.add(profile)
    db.commit()

    token = create_access_token(subject=user.email)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=payload.full_name,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    token = create_access_token(subject=user.email)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=profile.full_name if profile else None,
    )