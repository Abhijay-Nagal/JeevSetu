from supabase import Client

from app.services import rewards


def like_observation(supabase: Client, observation_id: str, user_id: str) -> dict:
    if not _has_liked(supabase, observation_id, user_id):
        supabase.table("observation_likes").insert(
            {"observation_id": observation_id, "user_id": user_id}
        ).execute()
        _adjust_like_count(supabase, observation_id, delta=1)
        _award_like_coins(supabase, observation_id, liker_id=user_id)

    return _like_status(supabase, observation_id, liked_by_me=True)


def unlike_observation(supabase: Client, observation_id: str, user_id: str) -> dict:
    if _has_liked(supabase, observation_id, user_id):
        supabase.table("observation_likes").delete().eq("observation_id", observation_id).eq(
            "user_id", user_id
        ).execute()
        _adjust_like_count(supabase, observation_id, delta=-1)

    return _like_status(supabase, observation_id, liked_by_me=False)


def _has_liked(supabase: Client, observation_id: str, user_id: str) -> bool:
    # maybe_single() returns None in supabase-py v2+ when no row matches — use limit(1)
    result = (
        supabase.table("observation_likes")
        .select("user_id")
        .eq("observation_id", observation_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return bool(result.data)


def _adjust_like_count(supabase: Client, observation_id: str, delta: int) -> None:
    current = (
        supabase.table("observations")
        .select("like_count")
        .eq("id", observation_id)
        .limit(1)
        .execute()
    )
    if not current.data:
        return
    new_count = max(current.data[0]["like_count"] + delta, 0)
    supabase.table("observations").update({"like_count": new_count}).eq(
        "id", observation_id
    ).execute()


def _award_like_coins(supabase: Client, observation_id: str, liker_id: str) -> None:
    post = supabase.table("observations").select("user_id").eq("id", observation_id).limit(1).execute()
    if not post.data:
        return
    author_id = post.data[0]["user_id"]
    if author_id == liker_id:
        # likes.py has no self-like prevention today -- guard the coin award
        # specifically so self-liking can't be farmed, without changing the
        # existing like/unlike behavior itself.
        return
    rewards.award_coins(supabase, author_id, rewards.COINS_POST_LIKED, "post_liked", observation_id)


def _like_status(supabase: Client, observation_id: str, liked_by_me: bool) -> dict:
    current = (
        supabase.table("observations")
        .select("like_count")
        .eq("id", observation_id)
        .limit(1)
        .execute()
    )
    like_count = current.data[0]["like_count"] if current.data else 0
    return {
        "observation_id": observation_id,
        "like_count": like_count,
        "liked_by_me": liked_by_me,
    }
