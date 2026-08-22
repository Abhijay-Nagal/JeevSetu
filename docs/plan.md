# Reward System — Implementation Plan

**Status:** draft, for review. Nothing in this doc has been built yet.

**Branch:** `reward_system` (currently identical to `main`)

## 1. What this is

A Sweatcoin-inspired gamification layer: users earn digital coins for engaging with JeevSetu,
with a daily quiz question + streak as the main driver ("engage users continuously"), backed by
a real BNHS content pool via the RAG pipeline already built on `main`. Confirmed with you so far:

- **Redemption:** none in v1. Coins/streaks/leaderboards are gamification only — no real-world
  value, no payment processing, no legal/financial exposure. Real BNHS perks (membership/camp
  discounts) are an explicit future step once there's a partnership + admin redemption flow.
- **Coin sources:** quiz-first, plus small social bonuses (posting, getting likes, joining a
  community).
- **Daily question:** one shared question per day for everyone (Wordle-style), not personalized.
- **Streaks:** have a grace/freeze mechanic rather than a hard reset on a missed day.
- **Community quizzes:** community creators can author a timed quiz for their community; members
  attempt it while it's live; a leaderboard is revealed once the timer ends.

## 2. Two quiz surfaces

**Global daily question** — one question, same for every user, refreshes at midnight. Drives the
streak. Generated once per day from real BNHS content via the RAG pipeline already built
(`rag_pipeline.get_quiz`), so it stays grounded and doesn't need hand-authoring.

**Community quizzes** — a community creator picks a topic, a start time, and a duration. Members
attempt it once, any time inside that window. The per-question correct answers are hidden from
API responses until either the member has submitted their own attempt, or the quiz has ended —
otherwise a member could peek at another member's revealed answers via the shared quiz object.
The leaderboard (ranked by score, then speed) is only computed and shown after `ends_at`, per
your requirement.

Both reuse the same generation building block (`rag_pipeline._generate_json` grounded via
`_retrieve_context`) that already powers `/api/quiz` — this isn't new AI-pipeline work, just new
scheduling/storage/scoring around it.

## 3. Data model

All new tables, one migration. `users.coin_balance` is a denormalized fast-read column; the
`coin_transactions` table is the source of truth / audit trail (what the "transaction history" UI
reads from).

```sql
alter table users add column coin_balance integer not null default 0;

create table coin_transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id),
  amount integer not null,               -- positive = earn (no spends in v1, but signed for later)
  reason text not null,                  -- 'daily_question_correct' | 'streak_milestone' |
                                          -- 'community_quiz_score' | 'community_quiz_placement' |
                                          -- 'post_created' | 'post_liked' | 'community_joined' | 'community_created'
  reference_id uuid,                     -- points at the row that caused this (attempt id, observation id, etc.)
  created_at timestamptz not null default now()
);

create table daily_questions (
  id uuid primary key default gen_random_uuid(),
  question_date date not null unique,
  question text not null,
  options jsonb not null,                -- 4 strings
  correct_answer int not null,           -- 0-3, never sent to the client pre-attempt
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
  unique (daily_question_id, user_id)    -- hard stop on double-answering, no rate-limit bookkeeping needed
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
  bonus_awarded boolean not null default false,   -- guards the placement-bonus payout from running twice
  created_at timestamptz not null default now()
);

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
```

**`award_coins` as a Postgres function**, not two separate client calls — a plain
`insert coin_transactions` + `update users.coin_balance` from Python risks the two drifting apart
if one fails, and there's no transaction spanning two supabase-py calls. One RPC does both
atomically, same pattern as `match_documents`:

```sql
create function award_coins(p_user_id uuid, p_amount int, p_reason text, p_reference_id uuid default null)
returns void language plpgsql as $$
begin
  insert into coin_transactions (user_id, amount, reason, reference_id)
  values (p_user_id, p_amount, p_reason, p_reference_id);

  update users set coin_balance = coin_balance + p_amount where id = p_user_id;
end;
$$;
```

## 4. Streak logic (lazy evaluation, no cron needed)

Runs inside `submit_answer()` for the daily question, comparing `user_streaks.last_answered_date`
to today:

