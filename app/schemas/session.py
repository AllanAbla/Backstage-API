from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from bson import ObjectId
import uuid


# ======== Utilitário de ObjectId Pydantic ========
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any):
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("ObjectId inválido")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


def now_utc() -> datetime:
    return datetime.utcnow()


# ======== Schema de Sessão ========
class SessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    datetime: datetime
    theater_id: PyObjectId = Field(...)
    performance_id: Optional[PyObjectId] = None
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)
