-- Backend-owned email confirmation, replacing Supabase Auth's built-in
-- confirmation email (which uses Supabase's low-volume, easily-spam-flagged
-- default mailer). Our own service sends a branded email via the NGO's own
-- SMTP; confirming a token calls the Supabase admin API to set
-- email_confirm=true on the underlying auth user, so it has the same
-- real effect Supabase's own link would have had.
create table email_confirmations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id),
  token text not null unique,
  expires_at timestamptz not null,
  confirmed_at timestamptz,
  created_at timestamptz not null default now()
);

create index email_confirmations_token_idx on email_confirmations(token);
