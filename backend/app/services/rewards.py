from supabase import Client

# Placeholder amounts -- flagged for review in docs/plan.md section 5. One
# place to tune once the numbers are confirmed.
COINS_DAILY_QUESTION_CORRECT = 10
COINS_STREAK_MILESTONE = 20
COINS_COMMUNITY_QUIZ_PER_CORRECT = 5
COINS_COMMUNITY_QUIZ_PLACEMENT = {1: 50, 2: 30, 3: 15}
COINS_POST_CREATED = 5
COINS_POST_LIKED = 2
COINS_COMMUNITY_JOINED = 10
COINS_COMMUNITY_CREATED = 25

WALLET_HISTORY_LIMIT = 20


def award_coins(
    supabase: Client, user_id: str, amount: int, reason: str, reference_id: str | None = None
) -> None:
    """Atomically records a ledger entry and updates the balance via the
    award_coins Postgres function (see migrations) -- two separate client
    calls here would risk the ledger and balance drifting apart if one
    failed.
    """
    supabase.rpc(
        "award_coins",
        {
            "p_user_id": user_id,
            "p_amount": amount,
            "p_reason": reason,
            "p_reference_id": reference_id,
        },
    ).execute()


def get_wallet(supabase: Client, user_id: str) -> dict:
    profile = supabase.table("users").select("coin_balance").eq("id", user_id).limit(1).execute()
    balance = profile.data[0]["coin_balance"] if profile.data else 0

    transactions = (
        supabase.table("coin_transactions")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(WALLET_HISTORY_LIMIT)
        .execute()
    )

    return {"coin_balance": balance, "recent_transactions": transactions.data}