- **First ever answer** (`last_answered_date is null`): `current_streak = 1`.
- **Answered yesterday**: `current_streak += 1`.
- **Gap of 2+ days AND `freezes_available > 0`**: consume one freeze (`freezes_available -= 1`,
  `freezes_used_total += 1`), streak bridges the gap and continues incrementing instead of
  resetting.
- **Gap of 2+ days, no freeze available**: `current_streak = 1` (streak restarts).
- Always: `longest_streak = max(longest_streak, current_streak)`, `last_answered_date = today`.
- **Earning freezes**: +1 freeze every 7-day streak milestone (`current_streak % 7 == 0`), capped
  at 3 banked freezes so they can't be hoarded indefinitely. Flagging the cap and the "every 7
  days" cadence as tunable numbers, not settled facts — easy to change in one place.

No scheduled job checks for missed days — the check only happens the next time the user actually
answers, which is both simpler to build and correct (a user who never comes back doesn't need
their streak "processed").

## 5. Coin amounts (flagged for your review — placeholder numbers, not final)

| Action | Coins | Notes |
|---|---|---|
| Daily question, correct | 10 | |
| Daily question, wrong | 0 | attempt still recorded, still counts toward "answered today" for streak purposes |
| Streak milestone (every 7 days) | +20 bonus | on top of the day's 10 |
| Community quiz, per correct answer | 5 | |
| Community quiz, placement bonus (top 3 once quiz ends) | 50 / 30 / 15 | 1st / 2nd / 3rd |
| Creating a post | 5 | |
| Your post gets liked | 2 | paid to the post's **author**, not the liker |
| Joining a community | 10 | one-time per community |
| Creating a community | 25 | one-time |

All amounts live as named constants in `app/services/rewards.py` so they're a one-place edit.

## 6. Anti-abuse — decisions I made by default, flagging for your sign-off

- **Daily question**: the `unique(daily_question_id, user_id)` constraint is the entire
  anti-farming mechanism — one attempt per day, full stop, no separate rate-limit code needed.
- **Community quiz**: same pattern, `unique(community_quiz_id, user_id)`.
- **Self-liking for coins**: `likes.py` currently has no self-like prevention at all — a user can
  like their own post today. I'm adding a same-author check specifically at the coin-award site
  (`if post.user_id == liker_id: skip award`) so this can't be farmed, without changing the
  existing like/unlike behavior itself. Worth deciding separately whether self-liking should be
  blocked outright, but that's a pre-existing behavior question, not a new one this feature
  introduces.
- **Baseline social actions (post/like/join) daily caps**: not yet confirmed with you. My
  recommendation is a modest daily cap (e.g. max 5 posts/day and max 20 likes-received/day count
  toward coins) so the leaderboard can't be trivially inflated by spam-posting. Flagging this as
  open — tell me if you'd rather ship uncapped for now.
- **"Community admin"**: the existing `community_members.role` type is only
  `Literal["creator", "member"]` — there's no separate "admin" role yet. I'm treating "creator" as
  the quiz-creation permission for v1 (reusing the exact same permission check
  `communities.py` already uses elsewhere), unless you want a real admin tier added — that would
  be a bigger change (role management UI, promote/demote members) and I'd treat it as a separate
  follow-up rather than bundling it into this feature.

## 7. Backend structure (Backend.md conventions: thin routers, service layer, `Depends()`)

**New migration:** `supabase/migrations/<ts>_create_reward_system_tables.sql` — everything in §3.

**New models** (`app/models/schema.py`): `WalletSummary`, `CoinTransactionOut`, `DailyQuestionPublic`
(no `correct_answer`/`explanation` until answered), `DailyQuestionAnswer`, `DailyQuestionResult`,
`StreakStatus`, `CommunityQuizCreate`, `CommunityQuizPublic`, `CommunityQuizAttemptSubmit`,
`CommunityQuizAttemptResult`, `LeaderboardEntry`.

**New services:**
- `app/services/rewards.py` — `award_coins(supabase, user_id, amount, reason, reference_id=None)`
  wrapping the RPC; the coin-amount constants table from §5.
- `app/services/streaks.py` — `update_streak(supabase, user_id, answered_date)` implementing §4.
- `app/services/daily_question.py` — `get_or_create_todays_question(supabase)` (lazy-generates via
  `rag_pipeline.get_quiz` on first request each day if no row exists for `question_date = today`,
  topic chosen by rotating through a fixed list of BNHS themes so it isn't the same subject every
  day), `submit_answer(supabase, user_id, selected_answer)`.
