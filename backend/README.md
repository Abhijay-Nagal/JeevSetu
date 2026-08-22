# Backend

FastAPI backend for both verticals — Community Engagement (`app/routers/community.py`) and RAG (`app/routers/rag.py`). See `Docs/architecture.md` for the full design.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Supabase keys
uvicorn app.main:app --reload
```

## Folder structure

```
app/
  core/       auth, config, supabase client
  models/     shared Pydantic contracts (schema.py) — frozen after Phase 1 unless Raghottam signs off
  routers/    one file per vertical
  services/   business logic called by routers
```

One owner per router/service pair. Community Engagement is Raghottam; RAG is Dhananjay/Pritam.
