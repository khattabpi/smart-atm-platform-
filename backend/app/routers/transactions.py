"""Simulated transaction system — withdraw/deposit against demo wallet."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionOut, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    status_str = "completed"
    if payload.type == "withdraw":
        if profile.simulated_balance < payload.amount:
            status_str = "failed"
        else:
            profile.simulated_balance -= payload.amount
    elif payload.type == "deposit":
        profile.simulated_balance += payload.amount

    tx = Transaction(
        user_id=current.id,
        atm_id=payload.atm_id,
        type=payload.type,
        amount=payload.amount,
        currency=payload.currency,
        status=status_str,
        note=payload.note,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    if status_str == "failed":
        raise HTTPException(status_code=400, detail="Insufficient balance")
    return tx


@router.get("/", response_model=List[TransactionOut])
def list_my_transactions(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == current.id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/analytics")
def get_analytics(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aggregated activity stats for the dashboard."""
    txs = db.query(Transaction).filter(Transaction.user_id == current.id).all()
    total_withdrawn = sum(t.amount for t in txs if t.type == "withdraw" and t.status == "completed")
    total_deposited = sum(t.amount for t in txs if t.type == "deposit" and t.status == "completed")
    return {
        "total_transactions": len(txs),
        "total_withdrawn": round(total_withdrawn, 2),
        "total_deposited": round(total_deposited, 2),
        "successful": sum(1 for t in txs if t.status == "completed"),
        "failed": sum(1 for t in txs if t.status == "failed"),
    }