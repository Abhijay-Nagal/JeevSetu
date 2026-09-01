# JeevSetu: Bridging People & Wildlife

A digital hub built for **BNHS (Bombay Natural History Society)** as part
of Code for Good 2026 (Bengaluru) — Challenge 1: *Engagement and
Awareness*.

BNHS has a lot of digital content (Hornbill magazine, newsletters, the
Virtual Museum, citizen-science tools) spread across disconnected
channels, with no single entry point that turns a curious visitor into an
engaged, returning contributor. JeevSetu organizes that existing content
into one AI-powered, gamified, community-driven experience — entirely
online, without building another flora/fauna photo-ID app.

## Features

- **Knowledge Hub**: semantic search + AI chatbot grounded in BNHS's real
  archive (species records, JBNHS journal, Hornbill editions, field
  guides, blog posts, newsletters), with cited sources and AI-generated
  "next steps" pointing to real BNHS actions (membership, camps, donate).
- **Community Engagement**: post observations, join/create communities,
  like and comment on posts, with a global broadcast option for
  announcements that show up everywhere.
- **Rewards & Gamification**: a daily AI-generated quiz question with
  streaks and freezes, plus coins for posting, getting liked, and
  joining/creating communities.
- **Publications**: research enthusiasts submit findings, automatically
  checked against BNHS's existing knowledge base first.
- **Email confirmation**: a branded, NGO-styled confirmation email sent
  via the project's own SMTP, independent of Supabase's default mailer.

See [`docs/plan.md`](docs/plan.md) for the reward system design,
[`docs/queries.md`](docs/queries.md) for ground-truth RAG test queries,
and [`docs/handoff.md`](docs/handoff.md) / [`docs/map.md`](docs/map.md)
for the original backend architecture handoff notes. A deep technical
architecture writeup (tech stack rationale, request flow, RAG pipeline
internals) lives at `docs/ppt3.md` on the `admin_analytics_frontend`
branch.

## Tech Stack

**Frontend:** React 19, Vite, React Router v6, Tailwind CSS v4,
`@supabase/supabase-js`, lucide-react

**Backend:** FastAPI (Python), Uvicorn, Pydantic / pydantic-settings,
supabase-py, Groq SDK (LLM inference), sentence-transformers (local
embeddings), pypdf, httpx

**Data / Infra:** Supabase (Postgres + Auth + Storage), pgvector, Groq API
(`openai/gpt-oss-120b`), Gmail SMTP

## Project Structure

```
Team-25/
├── backend/
│   ├── app/
│   │   ├── core/          # auth, config, supabase client
│   │   ├── models/        # schema.py -- every Pydantic model, one file
│   │   ├── routers/       # thin FastAPI routers, one per feature domain
│   │   └── services/      # business logic, all DB/RAG/reward logic
│   ├── scripts/           # ingestion + one-off data scripts
│   ├── tests/              # pytest suite + hand-rolled fake Supabase client
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/         # auto-discovered routes (see App.jsx)
│   │   ├── components/    # community/, rag/, ui/ component groups
│   │   ├── context/       # AuthContext, WalletContext
│   │   └── lib/           # api.js, supabaseClient.js, storage.js
│   └── .env.example
├── supabase/
│   └── migrations/        # versioned SQL, applied to the shared project
└── docs/                  # architecture, plans, ground-truth test queries
```

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- A Supabase project (Postgres + Auth + Storage + the `pgvector` and
  `http` extensions enabled)
- A [Groq API key](https://console.groq.com) (free tier works)
- An SMTP account for outbound email (Gmail with an
  [app password](https://myaccount.google.com/apppasswords) works; only
  needed for the confirmation-email feature)

## Getting Started

### 1. Clone and enter the repo

```bash
git clone <repo-url>
cd Team-25
```

### 2. Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt   # includes requirements.txt + test/lint tools

cp .env.example .env
# fill in .env -- see Environment Variables below
```

Apply the database migrations in `supabase/migrations/` to your Supabase
project (via the Supabase CLI, the SQL editor, or the Supabase MCP tools),
in filename order.

Run the backend:

```bash
uvicorn app.main:app --reload
# -> http://localhost:8000, interactive docs at /docs
```

### 3. Frontend setup

```bash
cd frontend
npm install

cp .env.example .env
# fill in .env -- see Environment Variables below
```

Run the frontend:

```bash
npm run dev
# -> http://localhost:5173
```

With both running, open `http://localhost:5173`, sign up, and confirm your
email (check spam if it doesn't arrive quickly) to start using the app.

## Environment Variables

**`backend/.env`**

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | yes | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | yes | Public/publishable key |
| `SUPABASE_SERVICE_ROLE_KEY` | yes | Secret key — full DB access, backend only, never expose to the frontend |
| `GROQ_API_KEY` | yes | Powers RAG search/chat, next-steps, quiz, and daily-question generation |
| `SMTP_HOST` / `SMTP_PORT` | no | Defaults to Gmail (`smtp.gmail.com:587`) |
| `SMTP_EMAIL` / `APP_PASSWORD` | no | Only needed for the confirmation-email feature; the app degrades to a clear error on signup if unset, nothing else breaks |
| `SMTP_FROM_NAME` | no | Defaults to `JeevSetu` |
| `FRONTEND_URL` | no | Defaults to `http://localhost:5173` -- used to build the confirmation-email link |

**`frontend/.env`**

| Variable | Required | Description |
|---|---|---|
| `VITE_SUPABASE_URL` | yes | Same Supabase project URL as the backend |
| `VITE_SUPABASE_ANON_KEY` | yes | Same anon key as the backend |
| `VITE_API_BASE_URL` | yes | Where the frontend reaches the backend (defaults to `http://localhost:8000`) |

## Available Scripts

**Backend** (`cd backend`, with `.venv` activated):

| Command | What it does |
|---|---|
| `uvicorn app.main:app --reload` | Run the dev server with hot-reload |
| `pytest` | Run the test suite |
| `ruff check .` | Lint |
| `black .` | Format |

**Frontend** (`cd frontend`):

| Command | What it does |
|---|---|
| `npm run dev` | Run the Vite dev server |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Lint (oxlint) |

## Testing

The backend test suite runs entirely against an in-memory fake Supabase
client (`tests/fakes.py`) — no live database needed:

```bash
cd backend
source .venv/bin/activate
pytest -q
```

For a real-data sanity check, `docs/queries.md` has hand-verified RAG
queries (search/next-steps/quiz) with expected results to check the
pipeline still behaves correctly after changes to embeddings, ingestion,
or the `match_documents` function.

## Database

All schema changes live as versioned SQL files in `supabase/migrations/`,
applied directly to the shared Supabase project (via the Supabase CLI or
the MCP `apply_migration` tool) rather than a local dev database. The
schema covers: user profiles, communities/posts/likes/comments, the RAG
document/chunk corpus (with `pgvector` embeddings), the reward system
(coin ledger, daily questions, streaks), research submissions, and email
confirmation tokens.

## Branches

- **`main`** — this branch: the contributor-facing app described above.
- **`admin_analytics_frontend`** — a staff-only admin dashboard and
  analytics section, developed and demoed separately on purpose. See that
  branch's own `README.md` for setup and the admin login.
