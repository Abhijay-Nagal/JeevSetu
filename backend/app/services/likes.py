from supabase import Client


def like_observation(supabase: Client, observation_id: str, user_id: str) -> dict:
    if not _has_liked(supabase, observation_id, user_id):
        supabase.table("observation_likes").insert(
            {"observation_id": observation_id, "user_id": user_id}
        ).execute()
        _adjust_like_count(supabase, observation_id, delta=1)

    return _like_status(supabase, observation_id, liked_by_me=True)


def unlike_observation(supabase: Client, observation_id: str, user_id: str) -> dict:
    if _has_liked(supabase, observation_id, user_id):
        supabase.table("observation_likes").delete().eq("observation_id", observation_id).eq(
            "user_id", user_id
        ).execute()
        _adjust_like_count(supabase, observation_id, delta=-1)

    return _like_status(supabase, observation_id, liked_by_me=False)


def _has_liked(supabase: Client, observation_id: str, user_id: str) -> bool:
    result = (
        supabase.table("observation_likes")
        .select("user_id")
        .eq("observation_id", observation_id)
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    return result.data is not None


def _adjust_like_count(supabase: Client, observation_id: str, delta: int) -> None:
    current = (
        supabase.table("observations")
        .select("like_count")
        .eq("id", observation_id)
        .maybe_single()
        .execute()
    )
    new_count = max(current.data["like_count"] + delta, 0)
    supabase.table("observations").update({"like_count": new_count}).eq(
        "id", observation_id
    ).execute()


def _like_status(supabase: Client, observation_id: str, liked_by_me: bool) -> dict:
    current = (
        supabase.table("observations")
        .select("like_count")
        .eq("id", observation_id)
        .maybe_single()
        .execute()
    )
    return {
        "observation_id": observation_id,
        "like_count": current.data["like_count"],
        "liked_by_me": liked_by_me,
    }
