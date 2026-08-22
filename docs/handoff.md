# Handoff

## Current state
- FastAPI backend scaffolded under `backend/app/` (core, models, routers, services) per `Docs/architecture.md`.
- Supabase tables live: `users`, `observations`, `status_events` (community engagement), `documents` (RAG source data, 3,197 rows pre-loaded from the BNHS Omeka API — see `data/bnhs-collections/README.md` at the CodeForGood root).
- Community Engagement vertical (`routers/community.py`, `services/observations.py`) is implemented and covered by automated tests (`backend/tests/`).
- RAG vertical (`routers/rag.py`) is a stub — returns 501 until an embedding model is chosen (owned by Dhananjay/Pritam).
- In progress: communities/posts-in-communities/likes feature per `Docs/detailed_plan.md` — schema is live, service/router layer being built now.

## What was just done
- Added `services/observations.py` so `community.py` stays a thin controller.
- Fixed `update_observation_status` to use `.maybe_single()` instead of `.single()` — `.single()` raises on zero rows in postgrest-py, which would have surfaced a 500 instead of the intended 404.
- Injected the Supabase client via `Depends(get_supabase)` in all four community routes instead of calling it directly, so it's swappable in tests.
- Added a pytest suite: fake in-memory Supabase client (`tests/fakes.py`), service-layer tests, auth dependency tests, router integration tests.
- Added ruff + black config (`pyproject.toml`) and `requirements-dev.txt`.
- Backfilled `supabase/migrations/` — four earlier migrations (documents, users/observations/status_events, http ingest function) were applied via the Supabase MCP tool without ever being saved as files; reconstructed and committed them, then reconciled via `supabase migration repair`.

## Known issues / not done
- No manual smoke test against the real (deployed) Supabase project yet — needs `SUPABASE_SERVICE_ROLE_KEY` in a local `.env` (get it from the Supabase dashboard; the MCP connection doesn't expose it).
- Notification channel (in-app vs. email) still undecided — `services/notifications.py` is a no-op.
- `document_chunks` table (for RAG embeddings) doesn't exist yet — blocked on the embedding model choice.

## Next steps
- Finish `Docs/detailed_plan.md` (communities/posts/likes).
- Run the smoke test script against real Supabase once `.env` is set up, and record the result here.
- RAG pair: pick an embedding model, implement `services/embeddings.py` and `services/rag_pipeline.py`, create the `document_chunks` table + migration.
- Frontend: wire `frontend/src/lib/supabaseClient.ts` for auth, and call the `/observations` endpoints per `map.md`.
