"""Ingestion (chunk + embed -> document_chunks) and retrieval for the RAG flow.

Owned by the RAG pair (Dhananjay/Pritam per Docs/architecture.md).
"""

from app.models.schema import RagAnswer


def ingest_document(document_id: str) -> int:
    """Chunks a `documents` row and embeds each chunk into `document_chunks`. Returns the count."""
    raise NotImplementedError


def answer_question(question: str) -> RagAnswer:
    """Embeds the question, retrieves top-k chunks by cosine distance, and generates an answer."""
    raise NotImplementedError
