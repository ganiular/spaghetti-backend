from fastapi import APIRouter
from app.api.comments.router import router as comment_router

api_router = APIRouter(prefix="/api")
api_router.include_router(comment_router)
