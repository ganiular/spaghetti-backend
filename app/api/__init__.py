from fastapi import APIRouter
from app.api.users.router import router as user_router
from app.api.teams.router import router as team_router
from app.api.comments.router import router as comment_router

api_router = APIRouter(prefix="/api")
api_router.include_router(user_router)
api_router.include_router(team_router)
api_router.include_router(comment_router)
