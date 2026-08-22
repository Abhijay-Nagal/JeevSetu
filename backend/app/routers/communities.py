from fastapi import APIRouter, Depends, status
from supabase import Client

from app.core.auth import CurrentUser, get_current_user
from app.core.supabase_client import get_supabase
from app.models.schema import Community, CommunityCreate, CommunityMember
from app.services import communities

router = APIRouter(prefix="/communities", tags=["communities"])


@router.post("", response_model=Community, status_code=status.HTTP_201_CREATED)
async def create_community(
    body: CommunityCreate,
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return communities.create_community(supabase, user.id, body)


@router.get("", response_model=list[Community])
async def list_communities(supabase: Client = Depends(get_supabase)):
    return communities.list_communities(supabase)


@router.get("/{slug}", response_model=Community)
async def get_community(slug: str, supabase: Client = Depends(get_supabase)):
    return communities.get_community_by_slug(supabase, slug)


@router.post("/{slug}/join", response_model=CommunityMember, status_code=status.HTTP_201_CREATED)
async def join_community(
    slug: str,
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    community = communities.get_community_by_slug(supabase, slug)
    return communities.join_community(supabase, community["id"], user.id)


@router.delete("/{slug}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_community(
    slug: str,
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    community = communities.get_community_by_slug(supabase, slug)
    communities.leave_community(supabase, community["id"], user.id)
