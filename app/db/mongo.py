from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.settings import get_settings

_settings = get_settings()
_client = AsyncIOMotorClient(_settings.mongodb_uri)
_db: AsyncIOMotorDatabase = _client[_settings.mongodb_db]

def get_db() -> AsyncIOMotorDatabase:
    return _db

def get_collection(name: str):
    return _db[name]