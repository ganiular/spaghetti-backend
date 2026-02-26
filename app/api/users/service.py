from typing import Annotated, cast

from bson import ObjectId
from fastapi import Body, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.users.model import (
    LoginForm,
    RefreshTokenInDB,
    RegisterForm,
    AuthenticatedUser,
    Token,
    User,
    UserWithPassword,
)
from app.api.users.password_hash import hash_password, verify_password
from app.api.users.token import (
    encode_access_token,
    encode_refresh_token,
    decode_token,
)
from app.database import Database
from app.exceptions import InvalidParameterException
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import Email

http_bearer = HTTPBearer(auto_error=False)


class UserService:
    @staticmethod
    async def create_indexes(db: Database):
        await db.users.create_index("email", unique=True)
        await db.refresh_tokens.create_index("token", unique=True)
        await db.refresh_tokens.create_index("user_id")
        # Automatically delete expired tokens.
        await db.refresh_tokens.create_index("time_expires", expireAfterSeconds=0)

    @staticmethod
    async def register_user(form: RegisterForm, db: Database) -> AuthenticatedUser:
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

        token = await create_token(user_id=user.id, db=db)
        return AuthenticatedUser(
            user=user,
            token=token,
        )

    @staticmethod
    async def login_user(form: LoginForm, db: Database) -> AuthenticatedUser:
        if userdata := await db.users.find_one({"email": form.email}):
            user = UserWithPassword(**userdata)
            if verify_password(form.password, user.password_hash):
                token = await create_token(user_id=user.id, db=db)
                return AuthenticatedUser(
                    user=user,
                    token=token,
                )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    @staticmethod
    async def refresh_token(
        db: Database,
        refresh_token: Annotated[str, Body()],
    ) -> Token:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Missing refresh token")

        try:
            payload = decode_token(refresh_token, "refresh")
        except:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        jti = payload.get("jti")
        user_id = payload.get("sub")

        if not user_id or not jti:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # 🔁 ROTATION: revoke old token
        result = await db.refresh_tokens.update_one(
            {"token": jti, "revoked": False}, {"$set": {"revoked": True}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=401, detail="Token revoked or invalid")

        return await create_token(user_id=cast(PyObjectId, ObjectId(user_id)), db=db)

    @staticmethod
    async def logout(
        db: Database,
        refresh_token: Annotated[str, Body()],
    ):
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Missing refresh token")

        try:
            payload = decode_token(refresh_token, "refresh")
        except:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        jti = payload.get("jti")
        user_id = payload.get("sub")

        if not user_id or not jti:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        await db.refresh_tokens.update_one({"token": jti}, {"$set": {"revoked": True}})
        return {"message": "Logged out successfully"}

    @staticmethod
    async def require_user(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
        db: Database,
    ) -> User:

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        if not authorization:
            raise credentials_exception

        try:
            payload = decode_token(authorization.credentials, "access")
            if payload["type"] != "access":
                raise HTTPException(status_code=401)

            user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
            if not user:
                raise HTTPException(status_code=401)

            return User(**user)
        except Exception:
            raise credentials_exception

    @staticmethod
    async def get_user_by_email(email: Email, db: Database) -> User:
        doc = await db.users.find_one({"email": email})
        if doc:
            return User(**doc)

        raise HTTPException(status_code=404, detail="User not found")


async def create_token(user_id: PyObjectId, db: Database):
    refresh_token, jti, expire = encode_refresh_token(str(user_id))
    refresh_token_db = RefreshTokenInDB(user_id=user_id, token=jti, time_expires=expire)

    await db.refresh_tokens.insert_one(refresh_token_db.mongo_dump())

    return Token(
        access_token=encode_access_token(str(user_id)),
        refresh_token=refresh_token,
        token_type="bearer",
    )
