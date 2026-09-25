"""Security middleware — rate limiting, security headers, and optional threat logging.

All additive. Does not modify any existing router or service logic.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rate limiter (slowapi)
# ---------------------------------------------------------------------------

def _key_func(request: Request) -> str:
    """Rate-limit key: client IP address."""
    return get_remote_address(request)


limiter = Limiter(key_func=_key_func, default_limits=["60/minute"])


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom 429 response with CORS headers so the browser sees the real error."""
    _log_security_event(request, 429, "rate_limit_exceeded")
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
        headers={
            "Retry-After": "60",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds defensive HTTP headers to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # HSTS — only meaningful over HTTPS, harmless over HTTP
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


# ---------------------------------------------------------------------------
# Request logging middleware (optional threat logging)
# ---------------------------------------------------------------------------

class ThreatLoggingMiddleware(BaseHTTPMiddleware):
    """Logs 4xx/5xx responses for security monitoring.

    Writes to the `security_events` Supabase table if it exists; degrades
    gracefully (logs to stderr) if it doesn't.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000)

        if response.status_code >= 400:
            _log_security_event(
                request,
                response.status_code,
                _classify_event(response.status_code),
                duration_ms=duration_ms,
            )

        return response


def _classify_event(status_code: int) -> str:
    if status_code == 401:
        return "auth_failure"
    elif status_code == 403:
        return "forbidden"
    elif status_code == 429:
        return "rate_limit_exceeded"
    elif status_code >= 500:
        return "server_error"
    return "client_error"


def _log_security_event(
    request: Request,
    status_code: int,
    event_type: str,
    duration_ms: int | None = None,
) -> None:
    """Best-effort write to security_events table. Never raises."""
    client_ip = get_remote_address(request)
    path = request.url.path
    method = request.method

    logger.warning(
        "SECURITY [%s] %s %s %s -> %d (ip=%s)",
        event_type,
        method,
        path,
        f"({duration_ms}ms)" if duration_ms else "",
        status_code,
        client_ip,
    )

    try:
        from app.core.supabase_client import get_supabase
        supabase = get_supabase()
        supabase.table("security_events").insert({
            "event_type": event_type,
            "method": method,
            "path": path,
            "status_code": status_code,
            "client_ip": client_ip,
            "duration_ms": duration_ms,
        }).execute()
    except Exception:
        # Table might not exist yet — that's fine, we already logged to stderr.
        pass


# ---------------------------------------------------------------------------
# Setup helper
# ---------------------------------------------------------------------------

def setup_security(app: FastAPI) -> None:
    """Register all security middleware and handlers on the FastAPI app.

    Call this from main.py after creating the app instance.
    """
    settings = get_settings()

    # Update limiter default limits from config
    limiter._default_limits = [f"{settings.rate_limit_per_minute}/minute"]

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ThreatLoggingMiddleware)
