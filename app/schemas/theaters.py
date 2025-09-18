from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from .common import Address, GeoPoint, Contacts

class TheaterIn(BaseModel):
    name: str
    slug: str = Field(description="URL-friendly unique slug")
    address: Address
    location: GeoPoint
    contacts: Contacts | None = None

class TheaterOut(TheaterIn):
    id: str = Field(serialization_alias="_id")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(populate_by_name=True)

class TheaterUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    address: Optional[Address] = None
    location: Optional[GeoPoint] = None
    contacts: Optional[Contacts] = None
