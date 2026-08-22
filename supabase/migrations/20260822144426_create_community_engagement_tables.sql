create table public.users (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  role text not null default 'contributor' check (role in ('contributor', 'staff', 'researcher')),
  created_at timestamptz not null default now()
);

create table public.observations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id),
  species text,
  description text,
  location text,
  media_url text,
  status text not null default 'submitted'
    check (status in ('submitted', 'under_review', 'forwarded', 'responded')),
  assigned_researcher text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.status_events (
  id uuid primary key default gen_random_uuid(),
  observation_id uuid not null references public.observations(id),
  old_status text,
  new_status text not null,
  note text,
  created_at timestamptz not null default now()
);

create index observations_user_id_idx on public.observations (user_id);
create index status_events_observation_id_idx on public.status_events (observation_id);

-- Seed a public.users row (default role 'contributor') whenever someone signs up via Supabase Auth.
create or replace function public.handle_new_auth_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.users (id, email) values (new.id, new.email);
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_auth_user();

alter table public.users enable row level security;
alter table public.observations enable row level security;
alter table public.status_events enable row level security;

create policy "users can read own profile" on public.users
  for select using (auth.uid() = id);

create policy "contributors can insert own observations" on public.observations
  for insert with check (auth.uid() = user_id);

create policy "contributors can read own observations" on public.observations
  for select using (auth.uid() = user_id);

create policy "contributors can read own status events" on public.status_events
  for select using (
    exists (
      select 1 from public.observations
      where observations.id = status_events.observation_id
      and observations.user_id = auth.uid()
    )
  );
