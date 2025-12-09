from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.db.sql import Base

class Theater(Base):
    __tablename__ = "theaters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)

    street = Column(String(255), nullable=True)
    number = Column(String(50), nullable=True)
    neighborhood = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(2), nullable=True, default="BR")

    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    website = Column(String(255), nullable=True)
    instagram = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    photo_base64 = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )