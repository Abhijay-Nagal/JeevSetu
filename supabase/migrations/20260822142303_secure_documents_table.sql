alter table public.documents enable row level security;

create policy "documents are publicly readable"
  on public.documents for select
  using (true);

alter function public.ingest_bnhs_item_set(text, bigint, int) set search_path = public;
