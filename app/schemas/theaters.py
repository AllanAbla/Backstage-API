from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl

# --------- auxiliares ---------
class Address(BaseModel):
    street: str
    number: str
    neighborhood: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str

class Location(BaseModel):
    type: str = Field("Point", pattern="^Point$")
    # [lng, lat]
    coordinates: List[float] = Field(..., min_items=2, max_items=2)

class Contacts(BaseModel):
    website: Optional[HttpUrl] = None
    instagram: Optional[str] = None
    phone: Optional[str] = None

class TheaterBase(BaseModel):
    name: str
    slug: Optional[str] = None
    address: Address
    location: Optional[Location] = None
    contacts: Optional[Contacts] = None
    photo_base64: Optional[str] = None

class TheaterCreate(TheaterBase):
    """Schema usado no POST /theaters."""
    pass

class TheaterIn(TheaterCreate):
    """Alias de compatibilidade (antigo nome usado pelo projeto)."""
    pass

class TheaterUpdate(BaseModel):
    """Schema usado no PATCH /theaters."""
    name: Optional[str] = None
    slug: Optional[str] = None
    address: Optional[Address] = None
    location: Optional[Location] = None
    contacts: Optional[Contacts] = None
    photo_base64: Optional[str] = None

class TheaterOut(TheaterBase):
    id: int

    class Config:
        from_attributes = True