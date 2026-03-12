"""
app/schemas/performances.py

Novos campos:
  - duration_minutes: int | None  → duração da peça em minutos
  - ticket_links: List[TicketLink] → um link por teatro; url pode ser None
    quando o link ainda não foi divulgado (has_link=False)
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime


# ── Crew ──────────────────────────────────────────────────────────────────────

class CrewRole(BaseModel):
    role: str
    people: List[str] = Field(default_factory=list)


# ── TicketLink ────────────────────────────────────────────────────────────────

class TicketLink(BaseModel):
    """
    Associa um teatro a um link de compra de ingressos dentro de uma performance.

    Campos:
        theater_id  — ObjectId (str) do teatro onde a temporada acontece
        theater_name — nome do teatro (desnormalizado para exibição sem join)
        url         — URL da bilheteria; None quando ainda não divulgado
    """
    theater_id:   str
    theater_name: str = ""
    url:          Optional[str] = Field(
        default=None,
        description="URL da bilheteria. None = link ainda não divulgado."
    )


# ── Performance (entrada) ─────────────────────────────────────────────────────

class PerformanceIn(BaseModel):
    name:            str
    synopsis:        str
    tags:            List[str]      = Field(default_factory=list)
    classification:  str
    season:          int
    duration_minutes: Optional[int] = Field(
        default=None,
        ge=1,
        description="Duração em minutos. None = não informado."
    )
    dramaturgy:      List[str]      = Field(default_factory=list)
    direction:       List[str]      = Field(default_factory=list)
    cast:            List[str]      = Field(default_factory=list)
    crew:            List[CrewRole] = Field(default_factory=list)
    ticket_links:    List[TicketLink] = Field(
        default_factory=list,
        description="Um item por teatro; url=None quando link ainda não divulgado."
    )
    banner_url:      Optional[str]  = Field(
        default=None,
        description="Path relativo da imagem (retornado por POST /media/upload)"
    )


# ── Performance (saída) ───────────────────────────────────────────────────────

class PerformanceOut(PerformanceIn):
    id:            str = Field(serialization_alias="_id")
    session_count: int = 0
    created_at:    datetime
    updated_at:    datetime
    model_config = ConfigDict(populate_by_name=True)


# ── Performance (atualização parcial) ─────────────────────────────────────────

class PerformanceUpdate(BaseModel):
    name:             Optional[str]             = None
    synopsis:         Optional[str]             = None
    tags:             Optional[List[str]]        = None
    classification:   Optional[str]             = None
    season:           Optional[int]             = None
    duration_minutes: Optional[int]             = Field(default=None, ge=1)
    dramaturgy:       Optional[List[str]]        = None
    direction:        Optional[List[str]]        = None
    cast:             Optional[List[str]]        = None
    crew:             Optional[List[CrewRole]]   = None
    ticket_links:     Optional[List[TicketLink]] = None
    banner_url:       Optional[str]             = None