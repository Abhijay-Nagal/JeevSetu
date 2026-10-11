-- Accounts move from Supabase Auth to the backend's own username + password
-- login (see backend/app/core/auth.py), so public.users no longer has to
-- mirror an auth.users row.
alter table public.users drop constraint if exists users_id_fkey;
alter table public.users alter column id set default gen_random_uuid();

alter table public.users
  add column if not exists username text,
  add column if not exists password_hash text,
  add column if not exists email_confirmed_at timestamptz;

-- Usernames are stored lowercased by the backend; the index enforces
-- uniqueness even if a row is written some other way.
create unique index if not exists users_username_lower_idx on public.users (lower(username));

-- Collectable cards bought with coins (catalog lives in backend/app/services/cards.py).
create table if not exists public.user_cards (
  user_id uuid not null references public.users(id) on delete cascade,
  card_id text not null,
  created_at timestamptz not null default now(),
  primary key (user_id, card_id)
);

alter table public.user_cards enable row level security;
