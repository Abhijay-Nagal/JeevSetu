from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import CurrentUser, get_current_user, require_role
from app.core.supabase_client import get_supabase
from app.models.schema import Observation, ObservationCreate, ObservationStatusUpdate
from app.services.notifications import notify_contributor

router = APIRouter(prefix="/observations", tags=["community"])


@router.post("", response_model=Observation, status_code=status.HTTP_201_CREATED)
async def create_observation(
    body: ObservationCreate,
    user: CurrentUser = Depends(get_current_user),
):
    supabase = get_supabase()
    row = {**body.model_dump(), "user_id": user.id}
    result = supabase.table("observations").insert(row).execute()
    return result.data[0]


@router.get("", response_model=list[Observation])
async def list_observations(user: CurrentUser = Depends(require_role("staff", "researcher"))):
    supabase = get_supabase()
    result = supabase.table("observations").select("*").order("created_at", desc=True).execute()
    return result.data


@router.get("/mine", response_model=list[Observation])
async def my_observations(user: CurrentUser = Depends(get_current_user)):
    supabase = get_supabase()
    result = (
        supabase.table("observations")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.patch("/{observation_id}", response_model=Observation)
async def update_observation_status(
    observation_id: str,
    body: ObservationStatusUpdate,
    user: CurrentUser = Depends(require_role("staff", "researcher")),
):
    supabase = get_supabase()

    current = supabase.table("observations").select("status").eq("id", observation_id).single().execute()
    if not current.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")
    old_status = current.data["status"]

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
