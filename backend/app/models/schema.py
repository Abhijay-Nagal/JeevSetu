from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field

Role = Literal["contributor", "staff", "researcher"]
ObservationStatus = Literal["submitted", "under_review", "forwarded", "responded"]


class User(BaseModel):
    id: UUID
    email: str
    name: str | None = None
    role: Role
    created_at: datetime


class SendConfirmationRequest(BaseModel):
    user_id: UUID
    email: str
    name: str


class ConfirmEmailRequest(BaseModel):
    token: str


class ConfirmEmailResult(BaseModel):
    already_confirmed: bool


class ObservationCreate(BaseModel):
    species: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    location: str | None = Field(default=None, max_length=500)
    media_url: str | None = Field(default=None, max_length=2000)
    community_slug: str | None = Field(default=None, max_length=200)


class Observation(BaseModel):
    id: UUID
    user_id: UUID
    author_name: str | None = None
    species: str | None = None
    description: str | None = None
    location: str | None = None
    media_url: str | None = None
    status: ObservationStatus = "submitted"
    assigned_researcher: str | None = None
    community_id: UUID | None = None
    like_count: int = 0
    liked_by_me: bool = False
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


# 1. Search Schemas
class SearchQuery(BaseModel):
    query: str = Field(max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)
    filter_type: str | None = Field(default=None, max_length=100)


class SearchResultCard(BaseModel):
    id: str | None = None
    title: str
    summary: str | None = None
    content_type: str | None = None
    source: str | None = None
    image_url: str | None = None
    bnhs_url: str | None = None
    file_name: str | None = None
    author: str | None = None
    similarity_score: float | None = None


class SearchResponse(BaseModel):
    results: list[SearchResultCard]


# 2. Next Steps Schemas
class CurrentResource(BaseModel):
    title: str
    content: str | None = None
    type: str | None = None


class NextStepsQuery(BaseModel):
    current_resource: CurrentResource
    user_interests: list[str] | None = None


class NextStepAction(BaseModel):
    action_label: str = Field(description="One of: Learn, Explore, Play, Take a quiz, Contribute, Advocate")
    description: str
    direct_link: str | None = None


class NextStepsResponse(BaseModel):
    actions: list[NextStepAction]


# 3. Quiz Schemas
class QuizQuery(BaseModel):
    topic: str = Field(max_length=500)
    num_questions: int = Field(default=5, ge=1, le=20)


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(description="Must contain exactly 4 options (A,B,C,D formatting optional)")
    correct_answer: int = Field(description="Index (0-3) of the correct option")
    explanation: str
    source_reference: str | None = None


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]


# 4. Community Schemas
class CommunityCreate(BaseModel):
    name: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class Community(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str | None
    created_by: UUID
    created_at: datetime


class CommunityMember(BaseModel):
    community_id: UUID
    user_id: UUID
    role: Literal["creator", "member"]
    joined_at: datetime


class LikeStatus(BaseModel):
    observation_id: UUID
    like_count: int
    liked_by_me: bool


class CommentCreate(BaseModel):
    content: str = Field(max_length=5000)


class Comment(BaseModel):
    id: UUID
    observation_id: UUID
    user_id: UUID
    user_name: str | None = None
    content: str
    created_at: datetime


# 5. Research Submissions ("Publications") Schemas
class RelatedRecordsQuery(BaseModel):
    abstract: str


class ResearchSubmissionCreate(BaseModel):
    title: str = Field(max_length=500)
    abstract: str = Field(max_length=10000)
    description: str | None = Field(default=None, max_length=10000)
    species: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=500)
    media_url: str | None = Field(default=None, max_length=2000)


class ResearchSubmission(ResearchSubmissionCreate):
    id: UUID
    user_id: UUID
    created_at: datetime


# 6. Reward System Schemas
class CoinTransactionOut(BaseModel):
    id: UUID
    amount: int
    reason: str
    reference_id: UUID | None = None
    created_at: datetime


class WalletSummary(BaseModel):
    coin_balance: int
    recent_transactions: list[CoinTransactionOut]


class StreakStatus(BaseModel):
    current_streak: int
    longest_streak: int
    freezes_available: int


class DailyQuestionPublic(BaseModel):
    id: UUID
    question: str
    options: list[str]
    already_answered: bool
    streak: StreakStatus


class DailyQuestionAnswer(BaseModel):
    selected_answer: int


class DailyQuestionResult(BaseModel):
    is_correct: bool
    correct_answer: int
    explanation: str | None = None
    coins_awarded: int
    streak: StreakStatus


# 7. Analytics / SHAP Schemas
class ShapExplanation(BaseModel):
    feature_name: str
    shap_value: float
    feature_value: float


class UserEngagementProfile(BaseModel):
    user_id: str
    features: dict[str, float]
    risk_score: float
    risk_label: str
    shap_explanations: list[ShapExplanation]
    cv_metrics: dict | None = None


class EngagementDashboard(BaseModel):
    total_users: int
    at_risk_count: int
    avg_risk_score: float
    cv_metrics: dict
    users: list[UserEngagementProfile]
