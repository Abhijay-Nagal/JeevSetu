from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import communities, community, rag

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
    """Catch-all handler so CORS headers are still sent even on 500 errors.

    Without this, Starlette's CORSMiddleware never gets to write the
    response headers when an unhandled exception bubbles up, which makes
    the browser report the error as a CORS failure instead of a 500.
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


app.include_router(communities.router)
app.include_router(community.router)
app.include_router(rag.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
