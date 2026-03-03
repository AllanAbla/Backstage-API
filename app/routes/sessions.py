"""
routes/sessions.py
Sessões são a única fonte de verdade (coleção MongoDB independente).
Performances NÃO armazenam mais sessões embedded.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
from bson import ObjectId

import app.repositories.sessions_repo as repo

router = APIRouter(prefix="/sessions", tags=["Sessions"])


# ─────────────────────────────────────────────
# Schemas (movidos para cá de dentro da rota)
# ─────────────────────────────────────────────

class SessionOut(BaseModel):
    id: str
    performance_id: Optional[str]
    theater_id: int
    datetime: datetime
    created_at: datetime
    updated_at: datetime


class RulePayload(BaseModel):
    """Cria sessões por regra de recorrência semanal."""
    performance_id: str
    theater_id: int
    start_date: str          # "YYYY-MM-DD"
    end_date: str            # "YYYY-MM-DD"
    # chave = weekday (0=seg … 6=dom), valor = lista de horários "HH:MM"
    rules: Dict[int, List[str]]

    @field_validator("performance_id")
    @classmethod
    def valid_oid(cls, v: str) -> str:
        if not ObjectId.is_valid(v):
            raise ValueError("performance_id inválido")
        return v


class ManualPayload(BaseModel):
    """Cria sessões manualmente."""
    performance_id: str
    theater_id: int
    # lista de ISO datetime strings: "2025-10-04T20:00:00"
    datetimes: List[str]

    @field_validator("performance_id")
    @classmethod
    def valid_oid(cls, v: str) -> str:
        if not ObjectId.is_valid(v):
            raise ValueError("performance_id inválido")
        return v


# ─────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────

def _expand_rules(payload: RulePayload) -> List[dict]:
    """Expande regras de recorrência em lista de {performance_id, theater_id, datetime}."""
    start = datetime.fromisoformat(payload.start_date).replace(tzinfo=timezone.utc)
    end   = datetime.fromisoformat(payload.end_date).replace(tzinfo=timezone.utc)

    sessions = []
    current = start
    while current <= end:
        weekday = current.weekday()  # Python: 0=seg, 6=dom
        if weekday in payload.rules:
            for hour_str in payload.rules[weekday]:
                h, m = map(int, hour_str.split(":"))
                dt = current.replace(hour=h, minute=m, second=0, microsecond=0)
                sessions.append({
                    "performance_id": payload.performance_id,
                    "theater_id": payload.theater_id,
                    "datetime": dt,
                })
        current += timedelta(days=1)

    return sessions


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@router.on_event("startup")
async def startup():
    await repo.ensure_indexes()


@router.post("/rule", status_code=201, response_model=List[SessionOut])
async def create_by_rule(payload: RulePayload):
    """Gera sessões automaticamente a partir de regras semanais."""
    sessions = _expand_rules(payload)
    if not sessions:
        raise HTTPException(status_code=400, detail="Nenhuma sessão gerada. Verifique as datas e regras.")
    return await repo.bulk_insert(sessions)


@router.post("/manual", status_code=201, response_model=List[SessionOut])
async def create_manual(payload: ManualPayload):
    """Insere sessões em datas/horários específicos."""
    sessions = []
    for iso in payload.datetimes:
        try:
            dt = datetime.fromisoformat(iso).replace(tzinfo=timezone.utc)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"datetime inválido: {iso!r}")
        sessions.append({
            "performance_id": payload.performance_id,
            "theater_id": payload.theater_id,
            "datetime": dt,
        })

    if not sessions:
        raise HTTPException(status_code=400, detail="Lista de datetimes vazia.")

    return await repo.bulk_insert(sessions)


@router.get("", response_model=List[SessionOut])
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[datetime] = Query(None),
    date_to:   Optional[datetime] = Query(None),
):
    return await repo.list_all(skip=skip, limit=limit, date_from=date_from, date_to=date_to)


@router.get("/by-performance/{performance_id}", response_model=List[SessionOut])
async def by_performance(performance_id: str):
    if not ObjectId.is_valid(performance_id):
        raise HTTPException(status_code=400, detail="performance_id inválido")
    return await repo.list_by_performance(performance_id)


@router.get("/by-theater/{theater_id}", response_model=List[SessionOut])
async def by_theater(theater_id: int):
    return await repo.list_by_theater(theater_id)


@router.delete("/by-performance/{performance_id}")
async def delete_by_performance(performance_id: str):
    if not ObjectId.is_valid(performance_id):
        raise HTTPException(status_code=400, detail="performance_id inválido")
    count = await repo.delete_by_performance(performance_id)
    return {"deleted": count}


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str):
    try:
        ok = await repo.delete_one(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="session_id inválido")
    if not ok:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")