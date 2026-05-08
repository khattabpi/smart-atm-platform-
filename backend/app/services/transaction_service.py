from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.events.publisher import publish
from app.events.schemas import EventType, TransactionCompletedPayload
from app.core.exceptions import ValidationError


class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, user_id: int, type_: str, amount: float, atm_id: int | None = None) -> Transaction:
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        if type_ not in ("withdraw", "deposit"):
            raise ValidationError("Invalid transaction type")

        tx = Transaction(user_id=user_id, type=type_, amount=amount, atm_id=atm_id, status="completed")
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)

        await publish(
            EventType.TRANSACTION_COMPLETED,
            TransactionCompletedPayload(
                transaction_id=tx.id, user_id=user_id, type=type_, amount=amount
            ).model_dump(),
        )
        return tx