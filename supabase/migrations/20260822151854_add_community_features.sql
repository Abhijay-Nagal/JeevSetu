create table public.communities (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  description text,
  created_by uuid not null references public.users(id),
  created_at timestamptz not null default now()
);

create table public.community_members (
  community_id uuid not null references public.communities(id) on delete cascade,
  user_id uuid not null references public.users(id),
  role text not null default 'member' check (role in ('creator', 'member')),
  joined_at timestamptz not null default now(),
  primary key (community_id, user_id)
);

alter table public.observations
  add column community_id uuid references public.communities(id),
  add column like_count integer not null default 0;

create index observations_community_id_idx on public.observations (community_id);

create table public.observation_likes (
  observation_id uuid not null references public.observations(id) on delete cascade,
  user_id uuid not null references public.users(id),
  created_at timestamptz not null default now(),
  primary key (observation_id, user_id)
);

alter table public.communities enable row level security;
alter table public.community_members enable row level security;
alter table public.observation_likes enable row level security;

create policy "communities are publicly readable" on public.communities
  for select using (true);

create policy "authenticated users can create communities" on public.communities
  for insert with check (auth.uid() = created_by);

create policy "members can read own membership" on public.community_members
  for select using (auth.uid() = user_id);

create policy "users can join communities themselves" on public.community_members
  for insert with check (auth.uid() = user_id);

create policy "users can leave communities themselves" on public.community_members
  for delete using (auth.uid() = user_id);

create policy "users can read own likes" on public.observation_likes
  for select using (auth.uid() = user_id);

create policy "users can like as themselves" on public.observation_likes
  for insert with check (auth.uid() = user_id);

create policy "users can unlike as themselves" on public.observation_likes
  for delete using (auth.uid() = user_id);
