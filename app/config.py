import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    MONGODB_URL: str = os.environ["MONGODB_URL"]
    DB_NAME: str = os.environ["DB_NAME"]
    JWT_SECRET = os.environ["JWT_SECRET"]
    JWT_REFRESH_SECRET = os.environ["JWT_REFRESH_SECRET"]
    ALGORITHM = "HS256"
    EXPIRE_MINUTES = 30
    REFRESH_EXPIRE_DAYS = 7


settings = Settings()
