from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import communities, community, rag

app = FastAPI(title="BNHS Code for Good API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(communities.router)
app.include_router(community.router)
app.include_router(rag.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
