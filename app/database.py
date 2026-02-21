import logging

from fastapi import FastAPI

from app.config import settings
from pymongo import AsyncMongoClient

client = AsyncMongoClient(settings.MONGODB_URL)
db = client[settings.DB_NAME]


async def open_connection(app: FastAPI):
    app.mongodb_client = client
    app.database = db
    ping_response = await app.database.command("ping")
    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")
    else:
        logging.info("Connected to database cluster.")


async def close_connection(app: FastAPI):
    await app.mongodb_client.close()
