"""
performances.py (schema)
Performances agora são APENAS metadados.
Sessões vivem exclusivamente na coleção `sessions` (sessions_repo).
O campo `banner` passou de base64 → URL relativa do arquivo no disco.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# ── Crew ──────────────────────────────────────
class CrewRole(BaseModel):
    role: str
    people: List[str] = Field(default_factory=list)


# ── Performance (entrada) ─────────────────────
class PerformanceIn(BaseModel):
    name: str
    synopsis: str
    tags: List[str] = Field(default_factory=list)
    classification: str
    season: int
    dramaturgy: List[str] = Field(default_factory=list)
    direction: List[str] = Field(default_factory=list)
    cast: List[str] = Field(default_factory=list)
    crew: List[CrewRole] = Field(default_factory=list)

    # URL relativa retornada pelo endpoint POST /media/upload
    # Ex: "static/uploads/banners/abc123.jpg"
    # None = sem banner ainda
    banner_url: Optional[str] = Field(
        default=None,
        description="Path relativo da imagem (retornado por POST /media/upload)"
    )


# ── Performance (saída) ───────────────────────
class PerformanceOut(PerformanceIn):
    id: str = Field(serialization_alias="_id")
    # campo informativo: total de sessões (preenchido pelo repo, não salvo no doc)
    session_count: int = 0
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(populate_by_name=True)


# ── Performance (atualização parcial) ─────────
class PerformanceUpdate(BaseModel):
    name: Optional[str] = None
    synopsis: Optional[str] = None
    tags: Optional[List[str]] = None
    classification: Optional[str] = None
    season: Optional[int] = None
    dramaturgy: Optional[List[str]] = None
    direction: Optional[List[str]] = None
    cast: Optional[List[str]] = None
    crew: Optional[List[CrewRole]] = None
    banner_url: Optional[str] = None