from fastapi import APIRouter
from app.api.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

router.post("/register")(UserService.register_user)
router.post("/login")(UserService.login_user)
router.post("/refresh")(UserService.refresh_token)
router.post("/logout")(UserService.logout)
