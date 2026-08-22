insert into storage.buckets (id, name, public)
values ('observation-images', 'observation-images', true)
on conflict (id) do nothing;

create policy "anyone can view observation images"
  on storage.objects for select
  using (bucket_id = 'observation-images');

create policy "authenticated users can upload observation images"
  on storage.objects for insert
  with check (bucket_id = 'observation-images' and auth.role() = 'authenticated');
