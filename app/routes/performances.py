from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.performances import PerformanceIn, PerformanceOut, PerformanceUpdate
from app.repositories.performances_repo import PerformancesRepository

router = APIRouter(prefix="/performances", tags=["performances"])
repo = PerformancesRepository()

@router.on_event("startup")
async def ensure_indexes():
    await repo.ensure_indexes()

@router.get(
    "",
    response_model=List[PerformanceOut],
    response_model_by_alias=True,
)
async def list_performances(
    q: Optional[str] = Query(None, description="Busca por nome/sinopse/tags"),
    season: Optional[int] = Query(None, description="Ano da temporada"),
    classification: Optional[str] = None,
    theater_id: Optional[str] = Query(None, description="Filtra performances por teatro"),
    date_from: Optional[datetime] = Query(None, description="Sessões a partir de (UTC)"),
    date_to: Optional[datetime] = Query(None, description="Sessões até (UTC)"),
    tags: Optional[List[str]] = Query(None, description="todas as tags devem bater"),
    skip: int = 0,
    limit: int = 50,
):
    return await repo.list(q, season, classification, theater_id, date_from, date_to, tags, skip, limit)

@router.get(
    "/{id}",
    response_model=PerformanceOut,
    response_model_by_alias=True,
)
async def get_performance(id: str):
    doc = await repo.get(id)
    if not doc:
        raise HTTPException(status_code=404, detail="Performance not found")
    return doc

@router.post(
    "",
    response_model=PerformanceOut,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_performance(payload: PerformanceIn):
    try:
        return await repo.create(payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.patch(
    "/{id}",
    response_model=PerformanceOut,
    response_model_by_alias=True,
)
async def update_performance(id: str, payload: PerformanceUpdate):
    try:
        updated = await repo.update(id, payload)
    except ValueError as ve:
        msg = str(ve)
        if "id inválido" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    if not updated:
        raise HTTPException(status_code=404, detail="Performance not found")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_performance(id: str):
    try:
        ok = await repo.delete(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="id inválido")
    if not ok:
        raise HTTPException(status_code=404, detail="Performance not found")
    return None