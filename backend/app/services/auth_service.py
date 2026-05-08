from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import ConflictError, UnauthorizedError
from app.events.publisher import publish
from app.events.schemas import EventType, UserRegisteredPayload


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def register(self, email: str, password: str, full_name: str, bank: str) -> dict:
        if self.db.query(User).filter(User.email == email).first():
            raise ConflictError("Email already registered")

        user = User(email=email, hashed_password=hash_password(password), username=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # publish event
        await publish(
            EventType.USER_REGISTERED,
            UserRegisteredPayload(user_id=user.id, email=email).model_dump(),
        )
        return {"access_token": create_access_token(user.id), "token_type": "bearer"}

    async def login(self, email: str, password: str) -> dict:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials")
        return {"access_token": create_access_token(user.id), "token_type": "bearer"}