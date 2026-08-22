from fastapi import HTTPException, status
from supabase import Client


def create_comment(supabase: Client, observation_id: str, user_id: str, content: str) -> dict:
    post = supabase.table("observations").select("id").eq("id", observation_id).limit(1).execute()
    if not post.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    result = (
        supabase.table("observation_comments")
        .insert({"observation_id": observation_id, "user_id": user_id, "content": content})
        .execute()
    )
    comment = result.data[0]
    return _attach_user_name(supabase, [comment])[0]


def list_comments(supabase: Client, observation_id: str) -> list[dict]:
    result = (
        supabase.table("observation_comments")
        .select("*")
        .eq("observation_id", observation_id)
        .order("created_at")
        .execute()
    )
    return _attach_user_name(supabase, result.data)


def _attach_user_name(supabase: Client, comments: list[dict]) -> list[dict]:
    if not comments:
        return comments

    user_ids = {comment["user_id"] for comment in comments}
    names: dict[str, str | None] = {}
    for user_id in user_ids:
        profile = supabase.table("users").select("name").eq("id", user_id).limit(1).execute()
        names[user_id] = profile.data[0]["name"] if profile.data else None

    for comment in comments:
        comment["user_name"] = names.get(comment["user_id"])
    return comments
