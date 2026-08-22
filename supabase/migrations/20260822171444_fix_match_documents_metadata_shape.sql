-- The original match_documents extracted metadata->>'abstract', 'content_type',
-- 'source', 'image_url' -- keys that don't exist in documents.metadata (the
-- Omeka ingest stores raw dcterms:*/wo:* keys; blog_post/newsletter store
-- {title, content, link/url, date}). Every result came back with summary,
-- content_type, source, and image_url all NULL regardless of match quality.
--
-- Derives from what's actually there: summary from the matched chunk's own
-- content (a real excerpt, not a nonexistent metadata field), content_type
-- from source_type (meaningful across every row), bnhs_url from whichever
-- metadata key actually holds a link for that source_type.
create or replace function public.match_documents(
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
    1 - (dc.embedding <=> query_embedding) as similarity
  from document_chunks dc
  join documents d on d.id = dc.document_id
  where dc.embedding is not null
    and 1 - (dc.embedding <=> query_embedding) > match_threshold
  order by dc.embedding <=> query_embedding
  limit match_count;
end;
$$;
