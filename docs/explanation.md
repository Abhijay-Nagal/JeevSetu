# How the RAG Pipeline Works

This explains, from the actual code on `main`, how JeevSetu's Knowledge Hub
turns a user's question into an answer — what's real retrieval, what's pure
generation, and where each of those is used.

## The Two Building Blocks

Everything in the pipeline is composed from exactly two primitives, both in
`backend/app/services/rag_pipeline.py`:

**1. Retrieval — `_retrieve_context(query, match_count)`**
```python
def _retrieve_context(query: str, match_count: int = 5) -> list[dict]:
    supabase = get_supabase()
    embedding = get_embedding(query)
    response = supabase.rpc(
        "match_documents",
        {"query_embedding": embedding, "match_threshold": 0.15, "match_count": match_count},
    ).execute()
    return response.data or []
```
- Embeds the query text with a **local** `sentence-transformers` model
  (`all-mpnet-base-v2`, 768 dimensions) — no external API call, no per-query
  cost or rate limit.
- Calls the `match_documents` Postgres function, which does cosine similarity
  search over `document_chunks.embedding` (a `pgvector` column), joins back to
  the parent `documents` row for title/attribution, and returns the best
  match **per document** above a similarity threshold of `0.15`.
- Returns real rows: `id`, `title`, `summary`, `content_type`, `bnhs_url`,
  `file_name`, `author`, `similarity` — every field traceable to an actual
  ingested BNHS record.

**2. Generation — `_generate_json(system, prompt)`**
```python
def _generate_json(system: str, prompt: str) -> dict:
    ...
    response = get_groq_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
```
- One call to Groq (`openai/gpt-oss-120b`) in JSON mode, so the response is
  always a parseable structured object, never freeform text.
- Takes whatever `system`/`prompt` strings the caller builds — retrieval and
  generation are fully decoupled; a caller can use one, the other, or both.

## Ingestion — How Content Gets In (offline, not a live request)

Before any of the above can run, content has to exist in `document_chunks`
with embeddings. This happens via one-off scripts in `backend/scripts/`, not
on the request path:

1. **Omeka collections** (`collections.bnhs.org`) — BNHS's Virtual Museum,
   species records, and publications, pulled via a Postgres `http` extension
   call directly into the `documents` table.
2. **`fetch_extended_content.py`** — BNHS's WordPress blog (paginated REST
   API) and newsletter PDFs (scraped links, text extracted with `pypdf`),
   upserted into `documents`.
3. **`build_embeddings.py`** — chunks long-form content (1000 characters,
   150-character overlap) and embeds every chunk with the same local
   `all-mpnet-base-v2` model into `document_chunks`. Also backfills any chunk
   still missing an embedding.
4. **`enrich_bare_chunks.py`** — a correctness pass: species/field-guide
   records that were originally chunked as just their bare title (discarding
   the real taxonomy/field-guide text sitting in their metadata) get
   recomposed into real descriptive text and re-embedded.

**Important operational detail:** not every row in `documents` has been
through steps 3–4. A document with zero rows in `document_chunks` is
ingested (metadata exists) but not yet searchable — `match_documents` can
only return what's actually been chunked and embedded.

## The Three RAG-Backed Endpoints — How Each One Actually Composes the Two Primitives

### Search — `POST /api/search` → `search_resources()`
**Retrieval only. No Groq call.**
```python
matches = _retrieve_context(body.query, match_count=body.limit)
```
Embeds the query, runs `match_documents`, maps the rows straight into
`SearchResultCard`s. No generation step exists in this path — it is
*structurally* impossible for this endpoint to fabricate a fact, because
nothing is generated. Every result is a real chunk from a real document,
with a real `bnhs_url` the user can click through to. Cheapest and fastest
of the three.

### Next Steps — `POST /api/next-steps` → `get_next_steps()`
**Generation only. No retrieval call.**
```python
system = "You are an expert conservation strategist for BNHS. Respond with a JSON object only..."
prompt = f"A user is viewing this resource:\nTitle: {resource.title}\n...\nRecommend 4 actions..."
data = _generate_json(system, prompt)
```
Takes whatever resource the frontend says the user is currently looking at
(title/content/type, passed in directly — not pulled from the vector store)
plus optional stated interests, and asks Groq for exactly 4 structured
actions from a fixed vocabulary (`Learn`, `Explore`, `Play`, `Take a quiz`,
`Contribute`, `Advocate`). The prompt explicitly asks the model to invent
*"realistic direct_links"* — these are model-generated URL guesses, not
verified against real BNHS pages, since this endpoint never touches the
document store.

### Quiz — `POST /api/quiz` → `get_quiz()`
**Retrieval *and* generation, composed together — the only endpoint where
retrieved content directly shapes what gets generated.**
```python
matches = _retrieve_context(body.topic, match_count=5)
if matches:
    context_text = "\n\n".join(...)
else:
    context_text = "No specific BNHS documents matched this topic -- use general Indian wildlife conservation knowledge."
...
prompt = f'Generate a {body.num_questions}-question quiz about "{body.topic}".\n\n' \
         "Ground your questions in this retrieved context where possible -- cite the matching title in source_reference. " \
         "If the context is insufficient for a question, use general Indian wildlife conservation knowledge instead " \
         "and leave source_reference null.\n\n<CONTEXT>...</CONTEXT>"
```
Retrieves 5 chunks for the topic, hands them to Groq as grounding context,
and asks for N multiple-choice questions with a `source_reference` citing
the matching document title. **This has an explicit, intentional ungrounded
fallback**: when retrieval comes up short, the prompt tells the model to
answer from general knowledge instead and leave `source_reference` null.
This is a deliberate UX choice (always return a usable quiz rather than
fail), but it means "every quiz question is grounded" is not literally true
— only the ones where retrieval actually found something relevant are.

### Daily Question — `GET/POST /rewards/daily-question`
Not a fourth generation path — a scheduling/persistence wrapper around Quiz.
Picks a topic deterministically (rotates through a fixed theme list keyed to
the calendar date, not random), calls the same quiz machinery for exactly 1
question, and caches the result in `daily_questions` so it's generated once
per day rather than once per request. Unlike the plain quiz endpoint, it
withholds `correct_answer` until the user submits an attempt, since the
reward (coins/streak) is gated on a real attempt.

### Publications "related records" — `POST /research/check-related`
Literally calls `search_resources()` — the exact same function as Search,
just invoked from the research-submission form using the submitter's
abstract as the query. Purely informational; doesn't block or gate
submission.

## Summary Table

| Endpoint | Retrieval? | Generation? | Can it hallucinate a fact? |
|---|:---:|:---:|---|
| Search | Yes | No | No — nothing is generated |
| Next Steps | No | Yes | N/A for facts — but suggested links are model-guessed, not verified |
| Quiz | Yes | Yes | Only when retrieval finds nothing relevant (explicit, disclosed fallback) |
| Daily Question | Yes | Yes | Same as Quiz — it *is* Quiz, scheduled and cached |
| Publications check | Yes | No | No — reuses Search |

## Why the Design Splits This Way

It's not "three separate RAG features" — it's one retrieval primitive and
one generation primitive, composed three different ways depending on what
the frontend actually needs:
- **Facts with sources** → retrieval only (Search)
- **Ungrounded, structured suggestions anchored to what's on screen** →
  generation only (Next Steps)
- **Grounded creative output, with a disclosed fallback** → both (Quiz)

Daily Question is a scheduling layer on top of Quiz; the Publications check
is a straight code-reuse of Search from a different screen.
