from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from app.repositories.theaters_repo import TheatersRepo 
from app.schemas.theaters import TheaterCreate, TheaterUpdate 
from app.dependencies import get_db

router = APIRouter()

def get_repo(db = Depends(get_db)) -> TheatersRepo:
    return TheatersRepo(db)

@router.get("/theaters")
async def list_theaters(repo: TheatersRepo = Depends(get_repo), limit: int = 100, skip: int = 0):
    return await repo.list(limit=limit, skip=skip)

@router.get("/theaters/{id}")
async def get_theater(id: str, repo: TheatersRepo = Depends(get_repo)):
    return await repo.get(id)

@router.post("/theaters", status_code=201)
async def create_theater(payload: TheaterCreate, repo: TheatersRepo = Depends(get_repo)):
    data = jsonable_encoder(payload, exclude_none=True)
    return await repo.create(data)

@router.patch("/theaters/{id}")
async def update_theater(id: str, payload: TheaterUpdate, repo: TheatersRepo = Depends(get_repo)):
    # serializa Pydantic -> tipos nativos (HttpUrl -> str, datetime -> iso, etc.)
    data = jsonable_encoder(payload, exclude_none=True)
    data.pop("_id", None)
    data.pop("id", None)
    updated = await repo.update(id, data)
    return updated

@router.delete("/theaters/{id}", status_code=204)
async def delete_theater(id: str, repo: TheatersRepo = Depends(get_repo)):
    ok = await repo.delete(id)
    if not ok:
        # você pode levantar HTTPException(404) se preferir
        return
    return