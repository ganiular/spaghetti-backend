from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.models.db_model import DBModel
from app.utils.models.py_object_id import PyObjectId


class LoginForm(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


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


class User(DBModel):
    name: str
    email: EmailStr
    image_url: Optional[str] = None


class UserWithPassword(User):
    password_hash: str


class AuthenticatedUser(BaseModel):
    user: User
    token: Token
