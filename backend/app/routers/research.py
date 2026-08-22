from fastapi import APIRouter, Depends, status
from supabase import Client

from app.core.auth import CurrentUser, get_current_user
from app.core.supabase_client import get_supabase
from app.models.schema import (
    RelatedRecordsQuery,
    ResearchSubmission,
    ResearchSubmissionCreate,
    SearchResponse,
)
from app.services import research_submissions

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/check-related", response_model=SearchResponse)
async def check_related_records(body: RelatedRecordsQuery):
    return research_submissions.check_related_records(body.abstract)


@router.post("/submissions", response_model=ResearchSubmission, status_code=status.HTTP_201_CREATED)
async def create_submission(
    body: ResearchSubmissionCreate,
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return research_submissions.create_submission(supabase, user.id, body.model_dump())


@router.get("/submissions/mine", response_model=list[ResearchSubmission])
async def my_submissions(
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return research_submissions.list_my_submissions(supabase, user.id)
