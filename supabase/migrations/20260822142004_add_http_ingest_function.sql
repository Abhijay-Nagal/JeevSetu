create extension if not exists http;

create or replace function public.ingest_bnhs_item_set(p_source_type text, p_item_set_id bigint, p_per_page int default 100)
returns int language plpgsql as $$
declare
  v_page int := 1;
  v_url text;
  v_resp http_response;
  v_items jsonb;
  v_item jsonb;
  v_count int;
  v_total int := 0;
begin
  loop
    v_url := format('https://collections.bnhs.org/api/items?item_set_id=%s&per_page=%s&page=%s', p_item_set_id, p_per_page, v_page);
    select * into v_resp from http_get(v_url);
    v_items := v_resp.content::jsonb;
    v_count := jsonb_array_length(v_items);
    exit when v_count = 0;
    for v_item in select * from jsonb_array_elements(v_items)
    loop
      insert into public.documents (source_type, external_id, title, source_file, metadata)
      values (
        p_source_type,
        (v_item->>'o:id')::bigint,
        v_item->>'o:title',
        null,
        v_item
      )
      on conflict (source_type, external_id) do nothing;
      v_total := v_total + 1;
    end loop;
    exit when v_count < p_per_page;
    v_page := v_page + 1;
  end loop;
  return v_total;
end;
$$;
