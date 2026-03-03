"""
performances_repo.py
Performances armazenam APENAS metadados.
Sessões vivem exclusivamente na coleção `sessions` (sessions_repo).
O campo `banner` virou `banner_url` (path relativo no disco).
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId, errors as bson_errors

from app.db.mongo import get_collection
from app.schemas.performances import PerformanceIn, PerformanceUpdate


# ── Serialização ──────────────────────────────────────────────────────────────

def _to_out(doc: Dict[str, Any], session_count: int = 0) -> Dict[str, Any]:
    if not doc:
        return doc
    return {
        "id":            str(doc["_id"]),
        "name":          doc.get("name"),
        "synopsis":      doc.get("synopsis"),
        "tags":          doc.get("tags", []),
        "classification":doc.get("classification"),
        "season":        doc.get("season"),
        "dramaturgy":    doc.get("dramaturgy", []),
        "direction":     doc.get("direction", []),
        "cast":          doc.get("cast", []),
        "crew":          doc.get("crew", []),
        "banner_url":    doc.get("banner_url"),
        "session_count": session_count,
        "created_at":    doc.get("created_at"),
        "updated_at":    doc.get("updated_at"),
    }


def _parse_oid(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except (bson_errors.InvalidId, TypeError):
        raise ValueError(f"id inválido: {id!r}")


# ── Repositório ───────────────────────────────────────────────────────────────

class PerformancesRepository:

    @property
    def col(self):
        return get_collection("performances")

    # ── Índices ───────────────────────────────────────────────────────────────

    async def ensure_indexes(self) -> None:
        existing = await self.col.index_information()
        # Recria índice de texto apenas se não existir com o nome correto
        if "performance_text_search" not in existing:
            # Remove qualquer índice textual antigo
            for name, info in existing.items():
                if info.get("weights"):
                    await self.col.drop_index(name)
            await self.col.create_index(
                [("name", "text"), ("synopsis", "text"), ("tags", "text")],
                name="performance_text_search",
            )

    # ── Listagem ──────────────────────────────────────────────────────────────

    async def list(
        self,
        q: Optional[str] = None,
        season: Optional[int] = None,
        classification: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        filt: Dict[str, Any] = {}

        if q:
            filt["$text"] = {"$search": q}
        if season:
            filt["season"] = season
        if classification:
            filt["classification"] = classification

        cursor = self.col.find(filt).sort("name", 1).skip(skip).limit(limit)
        return [_to_out(doc) async for doc in cursor]

    # ── Busca por ID ──────────────────────────────────────────────────────────

    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        oid = _parse_oid(id)
        doc = await self.col.find_one({"_id": oid})
        return _to_out(doc) if doc else None

    # ── Criação ───────────────────────────────────────────────────────────────

    async def create(self, payload: PerformanceIn) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        data = payload.model_dump()
        data["created_at"] = now
        data["updated_at"] = now

        res = await self.col.insert_one(data)
        doc = await self.col.find_one({"_id": res.inserted_id})
        return _to_out(doc)

    # ── Atualização ───────────────────────────────────────────────────────────

    async def update(self, id: str, payload: PerformanceUpdate) -> Optional[Dict[str, Any]]:
        oid = _parse_oid(id)
        updates = payload.model_dump(exclude_none=True)

        if not updates:
            # Nada para atualizar — retorna o doc atual
            doc = await self.col.find_one({"_id": oid})
            return _to_out(doc) if doc else None

        updates["updated_at"] = datetime.now(timezone.utc)

        doc = await self.col.find_one_and_update(
            {"_id": oid},
            {"$set": updates},
            return_document=True,
        )
        return _to_out(doc) if doc else None

    # ── Remoção ───────────────────────────────────────────────────────────────

    async def delete(self, id: str) -> bool:
        oid = _parse_oid(id)
        result = await self.col.delete_one({"_id": oid})
        return result.deleted_count == 1