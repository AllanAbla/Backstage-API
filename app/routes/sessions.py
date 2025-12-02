from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uuid
from bson import ObjectId

from app.repositories.sessions_repo import save_sessions, get_all_sessions, get_sessions_by_performance

router = APIRouter(prefix="/sessions", tags=["Sessions"])


class SessionRule(BaseModel):
    start_date: str
    end_date: str
    rules: Dict[int, List[str]]
    theater_id: str
    performance_id: str | None = None


class ManualSession(BaseModel):
    sessions: List[Dict[str, str]]
    theater_id: str
    performance_id: str | None = None


@router.post("/")
def create_sessions(data: dict):
    mode = data.get("mode")
    theater_id = data.get("theater_id")
    if not theater_id:
        raise HTTPException(status_code=400, detail="theater_id é obrigatório")

    sessions = []

    # === MODO POR REGRA ===
    if mode == "rule":
        rule_data = SessionRule(**data)
        start = datetime.fromisoformat(rule_data.start_date)
        end = datetime.fromisoformat(rule_data.end_date)
        current = start

        while current <= end:
            weekday = current.weekday()
            if str(weekday) in map(str, rule_data.rules.keys()):
                for hour in rule_data.rules[str(weekday)]:
                    dt = datetime.combine(
                        current.date(),
                        datetime.strptime(hour, "%H:%M").time()
                    )
                    sessions.append({
                        "id": str(uuid.uuid4()),
                        "datetime": dt,
                        "theater_id": ObjectId(rule_data.theater_id),
                        "performance_id": ObjectId(rule_data.performance_id)
                        if rule_data.performance_id and ObjectId.is_valid(rule_data.performance_id)
                        else None,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    })
            current += timedelta(days=1)

        save_sessions(sessions)
        return {"mode": "rule", "count": len(sessions), "sessions": sessions}

    # === MODO MANUAL ===
    elif mode == "manual":
        manual_data = ManualSession(**data)
        for s in manual_data.sessions:
            sessions.append({
                "id": str(uuid.uuid4()),
                "datetime": datetime.fromisoformat(f"{s['date']}T{s['hour']}:00"),
                "theater_id": ObjectId(manual_data.theater_id),
                "performance_id": ObjectId(manual_data.performance_id)
                if manual_data.performance_id and ObjectId.is_valid(manual_data.performance_id)
                else None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })

        save_sessions(sessions)
        return {"mode": "manual", "count": len(sessions), "sessions": sessions}

    else:
        raise HTTPException(status_code=400, detail="Modo inválido. Use 'rule' ou 'manual'.")


@router.get("/")
def list_sessions():
    return get_all_sessions()


@router.get("/by-performance/{performance_id}")
def list_by_performance(performance_id: str):
    return get_sessions_by_performance(performance_id)