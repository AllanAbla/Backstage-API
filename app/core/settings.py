from pydantic import BaseModel
from functools import lru_cache
import os

class Settings(BaseModel):
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db: str = os.getenv("MONGODB_DB", "theatersdb")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()