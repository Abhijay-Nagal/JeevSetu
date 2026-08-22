-- Research findings from citizen scientists/enthusiasts -- distinct from
-- `observations` (casual sightings with a staff-triage workflow). This is a
-- simpler, one-way submission: check it against existing BNHS knowledge via
-- the RAG pipeline, store it, done. No status/triage workflow -- BNHS staff
-- work directly against this table from here.
create table research_submissions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id),
  title text not null,
  abstract text not null,
  description text,
  species text,
  location text,
  media_url text,
  created_at timestamptz not null default now()
);

create index research_submissions_user_id_idx on research_submissions(user_id);
