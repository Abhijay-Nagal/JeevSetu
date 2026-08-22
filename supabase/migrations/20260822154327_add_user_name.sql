alter table public.users add column name text;

-- Capture the display name passed at signup (supabase.auth.signUp({ options: { data: { name } } })).
create or replace function public.handle_new_auth_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.users (id, email, name)
  values (new.id, new.email, new.raw_user_meta_data->>'name');
  return new;
end;
$$;
