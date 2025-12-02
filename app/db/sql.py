from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from app.core.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.sql_database_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

async def get_session() -> AsyncSession:
    """Dependency do FastAPI para injetar sessão SQL assíncrona."""
    async with AsyncSessionLocal() as session:
        yield session