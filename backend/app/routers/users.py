"""User-related endpoints (visit logging, etc.)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.history import UserHistory
from app.schemas.user import UserCreate, UserOut
from app.auth.security import hash_password

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Legacy user creation endpoint (use /api/auth/register instead)."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/visit/{atm_id}", status_code=201)
def log_visit(user_id: int, atm_id: int, lat: float, lng: float, db: Session = Depends(get_db)):
    """Log a user visit/use of an ATM (feeds recommendation history)."""
    h = UserHistory(user_id=user_id, atm_id=atm_id, user_lat=lat, user_lng=lng)
    db.add(h)
    db.commit()
    return {"status": "logged"}