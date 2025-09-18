from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.schemas import TheaterIn, TheaterOut, TheaterUpdate  # <- AQUI
from app.repositories.theaters_repo import TheatersRepository  # <- AQUI

router = APIRouter(prefix="/theaters", tags=["theaters"])
repo = TheatersRepository()

@router.on_event("startup")
async def ensure_indexes():
    await repo.ensure_indexes()

@router.get("", response_model=List[TheaterOut], response_model_by_alias=True,)
async def list_theaters(
    q: Optional[str] = Query(None, description="Busca por nome"),
    city: Optional[str] = None,
    state: Optional[str] = None,
    neighborhood: Optional[str] = None,
    slug: Optional[str] = None,
    near_lat: Optional[float] = Query(None, description="Latitude para busca geográfica"),
    near_lng: Optional[float] = Query(None, description="Longitude para busca geográfica"),
    max_distance_m: Optional[int] = Query(3000, description="Distância máxima em metros"),
    skip: int = 0,
    limit: int = 50,
):
    return await repo.list(q, city, state, neighborhood, slug, near_lat, near_lng, max_distance_m or 3000, skip, limit)

@router.get("/{id_or_slug}", response_model=TheaterOut, response_model_by_alias=True,)
async def get_theater(id_or_slug: str):
    doc = await repo.get(id_or_slug)
    if not doc:
        raise HTTPException(status_code=404, detail="Theater not found")
    return doc

@router.post("", response_model=TheaterOut, status_code=status.HTTP_201_CREATED)
async def create_theater(payload: TheaterIn):
    try:
        return await repo.create(payload)
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(status_code=409, detail="Slug já existe")
        raise

@router.patch("/{id}", response_model=TheaterOut)
async def update_theater(id: str, payload: TheaterUpdate):
    try:
        updated = await repo.update(id, payload)
    except ValueError as ve:
        msg = str(ve)
        if "id inválido" in msg:
            raise HTTPException(status_code=400, detail=msg)
        if "nada para atualizar" in msg:
            raise HTTPException(status_code=400, detail="Nada para atualizar")
        raise
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(status_code=409, detail="Slug já existe")
        raise
    if not updated:
        raise HTTPException(status_code=404, detail="Theater not found")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theater(id: str):
    try:
        ok = await repo.delete(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="id inválido")
    if not ok:
        raise HTTPException(status_code=404, detail="Theater not found")
    return None
