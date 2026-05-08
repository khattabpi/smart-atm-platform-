"""Dependency injection helpers."""
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError


def get_current_user_id(authorization: str | None = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    return int(payload["sub"])


def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db