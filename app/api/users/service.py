from typing import Annotated

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status, logger
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.users.model import (
    Email,
    LoginForm,
    RegisterForm,
    AuthenticatedUser,
    Token,
    User,
    UserWithPassword,
)
from app.api.users.password_hash import hash_password, verify_password
from app.api.users.token import create_access_token, create_refresh_token, verify_token
from app.database import db
from app.exceptions import InvalidParameterException

http_bearer = HTTPBearer(auto_error=False)


class UserService:
    @staticmethod
    async def create_index():
        await db.users.create_index("email", unique=True)

    @staticmethod
    async def register_user(form: RegisterForm) -> AuthenticatedUser:
        # Check if user exists
        existing_user = await db.users.find_one({"email": form.email})
        if existing_user:
            raise InvalidParameterException({"email": ["Email already registered"]})

        # Hash password
        password_hash = hash_password(form.password)

        # Create user
        user = UserWithPassword(
            name=form.name, email=form.email, password_hash=password_hash
        )
        await db.users.insert_one(user.mongo_dump())

        # Generate token (placeholder)
        token = Token(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
            token_type="bearer",
        )

        return AuthenticatedUser(
            user=user,
            token=token,
        )

    @staticmethod
    async def login_user(form: LoginForm) -> AuthenticatedUser:
        if userdata := await db.users.find_one({"email": form.email}):
            user = UserWithPassword(**userdata)
            if verify_password(form.password, user.password_hash):
                # Generate token (placeholder)
                token = Token(
                    access_token=create_access_token(str(user.id)),
                    refresh_token=create_refresh_token(str(user.id)),
                    token_type="bearer",
                )

                return AuthenticatedUser(
                    user=user,
                    token=token,
                )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    @staticmethod
    async def require_user(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    ) -> User:

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        if not authorization:
            raise credentials_exception

        try:
            payload = verify_token(authorization.credentials)
            if payload["type"] != "access":
                raise HTTPException(status_code=401)

            user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
            if not user:
                raise HTTPException(status_code=401)

            return User(**user)
        except Exception as e:
            logger.logger.error("require_user:", e)
            raise credentials_exception

    @staticmethod
    async def get_user_by_email(email: Email) -> User:
        doc = await db.users.find_one({"email": email})
        if doc:
            return User(**doc)

        raise HTTPException(status_code=404, detail="User not found")
