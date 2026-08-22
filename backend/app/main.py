from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import auth_email, communities, community, rag, research, rewards

app = FastAPI(title="BNHS Code for Good API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


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
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


app.include_router(auth_email.router)
app.include_router(communities.router)
app.include_router(community.router)
app.include_router(rag.router)
app.include_router(research.router)
app.include_router(rewards.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
