from fastapi import HTTPException, status
from supabase import Client

from app.models.schema import ObservationCreate, ObservationStatusUpdate
from app.services.notifications import notify_contributor


def create_observation(supabase: Client, user_id: str, body: ObservationCreate) -> dict:
    row = {**body.model_dump(), "user_id": user_id}
    result = supabase.table("observations").insert(row).execute()
    return result.data[0]


def list_all_observations(supabase: Client) -> list[dict]:
    result = supabase.table("observations").select("*").order("created_at", desc=True).execute()
    return result.data


def list_own_observations(supabase: Client, user_id: str) -> list[dict]:
    result = (
        supabase.table("observations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def update_observation_status(
    supabase: Client, observation_id: str, body: ObservationStatusUpdate
) -> dict:
    current = (
        supabase.table("observations").select("status").eq("id", observation_id).single().execute()
    )
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
