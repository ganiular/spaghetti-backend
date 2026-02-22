import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    DB_NAME: str = os.getenv("DB_NAME")
    JWT_SECRET = os.getenv("JWT_SECRET")
    ALGORITHM = "HS256"
    EXPIRE_MINUTES = 30
    REFRESH_EXPIRE_DAYS = 7


settings = Settings()
