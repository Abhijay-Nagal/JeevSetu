"""Re-chunks and re-embeds documents whose chunk content is just the bare
title -- the original Omeka ingest stored d.title as chunk_index=0's entire
content for species catalog records and field guide entries, discarding the
rich structured data (taxonomy, conservation status, field characters, food,
habits, etc.) that actually exists in documents.metadata as Omeka JSON-LD
property arrays. This composes real descriptive text per source_type instead,
then chunks + re-embeds it the same way build_embeddings.py does for
blog/newsletter content.

Idempotent: only touches documents whose current single chunk content still
equals the bare title (i.e. not yet enriched), so it's safe to re-run.

Usage:
    cd backend && source .venv/bin/activate && python scripts/enrich_bare_chunks.py
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
PAGE_SIZE = 200


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


def field(metadata: dict, key: str) -> str | None:
    """Extract a human-readable value from an Omeka JSON-LD property array."""
    value = metadata.get(key)
    if not value:
        return None
    if isinstance(value, list):
        parts = []
        for item in value:
            if not isinstance(item, dict):
                continue
            parts.append(item.get("@value") or item.get("display_title") or item.get("code"))
        parts = [p for p in parts if p]
        return "; ".join(parts) if parts else None
    return str(value)


def compose_species_text(title: str, metadata: dict) -> str:
    common = field(metadata, "wo:commonName")
    scientific = field(metadata, "wo:scientificName") or title
    kingdom = field(metadata, "wo:kingdom")
    phylum = field(metadata, "wo:phylum")
    klass = field(metadata, "wo:class")
    order = field(metadata, "wo:order")
    family = field(metadata, "wo:family")
    genus = field(metadata, "wo:genus")
    status = field(metadata, "wo:conservationStatus")
    description = field(metadata, "dcterms:description")
    threat = field(metadata, "wo:threatDescription")

    lines = [f"{common} ({scientific})" if common else scientific]

    taxonomy_bits = [
        b
        for b in [
            f"Kingdom: {kingdom}" if kingdom else None,
            f"Phylum: {phylum}" if phylum else None,
            f"Class: {klass}" if klass else None,
            f"Order: {order}" if order else None,
            f"Family: {family}" if family else None,
            f"Genus: {genus}" if genus else None,
        ]
        if b
    ]
    if taxonomy_bits:
        lines.append(", ".join(taxonomy_bits))
    if status:
        lines.append(f"Conservation status: {status}")
    if description and description != scientific:
        lines.append(description)
    if threat:
        lines.append(f"Threats: {threat}")

    return "\n".join(lines)


def compose_field_guide_text(title: str, metadata: dict) -> str:
    common = field(metadata, "bnhsfg:commonName") or title
    scientific = field(metadata, "bnhsfg:scientificName")
    lines = [f"{common} ({scientific})" if scientific else common]

    field_map = [
        ("Field characters", "bnhsfg:fieldCharacters"),
        ("Size", "bnhsfg:sizeRaw"),
        ("Colours of bare parts", "bnhsfg:coloursOfBareParts"),
        ("Food", "bnhsfg:food"),
        ("General habits", "bnhsfg:generalHabits"),
        ("Voice and calls", "bnhsfg:voiceAndCalls"),
        ("Breeding", "bnhsfg:breeding"),
        ("Migration", "bnhsfg:migration"),
        ("Status, distribution & habitat", "bnhsfg:statusDistributionHabitat"),
        ("Museum diagnosis", "bnhsfg:museumDiagnosis"),
        ("Local names", "bnhsfg:localNames"),
        ("Other names", "bnhsfg:otherNames"),
        ("Miscellaneous", "bnhsfg:miscellaneous"),
    ]
    for label, key in field_map:
        value = field(metadata, key)
        if value:
            lines.append(f"{label}: {value}")

    return "\n\n".join(lines)


COMPOSERS = {
    "species": compose_species_text,
    "field_guide_bird": compose_field_guide_text,
    "field_guide_page": compose_field_guide_text,
}


def enrich(supabase, model, source_type: str) -> int:
    composer = COMPOSERS[source_type]
    total_enriched = 0
    offset = 0
    while True:
        docs = (
            supabase.table("documents")
            .select("id, title, metadata")
            .eq("source_type", source_type)
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
            .data
        )
        if not docs:
            break

        for doc in docs:
            existing = (
                supabase.table("document_chunks")
                .select("id, content")
                .eq("document_id", doc["id"])
                .order("chunk_index")
                .execute()
                .data
            )
            if not existing or len(existing) != 1 or existing[0]["content"] != doc["title"]:
                continue  # already enriched, or not a bare-title chunk

            text = composer(doc["title"], doc["metadata"] or {})
            pieces = split_text(text)
            vectors = model.encode(pieces, show_progress_bar=False)

            supabase.table("document_chunks").delete().eq("id", existing[0]["id"]).execute()
            for index, (piece, vector) in enumerate(zip(pieces, vectors)):
                supabase.table("document_chunks").insert(
                    {
                        "document_id": doc["id"],
                        "chunk_index": index,
                        "content": piece,
                        "embedding": vector.tolist(),
                        "metadata": {"source_type": source_type},
                    }
                ).execute()
            total_enriched += 1

        offset += PAGE_SIZE
        print(f"  {source_type}: scanned {offset} documents, enriched {total_enriched} so far...")

    return total_enriched


def main() -> None:
    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    print(f"Loading embedding model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    for source_type in COMPOSERS:
        print(f"Enriching {source_type}...")
        count = enrich(supabase, model, source_type)
        print(f"Done with {source_type}: enriched {count} documents\n")


if __name__ == "__main__":
    main()
