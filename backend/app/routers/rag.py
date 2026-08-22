from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import CurrentUser, require_role
from app.models.schema import RagAnswer, RagQuery
from app.services import rag_pipeline

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest(document_id: str, user: CurrentUser = Depends(require_role("staff"))):
    try:
        chunk_count = rag_pipeline.ingest_document(document_id)
    except NotImplementedError:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="RAG ingestion not yet wired up")
    return {"document_id": document_id, "chunks": chunk_count}


@router.post("/query", response_model=RagAnswer)
async def query(body: RagQuery):
    try:
        return rag_pipeline.answer_question(body.question)
    except NotImplementedError:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="RAG query not yet wired up")
