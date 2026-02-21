from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api import api_router
from app import database


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    # Startup
    await database.open_connection(app)
    yield
    # Shutdown
    await database.close_connection(app)


app = FastAPI(title="Spaghetti Backend", lifespan=db_lifespan)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"status": "Spaghetti backend running"}
