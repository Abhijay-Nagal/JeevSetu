from fastapi import APIRouter, Depends, status
from supabase import Client

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.supabase_client import get_supabase
from app.models.schema import LikeStatus, Observation, ObservationCreate, ObservationStatusUpdate
from app.services import likes, observations

router = APIRouter(prefix="/observations", tags=["community"])

require_staff_or_researcher = require_role("staff", "researcher")


@router.post("", response_model=Observation, status_code=status.HTTP_201_CREATED)
async def create_observation(
    body: ObservationCreate,
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return observations.create_observation(supabase, user.id, body)


@router.get("", response_model=list[Observation])
async def list_observations(
    user: CurrentUser = Depends(require_staff_or_researcher),
    supabase: Client = Depends(get_supabase),
):
    return observations.list_all_observations(supabase)


@router.get("/mine", response_model=list[Observation])
async def my_observations(
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return observations.list_own_observations(supabase, user.id)


@router.patch("/{observation_id}", response_model=Observation)
async def update_observation_status(
    observation_id: str,
    body: ObservationStatusUpdate,
    user: CurrentUser = Depends(require_staff_or_researcher),
    supabase: Client = Depends(get_supabase),
):
    return observations.update_observation_status(supabase, observation_id, body)


@router.post("/{observation_id}/like", response_model=LikeStatus)
async def like_observation(
    observation_id: str,
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return likes.like_observation(supabase, observation_id, user.id)


@router.delete("/{observation_id}/like", response_model=LikeStatus)
async def unlike_observation(
    observation_id: str,
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return likes.unlike_observation(supabase, observation_id, user.id)
