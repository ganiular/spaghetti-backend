from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4
from app.config import settings
import jwt


def encode_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def encode_refresh_token(user_id: str) -> tuple[str, str, datetime]:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_EXPIRE_DAYS)

    jti = str(uuid4())

    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": jti,
        "exp": expire,
    }

    token = jwt.encode(
        payload, settings.JWT_REFRESH_SECRET, algorithm=settings.ALGORITHM
    )

    return token, jti, expire


def decode_token(token: str, type: str) -> dict[str, Any]:
    if type == "access":
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
    elif type == "refresh":
        return jwt.decode(
            token, settings.JWT_REFRESH_SECRET, algorithms=[settings.ALGORITHM]
        )
    return {}
