from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from bson import ObjectId
from pymongo import ASCENDING, TEXT
from app.db.mongo import get_collection
from app.schemas.performances import PerformanceIn, PerformanceUpdate

def _to_out(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    sessions = []
    for s in doc.get("sessions", []) or []:
        sessions.append({
            "theater_id": str(s.get("theater_id")) if s.get("theater_id") else None,
            "when": s.get("when"),
        })
    return {
        "id": str(doc.get("_id")),
        "name": doc.get("name"),
        "synopsis": doc.get("synopsis"),
        "tags": doc.get("tags", []),
        "classification": doc.get("classification"),
        "season": doc.get("season"),
        "dramaturgy": doc.get("dramaturgy", []),
        "direction": doc.get("direction", []),
        "cast": doc.get("cast", []),
        "crew": doc.get("crew", []),
        "sessions": sessions,
        "banner": doc.get("banner"),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }

class PerformancesRepository:
    @property
    def col(self):
        return get_collection("performances")

    @property
    def theaters_col(self):
        return get_collection("theaters")

    async def ensure_indexes(self):
        # texto para busca simples; índices por temporada, classificação e sessões
        await self.col.create_index([("name", TEXT), ("synopsis", TEXT), ("tags", TEXT)])
        await self.col.create_index([("season", ASCENDING)])
        await self.col.create_index([("classification", ASCENDING)])
        await self.col.create_index([("sessions.when", ASCENDING)])
        await self.col.create_index([("sessions.theater_id", ASCENDING)])

    async def _validate_theaters(self, theater_ids: List[ObjectId]) -> Tuple[bool, List[ObjectId]]:
        if not theater_ids:
            return True, []
        cursor = self.theaters_col.find({"_id": {"$in": theater_ids}}, {"_id": 1})
        found = {d["_id"] async for d in cursor}
        missing = [tid for tid in theater_ids if tid not in found]
        return (len(missing) == 0), missing

    async def list(
        self,
        q: Optional[str],
        season: Optional[int],
        classification: Optional[str],
        theater_id: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        tags: Optional[List[str]],
        skip: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        filt: Dict[str, Any] = {}
        if q:
            filt["$text"] = {"$search": q}
        if season is not None:
            filt["season"] = season
        if classification:
            filt["classification"] = classification
        if tags:
            filt["tags"] = {"$all": tags}

        session_and: List[Dict[str, Any]] = []
        if theater_id:
            if not ObjectId.is_valid(theater_id):
                return []
            session_and.append({"sessions.theater_id": ObjectId(theater_id)})
        if date_from or date_to:
            range_q: Dict[str, Any] = {}
            if date_from:
                range_q["$gte"] = date_from
            if date_to:
                range_q["$lte"] = date_to
            session_and.append({"sessions.when": range_q})
        if session_and:
            filt["$and"] = session_and if len(session_and) > 1 else session_and[0]

        cursor = self.col.find(filt).skip(skip).limit(min(limit, 200)).sort([("season", -1), ("name", 1)])
        return [_to_out(doc) async for doc in cursor]

    async def get(self, id: str) -> Dict[str, Any] | None:
        if ObjectId.is_valid(id):
            doc = await self.col.find_one({"_id": ObjectId(id)})
        else:
            doc = None
        return _to_out(doc) if doc else None

    async def create(self, payload: PerformanceIn) -> Dict[str, Any]:
        now = datetime.utcnow()
        data = payload.model_dump()
        theater_ids = []
        for s in data.get("sessions", []):
            s["theater_id"] = ObjectId(str(s["theater_id"]))
            theater_ids.append(s["theater_id"])
        ok, missing = await self._validate_theaters(theater_ids)
        if not ok:
            raise ValueError(f"theater_id(s) inexistente(s): {[str(m) for m in missing]}")
        data["created_at"] = now
        data["updated_at"] = now
        res = await self.col.insert_one(data)
        inserted = await self.col.find_one({"_id": res.inserted_id})
        return _to_out(inserted)

    async def update(self, id: str, payload: PerformanceUpdate) -> Dict[str, Any] | None:
        if not ObjectId.is_valid(id):
            raise ValueError("id inválido")
        updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
        if "sessions" in updates and updates["sessions"] is not None:
            theater_ids = []
            for s in updates["sessions"]:
                s["theater_id"] = ObjectId(str(s["theater_id"]))
                theater_ids.append(s["theater_id"])
            ok, missing = await self._validate_theaters(theater_ids)
            if not ok:
                raise ValueError(f"theater_id(s) inexistente(s): {[str(m) for m in missing]}")
        if not updates:
            raise ValueError("nada para atualizar")
        updates["updated_at"] = datetime.utcnow()
        doc = await self.col.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": updates},
            return_document=True,
        )
        return _to_out(doc) if doc else None

    async def delete(self, id: str) -> bool:
        if not ObjectId.is_valid(id):
            raise ValueError("id inválido")
        res = await self.col.delete_one({"_id": ObjectId(id)})
        return res.deleted_count > 0