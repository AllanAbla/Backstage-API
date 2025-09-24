# app/schemas/theaters.py
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


# --------- schemas auxiliares ---------
class Address(BaseModel):
    street: str
    neighborhood: Optional[str] = None
    city: str
    state: str
    postal_code: Optional[str] = None
    country: Optional[str] = "BR"


class Location(BaseModel):
    type: str = Field(default="Point")
    coordinates: list[float]  # [longitude, latitude]


class Contacts(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None


# --------- schemas principais ---------
class TheaterBase(BaseModel):
    name: str
    slug: str
    address: Address
    location: Optional[Location] = None
    contacts: Optional[Contacts] = None


class TheaterCreate(TheaterBase):
    """Schema usado no POST /theaters"""
    pass

class TheaterIn(TheaterCreate):
    """Alias de compatibilidade (antigo nome usado pelo projeto)."""
    pass

class TheaterUpdate(BaseModel):
    """Schema usado no PATCH /theaters"""
    name: Optional[str] = None
    slug: Optional[str] = None
    address: Optional[Address] = None
    location: Optional[Location] = None
    contacts: Optional[Contacts] = None


# opcional: resposta para GET
class TheaterOut(TheaterBase):
    id: str

    class Config:
        from_attributes = True  # para funcionar com ORMs/ODM