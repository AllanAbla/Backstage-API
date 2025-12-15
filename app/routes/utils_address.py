import re
import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/utils", tags=["utils"])

@router.get("/address-by-zip")
async def address_by_zip(
    country: str = Query(..., min_length=2, max_length=2),
    postal_code: str = Query(..., min_length=2),
):
    cc = country.upper().strip()
    code = postal_code.strip()

    async with httpx.AsyncClient(timeout=6) as client:
        if cc == "BR":
            cep = re.sub(r"\D", "", code)
            if len(cep) != 8:
                raise HTTPException(400, "CEP inválido")
            r = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
            data = r.json()
            if data.get("erro"):
                raise HTTPException(404, "Zip não encontrado")
            return {
                "street": data.get("logradouro") or "",
                "neighborhood": data.get("bairro"),
                "city": data.get("localidade") or "",
                "state": data.get("uf") or "",
                "postal_code": data.get("cep") or code,
                "country": "BR",
            }

        # Zippopotam (internacional)
        zip_clean = code.replace(" ", "")
        r = await client.get(f"https://api.zippopotam.us/{cc.lower()}/{zip_clean}")
        if r.status_code == 404:
            raise HTTPException(404, "Zip não encontrado")
        data = r.json()
        places = data.get("places") or []
        if not places:
            raise HTTPException(404, "Zip não encontrado")

        p = places[0]
        return {
            "street": "",              # normalmente não vem
            "neighborhood": None,      # normalmente não vem
            "city": p.get("place name") or "",
            "state": p.get("state abbreviation") or p.get("state") or "",
            "postal_code": data.get("post code") or zip_clean,
            "country": cc,
        }
