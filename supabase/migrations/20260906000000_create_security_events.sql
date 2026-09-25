-- Optional security events table for threat logging.
-- The ThreatLoggingMiddleware in app/core/security.py writes here on 4xx/5xx
-- responses. If this table doesn't exist, the middleware degrades gracefully
-- (logs to stderr only).

create table if not exists security_events (
  id uuid primary key default gen_random_uuid(),
  event_type text not null,
  method text not null,
  path text not null,
  status_code integer not null,
  client_ip text,
  duration_ms integer,
  created_at timestamptz not null default now()
);

create index security_events_created_at_idx on security_events(created_at desc);
create index security_events_event_type_idx on security_events(event_type);
