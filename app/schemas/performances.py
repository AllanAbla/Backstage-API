from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
import base64

class CrewRole(BaseModel):
    role: str
    people: List[str] = Field(default_factory=list)  # 1..N nomes

class SessionIn(BaseModel):
    theater_id: str  # validaremos como ObjectId
    when: datetime   # DATETIME (permite sessões no mesmo dia: 17:00, 21:00 etc.)

    @field_validator("theater_id")
    @classmethod
    def validate_oid(cls, v: str) -> str:
        from bson import ObjectId
        s = str(v)
        if not ObjectId.is_valid(s):
            raise ValueError("ObjectId inválido")
        return s

def _is_base64(s: str) -> bool:
    try:
        # aceita data URLs (data:image/png;base64,xxx)
        if s.startswith("data:") and ";base64," in s:
            s = s.split(";base64,", 1)[1]
        base64.b64decode(s, validate=True)
        return True
    except Exception:
        return False

class PerformanceIn(BaseModel):
    name: str
    synopsis: str
    tags: List[str] = Field(default_factory=list)
    classification: str        # "Livre", "10", "12", "14", "16", "18"
    season: int                # ano da apresentação (retornos em anos diferentes = novo item)
    dramaturgy: List[str] = Field(default_factory=list)
    direction: List[str] = Field(default_factory=list)
    cast: List[str] = Field(default_factory=list)
    crew: List[CrewRole] = Field(default_factory=list)
    sessions: List[SessionIn] = Field(default_factory=list)
    banner: Optional[str] = Field(default=None, description="Imagem base64 (ou data URL)")

    @field_validator("banner")
    @classmethod
    def validate_banner(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not _is_base64(v):
            raise ValueError("banner precisa ser base64 válido (pode ser data URL)")
        # limite de tamanho opcional (ex.: 5 MB => ~6.6 MB em base64)
        if len(v) > 7_000_000:
            raise ValueError("banner muito grande (limite ~7MB em base64)")
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
    sessions: Optional[List[SessionIn]] = None
    banner: Optional[str] = None