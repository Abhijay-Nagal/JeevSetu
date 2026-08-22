"""Embedding generation for RAG ingestion and querying.

Owned by the RAG pair (Dhananjay/Pritam per Docs/architecture.md). Model choice
and EMBEDDING_MODEL_API_KEY are not yet decided — see the chat history for the
`documents` table already populated in Supabase (3,197 rows: species, Hornbill
issues, collectors, etc.) that this should chunk and embed into
`document_chunks`.
"""


def embed(text: str) -> list[float]:
    raise NotImplementedError
