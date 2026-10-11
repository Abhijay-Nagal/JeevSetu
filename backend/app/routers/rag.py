from fastapi import APIRouter, Request

from app.core.security import limiter
from app.models.schema import (
    AskRequest,
    AskResponse,
    NextStepsQuery,
    NextStepsResponse,
    QuizQuery,
    QuizResponse,
    SearchQuery,
    SearchResponse,
)
from app.services import rag_pipeline

router = APIRouter(tags=["rag"])


@router.post("/search", response_model=SearchResponse)
async def search(body: SearchQuery):
    """1. Content Search / Recommendation endpoint."""
    return rag_pipeline.search_resources(body)


@router.post("/next-steps", response_model=NextStepsResponse)
@limiter.limit("20/minute")
def next_steps(request: Request, body: NextStepsQuery):
    """2. 'What should I do next?' endpoint."""
    return rag_pipeline.get_next_steps(body)


@router.post("/quiz", response_model=QuizResponse)
@limiter.limit("20/minute")
def quiz(request: Request, body: QuizQuery):
    """3. RAG-powered quizzes endpoint."""
    return rag_pipeline.get_quiz(body)


@router.post("/ask", response_model=AskResponse)
@limiter.limit("20/minute")
def ask(request: Request, body: AskRequest):
    """4. 'Ask BNHS' chatbot, answering from the archive with citations."""
    return rag_pipeline.ask(body)
