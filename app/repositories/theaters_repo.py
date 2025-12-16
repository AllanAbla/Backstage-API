from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.theater import Theater
from app.schemas.theaters import TheaterCreate, TheaterUpdate
import unicodedata
import re

def _slugify(value: str) -> str:
  """
  Gera um slug simples a partir do nome:
  - remove acentos
  - minúsculas
  - troca espaços por "-"
  """
  value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
  value = re.sub(r"[^\w\s-]", "", value).strip().lower()
  value = re.sub(r"[\s_-]+", "-", value)
  return value or "theater"

def _to_public(obj: Theater) -> Dict[str, Any]:
    address = {
        "street": obj.street or "",
        "number": obj.number or "",
        "neighborhood": obj.neighborhood,
        "city": obj.city or "",
        "state": obj.state or "",
        "postal_code": obj.postal_code,
        "country": obj.country or "BR",
    }

    location = None
    if obj.lng is not None and obj.lat is not None:
        location = {"type": "Point", "coordinates": [obj.lng, obj.lat]}

    contacts = None
    if obj.website or obj.instagram or obj.phone:
        contacts = {
            "website": obj.website,
            "instagram": obj.instagram,
            "phone": obj.phone,
        }

    return {
        "id": obj.id,
        "name": obj.name,
        "slug": obj.slug,
        "address": address,
        "location": location,
        "contacts": contacts,
        "photo_base64": obj.photo_base64,
    }

class TheatersRepo:
    """
    Repositório usando SQL (SQLAlchemy Async) para a entidade Theater.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        stmt = (
            select(Theater)
            .offset(skip)
            .limit(limit)
            .order_by(Theater.name)
        )
        result = await self.session.execute(stmt)
        theaters = result.scalars().all()
        return [_to_public(t) for t in theaters]

    async def get(self, id_: int | str) -> Optional[Dict[str, Any]]:
        try:
            pk = int(id_)
        except (ValueError, TypeError):
            return None
        obj = await self.session.get(Theater, pk)
        return _to_public(obj) if obj else None

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        name = data["name"]
        slug = data.get("slug") or _slugify(name)

        addr = data.get("address") or {}
        loc = data.get("location") or None
        contacts = data.get("contacts") or {}

        lng = lat = None
        if loc and isinstance(loc.get("coordinates"), (list, tuple)) and len(loc["coordinates"]) >= 2:
            lng = float(loc["coordinates"][0])
            lat = float(loc["coordinates"][1])

        obj = Theater(
            name=name,
            slug=slug,
            street=addr.get("street"),
            number=addr.get("number"),
            neighborhood=addr.get("neighborhood"),
            city=addr.get("city"),
            state=addr.get("state"),
            postal_code=addr.get("postal_code"),
            country=addr.get("country"),
            lng=lng,
            lat=lat,
            website=(contacts.get("website") or None),
            instagram=(contacts.get("instagram") or None),
            phone=(contacts.get("phone") or None),
            photo_base64=data.get("photo_base64"),
        )

        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return _to_public(obj)

    async def update(self, id_: int | str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            pk = int(id_)
        except (ValueError, TypeError):
            return None

        obj = await self.session.get(Theater, pk)
        if not obj:
            return None

        if "name" in data and isinstance(data["name"], str):
            new_name = data["name"].strip()
            if new_name and new_name != (obj.name or ""):
                obj.name = new_name
                obj.slug = _slugify(new_name)

        addr = data.get("address")
        if addr:
            obj.street = addr.get("street", obj.street)
            obj.number = addr.get("number", obj.number)
            obj.neighborhood = addr.get("neighborhood", obj.neighborhood)
            obj.city = addr.get("city", obj.city)
            obj.state = addr.get("state", obj.state)
            obj.postal_code = addr.get("postal_code", obj.postal_code)
            obj.country = addr.get("country", obj.country)

        loc = data.get("location")
        if loc and isinstance(loc.get("coordinates"), (list, tuple)) and len(loc["coordinates"]) >= 2:
            obj.lng = float(loc["coordinates"][0])
            obj.lat = float(loc["coordinates"][1])

        contacts = data.get("contacts")
        if contacts is not None:
            obj.website = contacts.get("website", obj.website)
            obj.instagram = contacts.get("instagram", obj.instagram)
            obj.phone = contacts.get("phone", obj.phone)

        if "photo_base64" in data:
            obj.photo_base64 = data["photo_base64"]

        await self.session.commit()
        await self.session.refresh(obj)
        return _to_public(obj)

    async def delete(self, id_: int | str) -> bool:
        try:
            pk = int(id_)
        except (ValueError, TypeError):
            return False

        obj = await self.session.get(Theater, pk)
        if not obj:
            return False

        await self.session.delete(obj)
        await self.session.commit()
        return True
