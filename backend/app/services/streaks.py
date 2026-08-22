from datetime import date

from supabase import Client

FREEZE_MILESTONE_DAYS = 7
MAX_BANKED_FREEZES = 3


def get_streak(supabase: Client, user_id: str) -> dict:
    result = supabase.table("user_streaks").select("*").eq("user_id", user_id).limit(1).execute()
    if not result.data:
        return {"current_streak": 0, "longest_streak": 0, "freezes_available": 0}
    row = result.data[0]
    return {
        "current_streak": row["current_streak"],
        "longest_streak": row["longest_streak"],
        "freezes_available": row["freezes_available"],
    }


def update_streak(supabase: Client, user_id: str, answered_date: date) -> dict:
    """Advances the caller's streak for answering the daily question on
    `answered_date`. Lazily evaluated -- there's no cron job scanning for
    missed days, this just compares against the last answered date the next
    time the user actually answers. See docs/plan.md section 4.
    """
    existing = supabase.table("user_streaks").select("*").eq("user_id", user_id).limit(1).execute()
    row = existing.data[0] if existing.data else None

    if row is None:
        current_streak = 1
        freezes_available = 0
        freezes_used_total = 0
        longest_streak = 1
    else:
        last_answered = row["last_answered_date"]
        last_date = date.fromisoformat(last_answered) if last_answered else None
        freezes_available = row["freezes_available"]
        freezes_used_total = row["freezes_used_total"]

        if last_date is None:
            current_streak = 1
        else:
            gap = (answered_date - last_date).days
            if gap <= 0:
                # Already answered today (or a clock oddity) -- no change.
                return get_streak(supabase, user_id)
            elif gap == 1:
                current_streak = row["current_streak"] + 1
            elif freezes_available > 0:
                freezes_available -= 1
                freezes_used_total += 1
                current_streak = row["current_streak"] + 1
            else:
                current_streak = 1

        longest_streak = max(current_streak, row["longest_streak"])

    if current_streak % FREEZE_MILESTONE_DAYS == 0 and freezes_available < MAX_BANKED_FREEZES:
        freezes_available += 1

    payload = {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "last_answered_date": answered_date.isoformat(),
        "freezes_available": freezes_available,
        "freezes_used_total": freezes_used_total,
    }

    if row is None:
        supabase.table("user_streaks").insert({"user_id": user_id, **payload}).execute()
    else:
        supabase.table("user_streaks").update(payload).eq("user_id", user_id).execute()

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "freezes_available": freezes_available,
    }
