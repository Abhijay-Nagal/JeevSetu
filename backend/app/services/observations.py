from fastapi import HTTPException, status
from supabase import Client

from app.models.schema import ObservationCreate, ObservationStatusUpdate
from app.services import rewards
from app.services.communities import get_community_by_slug, is_member
from app.services.notifications import notify_contributor


def create_observation(supabase: Client, user_id: str, body: ObservationCreate) -> dict:
    community_id = None
    if body.community_slug is not None:
        community = get_community_by_slug(supabase, body.community_slug)
        if not is_member(supabase, community["id"], user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Join the community before posting in it",
            )
        community_id = community["id"]

    row = {
        "species": body.species,
        "description": body.description,
        "location": body.location,
        "media_url": body.media_url,
        "user_id": user_id,
        "community_id": community_id,
    }
    result = supabase.table("observations").insert(row).execute()
    observation = result.data[0]

    rewards.award_coins(
        supabase, user_id, rewards.COINS_POST_CREATED, "post_created", observation["id"]
    )

    return _attach_author_name(supabase, [observation])[0]


def _attach_liked_by_me(supabase: Client, posts: list[dict], user_id: str) -> list[dict]:
    if not posts:
        return posts
    post_ids = [p["id"] for p in posts]
    likes = (
        supabase.table("observation_likes")
        .select("observation_id")
        .in_("observation_id", post_ids)
        .eq("user_id", user_id)
        .execute()
    )
    liked_ids = {like["observation_id"] for like in likes.data}
    for p in posts:
        p["liked_by_me"] = p["id"] in liked_ids
    return posts


def _attach_author_name(supabase: Client, posts: list[dict]) -> list[dict]:
    if not posts:
        return posts
    author_ids = list({p["user_id"] for p in posts})
    authors = (
        supabase.table("users").select("id, name, email").in_("id", author_ids).execute()
    )
    names_by_id = {row["id"]: row.get("name") or row.get("email") for row in authors.data}
    for p in posts:
        p["author_name"] = names_by_id.get(p["user_id"])
    return posts


def list_community_feed(supabase: Client, community_id: str, user_id: str) -> list[dict]:
    own_posts = (
        supabase.table("observations").select("*").eq("community_id", community_id).execute().data
    )
    global_posts = (
        supabase.table("observations").select("*").is_("community_id", "null").execute().data
    )
    combined = own_posts + global_posts
    posts = sorted(combined, key=lambda row: row["created_at"], reverse=True)
    posts = _attach_author_name(supabase, posts)
    return _attach_liked_by_me(supabase, posts, user_id)


def list_all_observations(supabase: Client, user_id: str) -> list[dict]:
    result = supabase.table("observations").select("*").order("created_at", desc=True).execute()
    posts = _attach_author_name(supabase, result.data)
    return _attach_liked_by_me(supabase, posts, user_id)


def list_own_observations(supabase: Client, user_id: str) -> list[dict]:
    result = (
        supabase.table("observations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    posts = _attach_author_name(supabase, result.data)
    return _attach_liked_by_me(supabase, posts, user_id)


def update_observation_status(
    supabase: Client, observation_id: str, body: ObservationStatusUpdate
) -> dict:
    current = (
        supabase.table("observations").select("status").eq("id", observation_id).limit(1).execute()
    )
    if not current.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")
    old_status = current.data[0]["status"]

    update = {"status": body.status}
    if body.assigned_researcher is not None:
        update["assigned_researcher"] = body.assigned_researcher
    updated = supabase.table("observations").update(update).eq("id", observation_id).execute()

    supabase.table("status_events").insert(
        {
            "observation_id": observation_id,
            "old_status": old_status,
            "new_status": body.status,
            "note": body.note,
        }
    ).execute()

    notify_contributor(observation_id, body.status)

    return updated.data[0]
