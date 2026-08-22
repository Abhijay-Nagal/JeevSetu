"""End-to-End RAG System using Gemini API and Supabase pgvector."""
import json
import os

from google import genai
from pydantic import BaseModel

from app.core.supabase_client import get_supabase
from app.models.schema import (
    NextStepAction,
    NextStepsQuery,
    NextStepsResponse,
    QuizQuery,
    QuizQuestion,
    QuizResponse,
    SearchQuery,
    SearchResponse,
    SearchResultCard,
)

from dotenv import load_dotenv

# Initialize Gemini Client
def get_genai_client():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing or empty in .env")
    return genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})


def get_embedding(text: str) -> list[float]:
    """Generates a 768-dimensional vector embedding using Gemini text-embedding-004."""
    client = get_genai_client()
    response = client.models.embed_content(
        model='gemini-embedding-2',
        contents=text,
    )
    return response.embeddings[0].values


def search_resources(body: SearchQuery) -> SearchResponse:
    """1. Content Search & Recommendation using RPC match_documents."""
    supabase = get_supabase()
    
    # Generate embedding for the search query
    try:
        query_embedding = get_embedding(body.query)
    except Exception as e:
        # Fallback if Gemini fails or key is missing
        raise RuntimeError(f"Failed to generate embeddings: {str(e)}")

    # Perform vector search via Supabase RPC
    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_threshold": 0.0, # Relaxed for now since data might not be perfectly embedded
            "match_count": body.limit
        }
    ).execute()
    
    results = []
    if response.data:
        for row in response.data:
            results.append(
                SearchResultCard(
                    id=row.get("id"),
                    title=row.get("title", ""),
                    summary=row.get("summary"),
                    content_type=row.get("content_type"),
                    source=row.get("source"),
                    image_url=row.get("image_url"),
                    bnhs_url=row.get("bnhs_url"),
                    similarity_score=row.get("similarity")
                )
            )
            
    return SearchResponse(results=results)


def get_next_steps(body: NextStepsQuery) -> NextStepsResponse:
    """2. 'What should I do next?' - Generates structured action recommendations."""
    client = get_genai_client()
    
    res = body.current_resource
    interests = ", ".join(body.user_interests) if body.user_interests else "wildlife conservation, learning, volunteering"
    
    prompt = f"""
    You are an expert conservation strategist for the Bombay Natural History Society (BNHS).
    A user is currently viewing the following resource:
    Title: {res.title}
    Type: {res.type}
    Content Summary: {res.content}
    
    Their stated interests are: {interests}.
    
    Based on this, recommend 4 highly relevant, actionable next steps to transform this passive reader into an active BNHS participant/advocate.
    The action_label must strictly be one of: Learn, Explore, Play, Take a quiz, Contribute, Advocate.
    Provide a compelling description and a realistic direct_link (e.g., https://bnhs.org/membership, or collections.bnhs.org).
    """
    
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": NextStepsResponse,
            "temperature": 0.2
        }
    )
    
    # Parse the strictly structured JSON response
    return NextStepsResponse.model_validate_json(response.text)


def get_quiz(body: QuizQuery) -> QuizResponse:
    """3. RAG-Powered Conservation Quizzes."""
    client = get_genai_client()
    supabase = get_supabase()
    
    # 1. Retrieve relevant context for the topic
    # We will do a hybrid/text search if vector embedding isn't populated, but since we are doing end-to-end vector:
    try:
        query_embedding = get_embedding(body.topic)
        rpc_response = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.0,
                "match_count": 5
            }
        ).execute()
        
        context_chunks = []
        if rpc_response.data:
            for row in rpc_response.data:
                context_chunks.append(f"Title: {row.get('title')}\nContent: {row.get('summary')}")
        
        context_text = "\n\n".join(context_chunks)
        if not context_text:
            context_text = "No specific BNHS documents retrieved. Use general conservation knowledge."
            
    except Exception:
        # Fallback if embedding fails
        context_text = "Use general BNHS and wildlife conservation knowledge to generate the quiz."
    
    # 2. Force LLM to generate quiz grounded in context
    prompt = f"""
    You are an educational designer for BNHS.
    Generate a {body.num_questions}-question multiple-choice quiz about "{body.topic}".
    
    CRITICAL INSTRUCTION: You MUST ground your questions ONLY in the following retrieved context.
    If the context is insufficient, create questions related to the topic based on Indian wildlife conservation.
    
    <CONTEXT>
    {context_text}
    </CONTEXT>
    """
    
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": QuizResponse,
            "temperature": 0.1
        }
    )
    
    return QuizResponse.model_validate_json(response.text)
