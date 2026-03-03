import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.theaters import router as theaters_router
from app.routes.performances import router as performances_router
from app.routes.sessions import router as sessions_router
from app.routes.utils_address import router as utils_router
from app.routes.media import router as media_router
from app.db.sql import Base, engine
from app.core.config import settings  # veja nota abaixo

# Garante que a pasta de uploads existe antes de montar
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Backstage API", version="0.6.0")

# ── Static files ─────────────────────────────
# Imagens ficam em /static/uploads/<category>/<arquivo>
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── CORS (origens via env, não hardcoded) ────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,   # lista vinda do .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────
# Substituímos @app.on_event("startup") pelo lifespan moderno
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria tabelas SQL
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app.router.lifespan_context = lifespan

# ── Health ────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}

# ── Routers ───────────────────────────────────
app.include_router(theaters_router)
app.include_router(performances_router)
app.include_router(sessions_router)
app.include_router(utils_router)
app.include_router(media_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)