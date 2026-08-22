"""Embeds document_chunks that don't have an embedding yet (the existing
3,205 Omeka-sourced rows), and chunks + embeds `documents` rows that don't
have chunks yet (blog posts, newsletters -- their content is long enough to
need splitting, unlike the short Omeka metadata records which are already
one-chunk-per-document via the earlier ingest).

Uses a local sentence-transformers model (no API key needed) matching the
existing vector(768) column -- sentence-transformers/all-mpnet-base-v2.

Usage:
    cd backend && source .venv/bin/activate && python scripts/build_embeddings.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402
from supabase import create_client  # noqa: E402

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
CHUNK_CHARS = 1000
CHUNK_OVERLAP = 150
BATCH_SIZE = 100


def split_text(text: str, size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        if end < len(text):
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def embed_existing_chunks(supabase, model) -> int:
    print("Embedding existing document_chunks with no embedding...")
    total = 0
    while True:
        rows = (
            supabase.table("document_chunks")
            .select("id, content")
            .is_("embedding", "null")
            .limit(BATCH_SIZE)
            .execute()
            .data
        )
        if not rows:
            break

        vectors = model.encode([row["content"] for row in rows], show_progress_bar=False)
        for row, vector in zip(rows, vectors):
            supabase.table("document_chunks").update({"embedding": vector.tolist()}).eq("id", row["id"]).execute()
        total += len(rows)
        print(f"  embedded {total} so far...")

    return total


def chunk_and_embed_new_documents(supabase, model, source_types: list[str]) -> int:
    print(f"Chunking + embedding documents with no chunks yet ({source_types})...")
    total_chunks = 0
    for source_type in source_types:
        docs = supabase.table("documents").select("id, title, metadata").eq("source_type", source_type).execute().data
        for doc in docs:
            existing = (
                supabase.table("document_chunks").select("id").eq("document_id", doc["id"]).limit(1).execute().data
            )
            if existing:
                continue

            content = (doc.get("metadata") or {}).get("content") or ""
            if not content:
                continue

            pieces = split_text(content)
            vectors = model.encode(pieces, show_progress_bar=False)
            for index, (piece, vector) in enumerate(zip(pieces, vectors)):
                chunk_text = f"{doc['title']}\n\n{piece}" if index == 0 else piece
                supabase.table("document_chunks").insert(
                    {
                        "document_id": doc["id"],
                        "chunk_index": index,
                        "content": chunk_text,
                        "embedding": vector.tolist(),
                        "metadata": {"source_type": source_type},
                    }
                ).execute()
            total_chunks += len(pieces)
            print(f"  {source_type} '{doc['title'][:60]}' -> {len(pieces)} chunks")

    return total_chunks


def main() -> None:
    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    print(f"Loading embedding model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    existing_count = embed_existing_chunks(supabase, model)
    new_count = chunk_and_embed_new_documents(supabase, model, ["blog_post", "newsletter"])

    print(f"\nDone. Backfilled {existing_count} existing chunks, created {new_count} new chunks.")


if __name__ == "__main__":
    main()
