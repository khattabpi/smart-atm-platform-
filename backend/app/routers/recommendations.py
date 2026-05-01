# backend/app/routers/recommendations.py — replace contents
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.models.user_profile import UserProfile

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.post("/", response_model=RecommendationResponse)
def get_recommendation(req: RecommendationRequest, db: Session = Depends(get_db)):
    preferred_bank = None
    if req.user_id:
        profile = db.query(UserProfile).filter(UserProfile.user_id == req.user_id).first()
        if profile:
            preferred_bank = profile.bank

    service = RecommendationService(db)
    best, score, reason, alts = service.recommend(
        lat=req.latitude, lng=req.longitude,
        user_id=req.user_id, needs_deposit=req.needs_deposit,
        needs_currency=req.needs_currency, preferred_bank=preferred_bank,
    )
    return RecommendationResponse(best_atm=best, score=score, reason=reason, alternatives=alts)