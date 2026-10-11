"""Observation image uploads, stored on disk under DATA_DIR/uploads."""

import re
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse

from app.core.auth import CurrentUser, get_current_user
from app.core.config import get_settings
from app.core.security import limiter

router = APIRouter(prefix="/uploads", tags=["uploads"])

MAX_IMAGE_BYTES = 5 * 1024 * 1024
STORED_NAME = re.compile(r"^[A-Za-z0-9_-]{16,64}\.(jpg|png|gif|webp)$")
MEDIA_TYPES = {"jpg": "image/jpeg", "png": "image/png", "gif": "image/gif", "webp": "image/webp"}


def _uploads_dir() -> Path:
    path = Path(get_settings().data_dir) / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _sniff_extension(head: bytes) -> str | None:
    """Trust the file's bytes, not its name or the client's Content-Type."""
    if head.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    return None


@router.post("", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    _user: CurrentUser = Depends(get_current_user),
):
    data = await file.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image is larger than 5 MB"
        )
    extension = _sniff_extension(data[:16])
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, GIF or WebP images can be uploaded",
        )

    name = f"{secrets.token_urlsafe(18)}.{extension}"
    (_uploads_dir() / name).write_bytes(data)
    return {"url": f"/api/uploads/{name}"}


@router.get("/{name}")
async def get_image(name: str):
    if not STORED_NAME.match(name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    path = _uploads_dir() / name
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return FileResponse(
        path,
        media_type=MEDIA_TYPES[name.rsplit(".", 1)[1]],
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
