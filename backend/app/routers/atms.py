from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.atm_service import ATMService
from app.schemas.atm import ATMOut, ATMCreate
from app.models.atm import ATM

router = APIRouter(prefix="/api/atms", tags=["ATMs"])


@router.get("/nearby", response_model=List[ATMOut])
def get_nearby_atms(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius_km: float = Query(5.0, ge=0.1, le=50),
    working_only: bool = False,
    needs_deposit: bool = False,
    needs_ewallet: bool = False,
    currency: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Return ATMs near a coordinate, ordered by distance."""
    service = ATMService(db)
    return service.get_nearby(
        lat, lng, radius_km, working_only, needs_deposit, needs_ewallet, currency
    )


@router.get("/{atm_id}", response_model=ATMOut)
def get_atm(atm_id: int, db: Session = Depends(get_db)):
    atm = ATMService(db).get_by_id(atm_id)
    if not atm:
        raise HTTPException(status_code=404, detail="ATM not found")
    return atm


@router.post("/", response_model=ATMOut, status_code=201)
def create_atm(payload: ATMCreate, db: Session = Depends(get_db)):
    """Admin endpoint — add a new ATM."""
    atm = ATM(**payload.model_dump())
    db.add(atm)
    db.commit()
    db.refresh(atm)
    return atm


@router.get("/", response_model=List[ATMOut])
def list_atms(db: Session = Depends(get_db), limit: int = 100):
    return db.query(ATM).limit(limit).all()