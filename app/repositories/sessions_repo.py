"""
sessions_repo.py
Repositório 100% async (motor). Fonte de verdade única para sessões.

Documento de sessão:
{
    "_id": ObjectId,
    "performance_id": str  (ObjectId da performance como string),
    "theater_id": int,
    "datetime": datetime (UTC),
    "created_at": datetime,
    "updated_at": datetime,
}
"""
from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.mongo import get_collection

COLLECTION = "sessions"


def _col() -> AsyncIOMotorCollection:
    return get_collection(COLLECTION)


def _to_out(doc: dict) -> dict:
    """Serializa documento MongoDB → dict seguro para JSON."""
    if not doc:
        return doc
    return {
        "id": str(doc["_id"]),
        "performance_id": doc.get("performance_id"),
        "theater_id": doc.get("theater_id"),
        "datetime": doc.get("datetime"),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }


async def ensure_indexes() -> None:
    """Cria índices necessários (idempotente — só cria se não existir)."""
    col = _col()
    existing = await col.index_information()
    idx_names = {v.get("name") for v in existing.values()}

    if "performance_id_1" not in idx_names:
        await col.create_index("performance_id", name="performance_id_1")
    if "theater_id_1" not in idx_names:
        await col.create_index("theater_id", name="theater_id_1")
    if "datetime_1" not in idx_names:
        await col.create_index("datetime", name="datetime_1")


async def bulk_insert(sessions: List[dict]) -> List[dict]:
    """
    Insere N sessões de uma vez.
    Cada item deve conter: performance_id, theater_id, datetime.
    Retorna os documentos inseridos com id resolvido.
    """
    if not sessions:
        return []

    now = datetime.now(timezone.utc)
    docs = [
        {
            "performance_id": s["performance_id"],
            "theater_id": int(s["theater_id"]),
            "datetime": s["datetime"],
            "created_at": now,
            "updated_at": now,
        }
        for s in sessions
    ]

    result = await _col().insert_many(docs)

    # reconstrói saída com os _id gerados
    for doc, oid in zip(docs, result.inserted_ids):
        doc["_id"] = oid

    return [_to_out(d) for d in docs]


async def list_by_performance(performance_id: str) -> List[dict]:
    cursor = _col().find({"performance_id": performance_id}).sort("datetime", 1)
    return [_to_out(d) async for d in cursor]


async def list_by_theater(theater_id: int) -> List[dict]:
    cursor = _col().find({"theater_id": theater_id}).sort("datetime", 1)
    return [_to_out(d) async for d in cursor]


async def list_all(
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> List[dict]:
    filt: dict = {}
    if date_from or date_to:
        filt["datetime"] = {}
        if date_from:
            filt["datetime"]["$gte"] = date_from
        if date_to:
            filt["datetime"]["$lte"] = date_to

    cursor = _col().find(filt).sort("datetime", 1).skip(skip).limit(limit)
    return [_to_out(d) async for d in cursor]


async def delete_by_performance(performance_id: str) -> int:
    """Remove todas as sessões de uma performance. Retorna qtd removida."""
    result = await _col().delete_many({"performance_id": performance_id})
    return result.deleted_count


async def delete_one(session_id: str) -> bool:
    """Remove uma sessão pelo id. Retorna True se encontrou e removeu."""
    result = await _col().delete_one({"_id": ObjectId(session_id)})
    return result.deleted_count == 1