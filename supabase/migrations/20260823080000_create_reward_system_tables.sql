-- Reward system: coin wallet, daily question + streak, and timed community
-- quizzes with a leaderboard. See docs/plan.md for the full design.

alter table users add column coin_balance integer not null default 0;

create table coin_transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id),
  amount integer not null,
  reason text not null,
  reference_id uuid,
  created_at timestamptz not null default now()
);

create index coin_transactions_user_id_idx on coin_transactions(user_id);

create table daily_questions (
  id uuid primary key default gen_random_uuid(),
  question_date date not null unique,
  question text not null,
  options jsonb not null,
  correct_answer int not null,
  explanation text,
  source_reference text,
  created_at timestamptz not null default now()
);

create table daily_question_attempts (
  id uuid primary key default gen_random_uuid(),
  daily_question_id uuid not null references daily_questions(id),
  user_id uuid not null references users(id),
  selected_answer int not null,
  is_correct boolean not null,
  answered_at timestamptz not null default now(),
  unique (daily_question_id, user_id)
);

create table user_streaks (
  user_id uuid primary key references users(id),
  current_streak int not null default 0,
  longest_streak int not null default 0,
  last_answered_date date,
  freezes_available int not null default 0,
  freezes_used_total int not null default 0,
  updated_at timestamptz not null default now()
);

create table community_quizzes (
  id uuid primary key default gen_random_uuid(),
  community_id uuid not null references communities(id),
  created_by uuid not null references users(id),
  title text not null,
  topic text not null,
  starts_at timestamptz not null,
  ends_at timestamptz not null,
  bonus_awarded boolean not null default false,
  created_at timestamptz not null default now()
);

create index community_quizzes_community_id_idx on community_quizzes(community_id);

create table community_quiz_questions (
  id uuid primary key default gen_random_uuid(),
  community_quiz_id uuid not null references community_quizzes(id),
  question_index int not null,
  question text not null,
  options jsonb not null,
  correct_answer int not null,
  explanation text
);

create table community_quiz_attempts (
  id uuid primary key default gen_random_uuid(),
  community_quiz_id uuid not null references community_quizzes(id),
  user_id uuid not null references users(id),
  score int not null,
  time_taken_seconds int not null,
  completed_at timestamptz not null default now(),
  unique (community_quiz_id, user_id)
);

-- Atomic ledger write + balance update -- a plain insert-then-update from the
-- Python client risks the two drifting apart if one call fails, and
-- supabase-py can't span a transaction across two separate requests.
create function award_coins(p_user_id uuid, p_amount int, p_reason text, p_reference_id uuid default null)
returns void language plpgsql as $$
begin
  insert into coin_transactions (user_id, amount, reason, reference_id)
  values (p_user_id, p_amount, p_reason, p_reference_id);

  update users set coin_balance = coin_balance + p_amount where id = p_user_id;
end;
$$;
