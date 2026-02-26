from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.models.db_model import DBModel
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import Email


class LoginForm(BaseModel):
    email: Email
    password: str = Field(..., min_length=6, max_length=128)


class RegisterForm(LoginForm):
    name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenInDB(DBModel):
    user_id: PyObjectId
    token: str  # this is jti
    time_expires: datetime
    revoked: bool = False


class User(DBModel):
    name: str
    email: EmailStr
    image_url: Optional[str] = None


class UserWithPassword(User):
    password_hash: str


class AuthenticatedUser(BaseModel):
    user: User
    token: Token
