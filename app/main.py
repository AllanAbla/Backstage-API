import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from app.routes.theaters import router as theaters_router
from app.routes.performances import router as performances_router

app = FastAPI(title="Backstage API", version="0.4.0")

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(theaters_router)
app.include_router(performances_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)