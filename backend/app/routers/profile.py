"""Profile CRUD — bank selection, preferences."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.profile import ProfileOut, ProfileUpdate
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])

# Predefined banks (Egypt-focused per your example)
SUPPORTED_BANKS = [
    "CIB", "Banque Misr", "National Bank of Egypt", "QNB Alahli",
    "HSBC", "Chase", "Bank of America", "Citibank", "Wells Fargo",
    "Barclays", "Deutsche Bank", "Standard Chartered",
]


@router.get("/banks")
def list_banks():
    """Public list of supported banks for the registration dropdown."""
    return {"banks": SUPPORTED_BANKS}


@router.get("/me", response_model=ProfileOut)
def get_me(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileOut(
        user_id=current.id,
        full_name=profile.full_name,
        email=current.email,
        bank=profile.bank,
        preferred_currency=profile.preferred_currency,
        simulated_balance=profile.simulated_balance,
        phone=profile.phone,
        avatar_url=profile.avatar_url,
        created_at=profile.created_at,
    )


@router.put("/me", response_model=ProfileOut)
def update_me(
    payload: ProfileUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return ProfileOut(
        user_id=current.id,
        full_name=profile.full_name,
        email=current.email,
        bank=profile.bank,
        preferred_currency=profile.preferred_currency,
        simulated_balance=profile.simulated_balance,
        phone=profile.phone,
        avatar_url=profile.avatar_url,
        created_at=profile.created_at,
    )