"""
routes/media.py
Upload de imagens (banner de performance, foto de teatro).
Armazena em /static/uploads/{category}/ e retorna a URL relativa.

Categorias suportadas: "banners" | "theaters"

O banco passa a guardar apenas o campo `image_url: str`, ex:
  "static/uploads/banners/abc123.jpg"

Para servir, o frontend acessa:
  GET http://localhost:8000/static/uploads/banners/abc123.jpg
"""
import uuid
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles  # montado em main.py

UPLOAD_ROOT = Path("static/uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 5
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

router = APIRouter(prefix="/media", tags=["Media"])


def _category_dir(category: str) -> Path:
    if category not in ("banners", "theaters"):
        raise HTTPException(status_code=400, detail="category deve ser 'banners' ou 'theaters'")
    d = UPLOAD_ROOT / category
    d.mkdir(parents=True, exist_ok=True)
    return d


@router.post("/upload", status_code=201)
async def upload_image(
    category: str = Form(..., description="'banners' ou 'theaters'"),
    file: UploadFile = File(...),
):
    """
    Recebe multipart/form-data com campo 'file' e 'category'.
    Retorna { url: "static/uploads/<category>/<uuid>.<ext>" }
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo não suportado: {file.content_type}. Use JPEG, PNG ou WebP."
        )

    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Limite: {MAX_SIZE_MB}MB."
        )

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    dest = _category_dir(category) / filename

    dest.write_bytes(content)

    relative_url = f"static/uploads/{category}/{filename}"
    return {"url": relative_url}


@router.delete("/upload")
async def delete_image(url: str):
    """
    Remove um arquivo pelo path relativo armazenado no banco.
    Exemplo: url = "static/uploads/banners/abc123.jpg"
    """
    path = Path(url)
    # Garante que está dentro de static/uploads (evita path traversal)
    try:
        path.resolve().relative_to(UPLOAD_ROOT.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Path inválido.")

    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    path.unlink()
    return {"deleted": url}