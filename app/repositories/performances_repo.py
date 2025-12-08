from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from pymongo import ASCENDING, TEXT
from sqlalchemy import select
from app.db.mongo import get_collection
from app.db.sql import AsyncSessionLocal
from app.models.theater import Theater
from app.schemas.performances import PerformanceIn, PerformanceUpdate


def _to_out(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc

    sessions = []
    for s in doc.get("sessions", []) or []:
        sessions.append({
            "theater_id": s.get("theater_id"),   # agora é int
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

    async def _validate_theaters_sql(self, theater_ids: List[int]) -> List[int]:
        """
        Valida IDs de teatro consultando o banco SQL.
        Retorna lista de IDs inválidos.
        """
        if not theater_ids:
            return []

        async with AsyncSessionLocal() as session:
            stmt = select(Theater.id).where(Theater.id.in_(theater_ids))
            result = await session.execute(stmt)
            found = {row[0] for row in result.all()}

        missing = [tid for tid in theater_ids if tid not in found]
        return missing

    async def ensure_indexes(self):
        # remover índice antigo de texto, se existir
        indexes = await self.col.index_information()
        for name, info in indexes.items():
            if info.get("weights"):  # índice textual
                await self.col.drop_index(name)

        # agora cria APENAS UM índice textual
        await self.col.create_index(
            [
                ("name", "text"),
                ("synopsis", "text"),
                ("tags", "text")
            ],
            name="performance_text_search"
        )

    async def create(self, payload: PerformanceIn):
        now = datetime.utcnow()
        data = payload.model_dump()

        # pega IDs de teatro da performance inteira
        theater_ids = [block.theater_id for block in data.get("theaters", [])]

        missing = await self._validate_theaters_sql(theater_ids)
        if missing:
            raise ValueError(f"IDs de teatro inexistentes: {missing}")

        # sessions agora é convertida para:
        # { when: ..., theater_id: int }
        sessions = []
        for block in data.get("theaters", []):
            for s in block.get("sessions", []):
                sessions.append({
                    "when": s["when"],
                    "theater_id": block["theater_id"],   # int
                })

        data["sessions"] = sessions
        data.pop("theaters", None)

        data["created_at"] = now
        data["updated_at"] = now

        res = await self.col.insert_one(data)
        doc = await self.col.find_one({"_id": res.inserted_id})
        return _to_out(doc)

    async def update(self, id: str, payload: PerformanceUpdate):
        updates = payload.model_dump(exclude_none=True)

        if "theaters" in updates:
            new_blocks = updates["theaters"]
            theater_ids = [b.theater_id for b in new_blocks]

            missing = await self._validate_theaters_sql(theater_ids)
            if missing:
                raise ValueError(f"IDs de teatro inexistentes: {missing}")

            sessions = []
            for block in new_blocks:
                for s in block.sessions:
                    sessions.append({
                        "when": s.when,
                        "theater_id": block.theater_id,
                    })
            updates["sessions"] = sessions
            updates.pop("theaters", None)

        updates["updated_at"] = datetime.utcnow()

        doc = await self.col.find_one_and_update(
            {"_id": id},
            {"$set": updates},
            return_document=True
        )
        return _to_out(doc)
