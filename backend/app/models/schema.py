from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

Role = Literal["contributor", "staff", "researcher"]
ObservationStatus = Literal["submitted", "under_review", "forwarded", "responded"]


class User(BaseModel):
    id: UUID
    email: str
    role: Role
    created_at: datetime


class ObservationCreate(BaseModel):
    species: str | None = None
    description: str | None = None
    location: str | None = None
    media_url: str | None = None


class Observation(ObservationCreate):
    id: UUID
    user_id: UUID
    status: ObservationStatus = "submitted"
    assigned_researcher: str | None = None
    created_at: datetime
    updated_at: datetime


class ObservationStatusUpdate(BaseModel):
    status: ObservationStatus
    note: str | None = None
    assigned_researcher: str | None = None


class StatusEvent(BaseModel):
    id: UUID
    observation_id: UUID
    old_status: ObservationStatus | None
    new_status: ObservationStatus
    note: str | None = None
    created_at: datetime


class RagQuery(BaseModel):
    question: str


class RagSource(BaseModel):
    title: str
    excerpt: str


class RagAnswer(BaseModel):
    answer: str
    sources: list[RagSource]
