from fastapi import APIRouter
from app.api.users.service import UserService

router = APIRouter(
    prefix="/users", tags=["Users"], on_startup=[UserService.create_index]
)

router.post("/register")(UserService.register_user)
router.post("/login")(UserService.login_user)
