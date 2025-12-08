from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
import base64


# ---------- CREW ----------
class CrewRole(BaseModel):
    role: str
    people: List[str] = Field(default_factory=list)


# ---------- SESSIONS ----------
class SessionIn(BaseModel):
    when: datetime


# ---------- THEATERS ----------
class TheaterBlock(BaseModel):
    theater_id: int                      # agora é inteiro (ID SQL)
    sessions: List[SessionIn] = Field(default_factory=list)


# ---------- HELPERS ----------
def _is_base64(s: str) -> bool:
    try:
        if s.startswith("data:") and ";base64," in s:
            s = s.split(";base64,", 1)[1]
        base64.b64decode(s, validate=True)
        return True
    except Exception:
        return False


# ---------- PERFORMANCE ----------
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

    # >>> AGORA: lista de blocos contendo theater_id (int) e sessões
    theaters: List[TheaterBlock] = Field(default_factory=list)

    banner: Optional[str] = Field(
        default=None,
        description="Imagem base64 (ou data URL)"
    )

    @field_validator("banner")
    @classmethod
    def validate_banner(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not _is_base64(v):
            raise ValueError("banner precisa ser base64 válido (pode ser data URL)")
        if len(v) > 7_000_000:
            raise ValueError("banner muito grande (limite ~7MB)")
        return v


class PerformanceOut(PerformanceIn):
    id: str = Field(serialization_alias="_id")
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(populate_by_name=True)


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

    # >>> atualização também usa theater_id = int
    theaters: Optional[List[TheaterBlock]] = None

    banner: Optional[str] = None