- `app/services/community_quizzes.py` — `create_quiz(...)` (creator-role check reusing the
  existing community permission pattern), `get_quiz_for_member(...)` (hides answers per the rule
  in §2), `submit_attempt(...)` (rejects attempts outside `[starts_at, ends_at]`, rejects a second
  attempt via the unique constraint), `get_leaderboard(...)` (returns "not ended yet" instead of
  data before `ends_at`; lazily computes and pays the top-3 placement bonus on first leaderboard
  read after `ends_at`, guarded by `bonus_awarded` so it can't double-pay).

**New/modified routers:**
- `app/routers/rewards.py`, prefix `/rewards`:
  - `GET /rewards/wallet` — balance + paginated transaction history
  - `GET /rewards/daily-question` — today's question (answers hidden) + already-answered flag +
    current streak/freeze status
  - `POST /rewards/daily-question/answer` — submit, returns correctness + coins awarded + updated
    streak
- `app/routers/communities.py` (extend, not a new router — these are community-scoped) or a new
  `app/routers/community_quizzes.py` mounted at the same prefix:
  - `POST /communities/{slug}/quizzes` — create (creator only)
  - `GET /communities/{slug}/quizzes` — list, with a derived `status` (`upcoming`/`live`/`ended`)
  - `GET /communities/{slug}/quizzes/{quiz_id}` — questions (answers hidden per §2)
  - `POST /communities/{slug}/quizzes/{quiz_id}/attempt` — submit all answers at once (simplest
    for v1 versus per-question submission/live sync)
  - `GET /communities/{slug}/quizzes/{quiz_id}/leaderboard`

**Existing services get one new call each**, not a rewrite: `observations.create_observation`
calls `rewards.award_coins(..., "post_created")` after insert; `likes.like_observation` calls it
(with the self-like guard from §6) after the like is recorded; `communities.create_community` /
`join_community` call it after their inserts.

## 8. Frontend structure

- **Wallet visibility**: a coin balance badge in `AppLayout`'s sidebar, next to the user's name —
  Sweatcoin keeps the number visible at all times, so this should too, not buried in a separate
  page.
- **New page** `pages/Rewards.jsx` (route `/rewards`, `layout: "app"`, added to the sidebar nav
  list in `AppLayout.jsx`) — today's daily question card, current streak + freeze count, coin
  transaction history.
- **Shared `QuizQuestionCard` component**, extracted from the click-to-attempt quiz UI already
  built in `RAGPage.jsx` (lock-in-a-choice, reveal correct/incorrect, show explanation) — both the
  daily question and community quizzes render through this one component instead of duplicating
  the interaction.
- **Community quiz UI**, inside `CommunityDetail.jsx`: a "Create Quiz" button visible only to the
  community's creator, a countdown/timer while a quiz is live, the quiz itself once a member opens
  it, and a leaderboard view that only renders once the quiz has ended (matches the backend's
  "not ended yet" response).

## 9. Build order

1. Migration (§3) + `award_coins` RPC — foundation everything else depends on.
2. `rewards.py` service + `/rewards/wallet` endpoint + sidebar coin badge — smallest possible
   vertical slice to prove the ledger works end-to-end before building quiz logic on top of it.
3. Daily question + streak (§4) — the main "engage continuously" driver, ship this before
   community quizzes since it's the higher-priority mechanic per your steer.
4. Baseline social bonuses (post/like/join hooks) — small, mechanical, low risk once `rewards.py`
   exists.
5. Community quizzes end-to-end (create → attempt → timer → leaderboard → placement bonus) —
   largest single piece, built last since it's the most novel/complex part.

## 10. Explicitly out of scope for v1

- Real-world coin redemption (BNHS discounts, membership perks) — flagged in §1, future work once
  there's a partnership and an admin-side redemption/coupon flow.
- A global cross-community leaderboard (only per-community quiz leaderboards + personal streak in
  v1) — easy follow-up once the per-community version works.
- Levels/badges beyond a raw coin balance — not asked for; defaulting to balance + transaction
  history only, flagging in case you want tiers/badge art added later.
- Personalized daily questions — you picked the shared single-question-for-everyone model.
