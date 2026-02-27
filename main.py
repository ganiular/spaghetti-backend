from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api import api_router
from app import database
from app.api.comments.service import CommentService
from app.api.team_members.service import TeamMemberService
from app.api.teams.service import TeamService
from app.api.users.service import UserService
from app.exceptions import register_exceptions


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    # Startup
    db = await database.open_connection(app)

    # Create database indexes
    await UserService.create_indexes(db)
    await TeamService.create_indexes(db)
    await TeamMemberService.create_indexes(db)
    await CommentService.create_indexes(db)

    yield

    # Shutdown
    await database.close_connection(app)


app = FastAPI(title="Spaghetti Backend", lifespan=db_lifespan)

app.include_router(api_router)

register_exceptions(app)


@app.get("/")
async def root():
    return {"status": "Spaghetti backend running"}
