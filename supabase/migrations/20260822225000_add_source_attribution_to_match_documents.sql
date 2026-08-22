-- Search results gave no way to tell which actual document a chunk came
-- from beyond a bare URL -- no PDF filename, no attribution. Every ingested
-- source (Omeka collections, blog posts, newsletter PDFs) is published by
-- BNHS as an institution; the underlying feeds carry no per-item personal
-- author (the WordPress REST API's /users endpoint is disabled on
-- blog.bnhs.org, and the Omeka records have no dcterms:creator field), so
-- author is a constant rather than fabricated per-item data. file_name is
-- derived from the source URL only when it's an actual downloadable file
-- (currently just the newsletter PDFs); other source types have no
-- separate filename distinct from their title/URL, so it's left null.
--
-- Adds file_name/author columns to the return row, which Postgres treats as
-- a return-type change -- drop before recreate.
drop function if exists public.match_documents(vector, double precision, integer);

create function public.match_documents(
  query_embedding vector,
  match_threshold double precision,
  match_count integer
)
returns table (
  id uuid,
  title text,
  summary text,
  content_type text,
  source text,
  image_url text,
  bnhs_url text,
  file_name text,
  author text,
  similarity double precision
)
language plpgsql
as $$
begin
  return query
  select
    d.id,
    d.title,
    left(dc.content, 300) as summary,
    d.source_type as content_type,
    'BNHS' as source,
    null::text as image_url,
    coalesce(d.metadata->>'url', d.metadata->>'link', d.source_file) as bnhs_url,
    case
      when coalesce(d.metadata->>'url', d.source_file) ilike '%.pdf'
        then regexp_replace(coalesce(d.metadata->>'url', d.source_file), '^.*/', '')
      else null
    end as file_name,
    coalesce(d.metadata->>'author', 'Bombay Natural History Society (BNHS)') as author,
    1 - (dc.embedding <=> query_embedding) as similarity
  from document_chunks dc
  join documents d on d.id = dc.document_id
  where dc.embedding is not null
    and 1 - (dc.embedding <=> query_embedding) > match_threshold
  order by dc.embedding <=> query_embedding
  limit match_count;
end;
$$;
