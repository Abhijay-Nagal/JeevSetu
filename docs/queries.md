# RAG Pipeline Test Queries

Hand-verified queries for checking the RAG pipeline (`backend/app/services/rag_pipeline.py`)
still works correctly after changes to embeddings, ingestion, or the `match_documents` RPC.

Pipeline: local `sentence-transformers/all-mpnet-base-v2` embeddings (768-dim, matches the
`vector(768)` column) for retrieval, Groq `openai/gpt-oss-120b` for generation (next-steps, quiz).

To re-run: start the backend (`cd backend && source .venv/bin/activate && uvicorn app.main:app --reload`)
and `curl` the endpoints below.

## `/api/search` — semantic search (deterministic, exact match expected)

Retrieval is embeddings + cosine similarity with no LLM step, so the top result for a given
query should be stable across runs as long as the same documents/embeddings are in the DB.
If a query below starts returning a different top result, either the embedding model, the
ingested data, or `match_documents` changed — check which.

| Query | Expected top result | content_type | Notes |
|---|---|---|---|
| `otter conservation research` | "Meet The BNHS Scientist Studying The Secret Lives Of Otters In India" | blog_post | similarity ~0.78 |
| `Kaas plateau flowers` | "The Flowers of Kaas" | blog_post | similarity ~0.68 |
| `slender-billed vulture scientific classification` | "Torgos tracheliotos (Lappet-faced Vulture)" or another `species` record with `Vulture` in the title | species | Omeka species catalog, exact top hit may shift among vulture species but content_type must be `species` |
| `vulture conservation in India` | A vulture-related `blog_post` or `newsletter` | blog_post / newsletter | similarity > 0.85 |
| `wetland bird migration` | A `newsletter` document | newsletter | similarity ~0.65-0.68 |

Every result must include a non-null `author` (defaults to "Bombay Natural History Society (BNHS)"
since none of the source feeds expose a per-item personal author). `file_name` is populated only
for newsletter PDFs (e.g. `MARCH-NEWSLETTER-BNHS-2025-G_FINAL VERSION.pdf`) and null otherwise —
Omeka collection records and blog posts have no downloadable file, only a page URL (`bnhs_url`).

```bash
curl -s -X POST http://127.0.0.1:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "otter conservation research", "limit": 2}'
```

## `/api/next-steps` — LLM-generated actions (non-deterministic wording, verify structure + grounding)

Groq generation, so exact wording varies run to run. Verify instead:
- Always returns exactly 4 actions
- `action_label` is one of: Learn, Explore, Play, Take a quiz, Contribute, Advocate
- `description` is topically relevant to the input resource (not generic/off-topic)

| Input resource | Sanity check |
|---|---|
| title: "Vulture Guardians Workshop", content: "BNHS held a national workshop on rescue, rehabilitation and conservation of vultures in India, covering conservation breeding techniques and post-release monitoring.", type: blog_post | All 4 actions should reference vultures, conservation, or BNHS programs — not unrelated species |

```bash
curl -s -X POST http://127.0.0.1:8000/api/next-steps \
  -H "Content-Type: application/json" \
  -d '{"current_resource": {"title": "Vulture Guardians Workshop", "content": "BNHS held a national workshop on rescue, rehabilitation and conservation of vultures in India, covering conservation breeding techniques and post-release monitoring.", "type": "blog_post"}, "user_interests": ["wildlife photography", "volunteering"]}'
```

## `/api/quiz` — RAG-grounded quiz generation (verify grounding, not exact wording)

Retrieval feeds real chunks to Groq as context; verify the generated questions/explanations
actually match facts in the source article rather than being generic trivia.

| Topic | Ground truth fact the quiz should be grounded in | Source |
|---|---|---|
| `Kaas plateau flowers` | "Water snowflakes" = *Nymphoides indica*, an aquatic plant blooming on Kaas Lake | "The Flowers of Kaas" blog post |
| `Kaas plateau flowers` | The mass wildflower bloom on Kaas plateau is triggered by the south-west monsoon | "The Flowers of Kaas" blog post |
| `Great Indian Bustard conservation` | Rajasthan's Thar Desert (Jaisalmer District) is the last stronghold for the species | "Dentist-Turned-Conservationist: The Story Of GIB Protector..." blog post |
| `Great Indian Bustard conservation` | Power lines are a major collision/mortality risk for bustards | "Wings Against Wires: How Power Lines Are Killing Bustards In India" blog post |

```bash
curl -s -X POST http://127.0.0.1:8000/api/quiz \
  -H "Content-Type: application/json" \
  -d '{"topic": "Kaas plateau flowers", "num_questions": 2}'
```

If a quiz question's `source_reference` cites a title unrelated to its `explanation`, or the
`explanation` states something not actually in the cited article, that's a grounding failure —
check `_retrieve_context()` in `rag_pipeline.py` and the `match_threshold` used in `match_documents`.
