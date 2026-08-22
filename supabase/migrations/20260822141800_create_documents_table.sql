create table public.documents (
  id uuid primary key default gen_random_uuid(),
  source_type text not null,
  external_id bigint,
  title text,
  source_file text,
  metadata jsonb,
  created_at timestamptz not null default now()
);

create index documents_source_type_idx on public.documents (source_type);
create index documents_metadata_gin_idx on public.documents using gin (metadata);
create unique index documents_source_type_external_id_idx on public.documents (source_type, external_id);
