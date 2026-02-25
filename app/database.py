from typing import Annotated

from fastapi import FastAPI, Request, Depends
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from app.config import settings


async def open_connection(app: FastAPI) -> AsyncDatabase:
    client = AsyncMongoClient(settings.MONGODB_URL)
    db = client[settings.DB_NAME]

    app.state.mongodb_client = client
    app.state.database = db

    # Ensure connection
    await db.command("ping")

    print("Database connected")
    return db


async def close_connection(app: FastAPI):
    await app.state.mongodb_client.close()


def _get_db(request: Request) -> AsyncDatabase:
    return request.app.state.database


# Database depend
Database = Annotated[AsyncDatabase, Depends(_get_db)]
