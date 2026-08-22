from fastapi import APIRouter, Depends, status
from supabase import Client

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.supabase_client import get_supabase
from app.models.schema import Observation, ObservationCreate, ObservationStatusUpdate
from app.services import observations

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
