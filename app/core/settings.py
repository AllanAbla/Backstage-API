# app/core/settings.py
from pydantic import BaseModel
from functools import lru_cache
import os

class Settings(BaseModel):
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db: str = os.getenv("MONGODB_DB", "theatersdb")

    # NOVO: banco SQL para teatros
    sql_database_url: str = os.getenv(
        "SQL_DATABASE_URL",
        "sqlite+aiosqlite:///./backstage.db",
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
