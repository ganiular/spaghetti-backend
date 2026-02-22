from typing import Annotated

from fastapi import Depends

from app.api.users.model import User
from app.api.users.service import UserService


RequireUser = Annotated[User, Depends(UserService.require_user)]
