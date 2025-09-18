from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator

class Address(BaseModel):
    street: str
    neighborhood: str
    city: str
    state: str
    postal_code: str
    country: str = Field(default="BR", min_length=2, max_length=2)

class GeoPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float]  # [lng, lat]

    @field_validator("coordinates")
    @classmethod
    def validate_coords(cls, v):
        if len(v) != 2:
            raise ValueError("coordinates must be [lng, lat]")
        lng, lat = v
        if not (-180 <= lng <= 180 and -90 <= lat <= 90):
            raise ValueError("invalid lng/lat values")
        return v

class Contacts(BaseModel):
    website: Optional[HttpUrl] = None
    phone: Optional[str] = None
    email: Optional[str] = None