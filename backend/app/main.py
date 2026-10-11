import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import BACKEND_DIR, get_settings
from app.core.security import setup_security
from app.core.supabase_client import get_supabase
from app.routers import (
    analytics,
    auth_email,
    communities,
    community,
    engagement,
    rag,
    research,
    rewards,
    uploads,
)
from app.services import knowledge_base

logger = logging.getLogger(__name__)
settings = get_settings()

# Built frontend (npm run build). When present the API also serves the web
# app, so a single `uvicorn app.main:app` runs all of JeevSetu.
FRONTEND_DIST = (BACKEND_DIR.parent / "frontend" / "dist").resolve()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Build the search index up front so the first search isn't slow.
    knowledge_base.get_knowledge_base()
    if not settings.uses_supabase:
        get_supabase()  # opens the local store and seeds it if empty
    yield


app = FastAPI(title="JeevSetu API", lifespan=lifespan)

# --- CORS --- configurable origins; set ALLOWED_ORIGINS (comma-separated).
origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security middleware (rate limiting, security headers, threat logging) ---
setup_security(app)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all so CORS headers are still sent on 500s.

    Without this, an unhandled exception bypasses CORSMiddleware entirely
    (Starlette's ServerErrorMiddleware sits outside it), so the browser
    reports it as a CORS failure instead of showing the real 500. The
    exception text is logged, not returned -- it can contain internals.
    """
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    origin = request.headers.get("origin")
    headers = {"Access-Control-Allow-Origin": origin} if origin in origins else {}
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our side. Please try again."},
        headers=headers,
    )


for router in (
    analytics,
    auth_email,
    communities,
    community,
    engagement,
    rag,
    research,
    rewards,
    uploads,
):
    app.include_router(router.router, prefix="/api")


@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/{full_path:path}", include_in_schema=False)
async def frontend(full_path: str):
    """Serves the built single-page app; unknown paths get index.html so
    client-side routes like /explore-communities work on refresh."""
    if full_path.startswith("api/") or not (FRONTEND_DIST / "index.html").is_file():
        raise HTTPException(status_code=404, detail="Not found")
    candidate = (FRONTEND_DIST / full_path).resolve()
    if full_path and candidate.is_file() and candidate.is_relative_to(FRONTEND_DIST):
        return FileResponse(candidate)
    return FileResponse(FRONTEND_DIST / "index.html", headers={"Cache-Control": "no-cache"})
