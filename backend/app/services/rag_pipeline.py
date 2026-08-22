"""End-to-end RAG pipeline.

Embeddings: local sentence-transformers (no API key, no per-call cost/rate
limit) -- must stay in sync with the model used in scripts/build_embeddings.py
and the vector(768) column in document_chunks.

Generation (next-steps, quiz): Groq's OpenAI-compatible chat completions API,
in JSON mode, grounded in chunks retrieved via the match_documents RPC.
"""

import json
from functools import lru_cache

from groq import Groq
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.supabase_client import get_supabase
from app.models.schema import (
    NextStepsQuery,
    NextStepsResponse,
    QuizQuery,
    QuizResponse,
    SearchQuery,
    SearchResponse,
    SearchResultCard,
)

EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
GROQ_MODEL = "openai/gpt-oss-120b"


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@lru_cache
def get_groq_client() -> Groq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is missing -- set it in .env")
    return Groq(api_key=settings.groq_api_key)


def get_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(text).tolist()


def _generate_json(system: str, prompt: str) -> dict:
    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Groq returned invalid JSON: {content[:500]}") from exc


def _retrieve_context(query: str, match_count: int = 5) -> list[dict]:
    supabase = get_supabase()
    embedding = get_embedding(query)
    response = supabase.rpc(
        "match_documents",
        {"query_embedding": embedding, "match_threshold": 0.15, "match_count": match_count},
    ).execute()
    return response.data or []


def search_resources(body: SearchQuery) -> SearchResponse:
    """Semantic search over BNHS content via match_documents."""
    matches = _retrieve_context(body.query, match_count=body.limit)
    results = [
        SearchResultCard(
            id=row.get("id"),
            title=row.get("title") or "",
            summary=row.get("summary"),
            content_type=row.get("content_type"),
            source=row.get("source"),
            image_url=row.get("image_url"),
            bnhs_url=row.get("bnhs_url"),
            file_name=row.get("file_name"),
            author=row.get("author"),
            similarity_score=row.get("similarity"),
        )
        for row in matches
    ]
    return SearchResponse(results=results)


def get_next_steps(body: NextStepsQuery) -> NextStepsResponse:
    """Generates structured, actionable next-step recommendations."""
    resource = body.current_resource
    interests = ", ".join(body.user_interests) if body.user_interests else "wildlife conservation, learning, volunteering"

    system = (
        "You are an expert conservation strategist for the Bombay Natural History Society (BNHS). "
        "Respond with a JSON object only, matching exactly this shape: "
        '{"actions": [{"action_label": "Learn|Explore|Play|Take a quiz|Contribute|Advocate", '
        '"description": "string", "direct_link": "string or null"}]} -- return exactly 4 actions.'
    )
    prompt = (
        f"A user is viewing this resource:\n"
        f"Title: {resource.title}\n"
        f"Type: {resource.type}\n"
        f"Content: {resource.content}\n\n"
        f"Their stated interests: {interests}.\n\n"
        "Recommend 4 actions that turn this passive reader into an active BNHS participant/advocate. "
        "Use realistic direct_links (e.g. https://bnhs.org/membership-form, https://collections.bnhs.org, "
        "https://blog.bnhs.org, https://bnhs.org/news-letter)."
    )

    data = _generate_json(system, prompt)
    return NextStepsResponse.model_validate(data)


def get_quiz(body: QuizQuery) -> QuizResponse:
    """RAG-grounded multiple-choice quiz generation."""
    matches = _retrieve_context(body.topic, match_count=5)
    if matches:
        context_text = "\n\n".join(f"[{row.get('content_type')}] {row.get('title')}: {row.get('summary')}" for row in matches)
    else:
        context_text = "No specific BNHS documents matched this topic -- use general Indian wildlife conservation knowledge."

    system = (
        "You are an educational quiz designer for BNHS. Respond with a JSON object only, matching exactly: "
        '{"questions": [{"question": "string", "options": ["string", "string", "string", "string"], '
        '"correct_answer": 0, "explanation": "string", "source_reference": "string or null"}]}. '
        "options must contain exactly 4 items; correct_answer is the 0-based index of the correct option."
    )
    prompt = (
        f'Generate a {body.num_questions}-question multiple-choice quiz about "{body.topic}".\n\n'
        "Ground your questions in this retrieved context where possible -- cite the matching title in "
        "source_reference. If the context is insufficient for a question, use general Indian wildlife "
        "conservation knowledge instead and leave source_reference null.\n\n"
        f"<CONTEXT>\n{context_text}\n</CONTEXT>"
    )

    data = _generate_json(system, prompt)
    return QuizResponse.model_validate(data)
