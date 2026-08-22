from supabase import Client

from app.models.schema import SearchQuery, SearchResponse
from app.services import rag_pipeline

RELATED_RECORDS_LIMIT = 5


def check_related_records(abstract: str) -> SearchResponse:
    """Runs the submitter's abstract through the same RAG search used by
    the Knowledge Hub -- purely informational (shows what BNHS already has
    on the topic), doesn't block or gate the submission.
    """
    return rag_pipeline.search_resources(SearchQuery(query=abstract, limit=RELATED_RECORDS_LIMIT))


def create_submission(supabase: Client, user_id: str, body: dict) -> dict:
    row = {**body, "user_id": user_id}
    result = supabase.table("research_submissions").insert(row).execute()
    return result.data[0]


def list_my_submissions(supabase: Client, user_id: str) -> list[dict]:
    result = (
        supabase.table("research_submissions")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data
