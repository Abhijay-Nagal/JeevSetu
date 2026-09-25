from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.security import setup_security
from app.routers import analytics, auth_email, communities, community, rag, research, rewards

app = FastAPI(title="BNHS Code for Good API")

# --- CORS --- tightened from allow_origins=["*"] to configurable origins.
# Set ALLOWED_ORIGINS in .env (comma-separated) for production.
settings = get_settings()
origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --- Security middleware (rate limiting, security headers, threat logging) ---
setup_security(app)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all so CORS headers are still sent on 500s.

    Without this, an unhandled exception bypasses CORSMiddleware entirely
    (Starlette's ServerErrorMiddleware sits outside it), so the browser
    reports it as a CORS failure instead of showing the real 500.
    """
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": origins[0] if origins else "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


app.include_router(analytics.router, prefix="/api")
app.include_router(auth_email.router, prefix="/api")
app.include_router(communities.router, prefix="/api")
app.include_router(community.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(research.router, prefix="/api")
app.include_router(rewards.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}

