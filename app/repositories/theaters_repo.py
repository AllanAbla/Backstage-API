from typing import Any, Dict, List, Optional
from bson import ObjectId
from datetime import datetime
from app.db.mongo import get_collection
from app.schemas.theaters import TheaterIn, TheaterUpdate

def _to_out(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    return {
        "id": str(doc.get("_id")),
        "name": doc.get("name"),
        "slug": doc.get("slug"),
        "address": doc.get("address"),
        "location": doc.get("location"),
        "contacts": doc.get("contacts"),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }

class TheatersRepository:
    @property
    def col(self):
        return get_collection("theaters")

    async def ensure_indexes(self):
        await self.col.create_index("slug", unique=True)
        await self.col.create_index([("location", "2dsphere")])

    async def list(
        self,
        q: Optional[str],
        city: Optional[str],
        state: Optional[str],
        neighborhood: Optional[str],
        slug: Optional[str],
        near_lat: Optional[float],
        near_lng: Optional[float],
        max_distance_m: int,
        skip: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        filt: Dict[str, Any] = {}
        if q:
            filt["name"] = {"$regex": q, "$options": "i"}
        if city:
            filt["address.city"] = city
        if state:
            filt["address.state"] = state
        if neighborhood:
            filt["address.neighborhood"] = neighborhood
        if slug:
            filt["slug"] = slug
        if near_lat is not None and near_lng is not None:
            filt["location"] = {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [near_lng, near_lat]},
                    "$maxDistance": max_distance_m,
                }
            }
        cursor = self.col.find(filt).skip(skip).limit(min(limit, 200)).sort("name", 1)
        return [_to_out(doc) async for doc in cursor]

    async def get(self, id_or_slug: str) -> Dict[str, Any] | None:
        doc = None
        if ObjectId.is_valid(id_or_slug):
            doc = await self.col.find_one({"_id": ObjectId(id_or_slug)})
        if not doc:
            doc = await self.col.find_one({"slug": id_or_slug})
        return _to_out(doc) if doc else None

    async def create(self, payload: TheaterIn) -> Dict[str, Any]:
        now = datetime.utcnow()
        doc = payload.model_dump()
        doc["created_at"] = now
        doc["updated_at"] = now
        res = await self.col.insert_one(doc)
        inserted = await self.col.find_one({"_id": res.inserted_id})
        return _to_out(inserted)

    async def update(self, id: str, payload: TheaterUpdate) -> Dict[str, Any] | None:
        if not ObjectId.is_valid(id):
            raise ValueError("id inválido")
        updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
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