import json
import pathlib
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.db.sql import AsyncSessionLocal
from app.models.theater import Theater
from app.repositories.theaters_repo import _slugify

FILE = pathlib.Path(__file__).with_name("theaters.json")

async def seed_sql():
    async with AsyncSessionLocal() as session:
        # limpar tabela
        await session.execute(delete(Theater))
        await session.commit()

        data = json.loads(FILE.read_text(encoding="utf-8"))
        items = []

        for item in data:
            name = item["name"]

            # address
            addr = item.get("address", {})
            street = addr.get("street")
            neighborhood = addr.get("neighborhood")
            city = addr.get("city")
            state = addr.get("state")
            postal_code = addr.get("postal_code")
            country = addr.get("country")

            # location
            loc = item.get("location", {})
            coords = loc.get("coordinates") or [None, None]
            lng, lat = coords

            # contacts
            contacts = item.get("contacts", {})
            website = contacts.get("website")
            instagram = contacts.get("instagram")
            phone = contacts.get("phone")

            slug = item.get("slug") or _slugify(name)

            t = Theater(
                name=name,
                slug=slug,
                street=street,
                neighborhood=neighborhood,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                lng=lng,
                lat=lat,
                website=website,
                instagram=instagram,
                phone=phone,
                photo_base64=None,  # não existe no JSON original
            )
            session.add(t)

        await session.commit()
        print(f"Seeded {len(data)} theaters into SQL.")

def main():
    asyncio.run(seed_sql())

if __name__ == "__main__":
    main()
