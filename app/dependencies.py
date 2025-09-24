# app/dependencies.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB")

_client = AsyncIOMotorClient(MONGO_URL)
_db = _client[DB_NAME]

async def get_db():
    return _db
