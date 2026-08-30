from fastapi import APIRouter

from app.models.schema import (
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
async def next_steps(body: NextStepsQuery):
    """2. 'What should I do next?' endpoint."""
    return rag_pipeline.get_next_steps(body)


@router.post("/quiz", response_model=QuizResponse)
async def quiz(body: QuizQuery):
    """3. RAG-powered quizzes endpoint."""
    return rag_pipeline.get_quiz(body)
