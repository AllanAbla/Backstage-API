from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sql import get_session
from app.repositories.theaters_repo import TheatersRepo
from app.schemas.theaters import TheaterCreate, TheaterUpdate

router = APIRouter()

def get_repo(session: AsyncSession = Depends(get_session)) -> TheatersRepo:
    return TheatersRepo(session)

@router.get("/theaters")
async def list_theaters(
    repo: TheatersRepo = Depends(get_repo),
    limit: int = 100,
    skip: int = 0,
):
    return await repo.list(limit=limit, skip=skip)

@router.get("/theaters/{id}")
async def get_theater(id: str, repo: TheatersRepo = Depends(get_repo)):
    theater = await repo.get(id)
    if not theater:
        raise HTTPException(status_code=404, detail="Teatro não encontrado")
    return theater

@router.post("/theaters", status_code=201)
async def create_theater(payload: TheaterCreate, repo: TheatersRepo = Depends(get_repo)):
    data = jsonable_encoder(payload, exclude_none=True)
    return await repo.create(data)

@router.patch("/theaters/{id}")
async def update_theater(id: str, payload: TheaterUpdate, repo: TheatersRepo = Depends(get_repo)):
    data = jsonable_encoder(payload, exclude_none=True)
    data.pop("id", None)
    updated = await repo.update(id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Teatro não encontrado")
    return updated

@router.delete("/theaters/{id}", status_code=204)
async def delete_theater(id: str, repo: TheatersRepo = Depends(get_repo)):
    ok = await repo.delete(id)
    if not ok:
        raise HTTPException(status_code=404, detail="Teatro não encontrado")
    return