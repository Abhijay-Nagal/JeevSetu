import secrets

from fastapi import HTTPException, status
from supabase import Client

from app.models.schema import CommunityCreate


def _slugify(name: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in name)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "community"


def create_community(supabase: Client, user_id: str, body: CommunityCreate) -> dict:
    slug = _slugify(body.name)

    # maybe_single() returns None (not a response) in supabase-py v2+
    # when no row matches — use limit(1) instead and check the list.
    existing = (
        supabase.table("communities").select("id").eq("slug", slug).limit(1).execute()
    )
    if existing.data:
        slug = f"{slug}-{secrets.token_hex(2)}"

    result = (
        supabase.table("communities")
        .insert(
            {
                "slug": slug,
                "name": body.name,
                "description": body.description,
                "created_by": user_id,
            }
        )
        .execute()
    )
    community = result.data[0]

    supabase.table("community_members").insert(
        {"community_id": community["id"], "user_id": user_id, "role": "creator"}
    ).execute()

    return community


def list_communities(supabase: Client) -> list[dict]:
    result = supabase.table("communities").select("*").order("created_at", desc=True).execute()
    return result.data


def list_my_communities(supabase: Client, user_id: str) -> list[dict]:
    memberships = (
        supabase.table("community_members")
        .select("community_id")
        .eq("user_id", user_id)
        .execute()
        .data
    )
    joined_ids = {membership["community_id"] for membership in memberships}
    if not joined_ids:
        return []

    all_communities = (
        supabase.table("communities").select("*").order("created_at", desc=True).execute().data
    )
    return [community for community in all_communities if community["id"] in joined_ids]


def get_community_by_slug(supabase: Client, slug: str) -> dict:
    result = supabase.table("communities").select("*").eq("slug", slug).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")
    return result.data[0]


def join_community(supabase: Client, community_id: str, user_id: str) -> dict:
    existing = (
        supabase.table("community_members")
        .select("*")
        .eq("community_id", community_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if existing.data:
        return existing.data[0]

    result = (
        supabase.table("community_members")
        .insert({"community_id": community_id, "user_id": user_id, "role": "member"})
        .execute()
    )
    return result.data[0]


def leave_community(supabase: Client, community_id: str, user_id: str) -> None:
    membership = (
        supabase.table("community_members")
        .select("role")
        .eq("community_id", community_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not membership.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a member")
    if membership.data[0]["role"] == "creator":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creator cannot leave their own community",
        )

    supabase.table("community_members").delete().eq("community_id", community_id).eq(
        "user_id", user_id
    ).execute()


def is_member(supabase: Client, community_id: str, user_id: str) -> bool:
    result = (
        supabase.table("community_members")
        .select("user_id")
        .eq("community_id", community_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return bool(result.data)
