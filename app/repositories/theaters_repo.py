from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from bson import ObjectId
from pymongo import ReturnDocument


class TheatersRepo:
    def __init__(self, db):
        self.db = db
        self.col = db["theaters"]

    # -------- helpers --------

    def _ensure_object_id(self, id_str: Union[str, ObjectId]) -> ObjectId:
        if isinstance(id_str, ObjectId):
            return id_str
        return ObjectId(str(id_str))

    def _to_public(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Converte o documento do Mongo em um dicionário serializável:
        - _id (ObjectId) -> id (str)
        - remove campos que não podem ser serializados
        """
        if not doc:
            return None
        d = dict(doc)
        _id = d.pop("_id", None)
        if isinstance(_id, ObjectId):
            d["id"] = str(_id)
        elif _id is not None:
            d["id"] = str(_id)

        # Se por acaso houver ObjectId em outros campos, converta aqui (raro neste schema)
        # Exemplo:
        # if isinstance(d.get("owner_id"), ObjectId):
        #     d["owner_id"] = str(d["owner_id"])

        return d

    def _sanitize_updatable_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        clean = dict(data or {})
        clean.pop("_id", None)
        clean.pop("id", None)
        contacts = clean.get("contacts")
        if isinstance(contacts, dict):
            website = contacts.get("website")
            if website is not None and not isinstance(website, str):
                contacts["website"] = str(website)
            clean["contacts"] = contacts
        return clean

    async def _maybe_await(self, maybe_coro):
        try:
            return await maybe_coro  # Motor
        except TypeError:
            return maybe_coro        # PyMongo

    # -------- CRUD --------

    async def list(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        cursor = self.col.find({}).skip(skip).limit(limit)

        items: List[Dict[str, Any]] = []
        try:
            async for doc in cursor:  # Motor
                items.append(self._to_public(doc))
        except TypeError:
            for doc in cursor:        # PyMongo
                items.append(self._to_public(doc))
        return items

    async def get(self, id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        oid = self._ensure_object_id(id)
        doc = await self._maybe_await(self.col.find_one({"_id": oid}))
        return self._to_public(doc)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.utcnow()
        payload = dict(data or {})
        payload.pop("_id", None)
        payload.pop("id", None)
        payload["created_at"] = now
        payload["updated_at"] = now

        result = await self._maybe_await(self.col.insert_one(payload))
        inserted_id = getattr(result, "inserted_id", None)
        return await self.get(inserted_id)

    async def update(self, id: Union[str, ObjectId], data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        oid = self._ensure_object_id(id)
        clean = self._sanitize_updatable_fields(data)
        update_doc = {"$set": {**clean, "updated_at": datetime.utcnow()}}

        doc = await self._maybe_await(
            self.col.find_one_and_update(
                {"_id": oid},
                update_doc,
                return_document=ReturnDocument.AFTER,
            )
        )
        return self._to_public(doc)

    async def delete(self, id: Union[str, ObjectId]) -> bool:
        oid = self._ensure_object_id(id)
        result = await self._maybe_await(self.col.delete_one({"_id": oid}))
        return bool(getattr(result, "deleted_count", 0))
