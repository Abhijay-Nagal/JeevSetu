# Handoff

## Current state
- FastAPI backend scaffolded under `backend/app/` (core, models, routers, services) per `Docs/architecture.md`.
- Supabase tables live: `users`, `observations`, `status_events` (community engagement), `documents` (RAG source data, 3,197 rows pre-loaded from the BNHS Omeka API — see `data/bnhs-collections/README.md` at the CodeForGood root).
- Community Engagement vertical (`routers/community.py`, `services/observations.py`) is implemented and covered by automated tests (`backend/tests/`).
- Communities/posts-in-communities/likes feature (per `Docs/detailed_plan.md`) is fully built: `communities`, `community_members`, `observation_likes` tables; `routers/communities.py` + `routers/community.py` (like/unlike); `services/communities.py`, `services/likes.py`; extended `services/observations.py` for community-scoped posting. 31 tests passing.
- A public `observation-images` Storage bucket exists — frontend uploads directly to it and passes the resulting URL as `media_url` on `POST /observations`. No backend upload endpoint (deliberate — see `detailed_plan.md` Design Decisions).
- RAG vertical (`routers/rag.py`) is a stub — returns 501 until an embedding model is chosen (owned by Dhananjay/Pritam).

## What was just done
- Added `services/observations.py` so `community.py` stays a thin controller.
- Fixed `update_observation_status` to use `.maybe_single()` instead of `.single()` — `.single()` raises on zero rows in postgrest-py, which would have surfaced a 500 instead of the intended 404.
- Injected the Supabase client via `Depends(get_supabase)` in all four community routes instead of calling it directly, so it's swappable in tests.
- Added a pytest suite: fake in-memory Supabase client (`tests/fakes.py`), service-layer tests, auth dependency tests, router integration tests.
- Added ruff + black config (`pyproject.toml`) and `requirements-dev.txt`.
- Backfilled `supabase/migrations/` — four earlier migrations (documents, users/observations/status_events, http ingest function) were applied via the Supabase MCP tool without ever being saved as files; reconstructed and committed them, then reconciled via `supabase migration repair`.
- Built the full communities/posts/likes feature (`Docs/detailed_plan.md`, all 10 tasks). Found and fixed two more testability/correctness bugs along the way while writing tests: the fake client's row `id` was a plain counter ("1", "2") which failed `response_model=Observation`'s UUID validation once tests went through the router; `community_members`' timestamp column is `joined_at` not `created_at`, which the fake didn't default, failing `CommunityMember` response validation.
- Like counts are a real `observations.like_count` column, maintained by application code (`services/likes.py`), not a Postgres trigger — simpler to test, at the cost of not being atomic against a second write path. Everything goes through this backend with the service-role key, so that's an acceptable trade for now.

## Known issues / not done
- No manual smoke test against the real (deployed) Supabase project yet — needs `SUPABASE_SERVICE_ROLE_KEY` in a local `.env` (get it from the Supabase dashboard; the MCP connection doesn't expose it). Run `python scripts/smoke_test.py` once `.env` is filled in (covers the observations API only — communities/likes aren't in that script yet).
- Like-count updates are read-then-write in application code, not atomic — a race between two simultaneous likes on the same post could under/over-count by one. Acceptable for now; a Postgres trigger or `increment()` RPC would fix it if it becomes a real problem.
- Notification channel (in-app vs. email) still undecided — `services/notifications.py` is a no-op.
- `document_chunks` table (for RAG embeddings) doesn't exist yet — blocked on the embedding model choice.
- Not built (deliberately, YAGNI — see `detailed_plan.md` Design Decisions): comments, a "list community members" endpoint, community edit/delete, per-invite tracking/expiry.

## Next steps
- Run the smoke test script against real Supabase once `.env` is set up, and record the result here.
- RAG pair: pick an embedding model, implement `services/embeddings.py` and `services/rag_pipeline.py`, create the `document_chunks` table + migration.
- Frontend: wire `frontend/src/lib/supabaseClient.ts` for auth, and call the `/observations` and `/communities` endpoints per `map.md`.
