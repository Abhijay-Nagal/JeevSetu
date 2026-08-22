create table observation_comments (
  id uuid primary key default gen_random_uuid(),
  observation_id uuid not null references observations(id),
  user_id uuid not null references users(id),
  content text not null,
  created_at timestamptz not null default now()
);

create index observation_comments_observation_id_idx on observation_comments(observation_id);
