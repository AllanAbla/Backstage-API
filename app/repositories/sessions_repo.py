from app.db.mongo import _db as db
from typing import List

COLLECTION_NAME = "sessions"


def save_sessions(sessions: List[dict]):
    """Salva várias sessões no MongoDB"""
    if not sessions:
        return []
    db[COLLECTION_NAME].insert_many(sessions)
    return sessions


def get_all_sessions():
    """Retorna todas as sessões"""
    return list(db[COLLECTION_NAME].find({}, {"_id": 0}))


def get_sessions_by_theater(theater_id):
    """Busca sessões por teatro"""
    return list(db[COLLECTION_NAME].find({"theater_id": theater_id}, {"_id": 0}))


def get_sessions_by_performance(performance_id):
    """Busca sessões por performance"""
    return list(db[COLLECTION_NAME].find({"performance_id": performance_id}, {"_id": 0}))
