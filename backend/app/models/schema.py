from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

Role = Literal["contributor", "staff", "researcher"]
ObservationStatus = Literal["submitted", "under_review", "forwarded", "responded"]


class User(BaseModel):
    id: UUID
    email: str
    name: str | None = None
    role: Role
    created_at: datetime


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=24)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=254)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class UserProfile(BaseModel):
    id: str
    username: str | None = None
    name: str | None = None
    email: str | None = None
    role: str = "contributor"
    coin_balance: int = 0
    created_at: datetime | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class UsernameAvailability(BaseModel):
    username: str
    available: bool
    reason: str | None = None


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

    @field_validator("media_url")
    @classmethod
    def media_url_must_be_web_or_upload(cls, value: str | None) -> str | None:
        if value and not value.startswith(("https://", "http://", "/api/uploads/")):
            raise ValueError("media_url must be an uploaded image or an http(s) link")
        return value

    @model_validator(mode="after")
    def must_have_content(self) -> "ObservationCreate":
        if not ((self.species or "").strip() or (self.description or "").strip() or self.media_url):
            raise ValueError("A post needs a species, a description or a photo")
        return self


class Observation(BaseModel):
    id: UUID
    user_id: UUID
    author_username: str | None = None
    comment_count: int = 0
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
    content: str = Field(min_length=1, max_length=5000)

    @field_validator("content")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Comment can't be empty")
        return value.strip()


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


# 8. Knowledge Hub chat
class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=10)


class AskSource(BaseModel):
    title: str
    excerpt: str | None = None
    url: str | None = None
    content_type: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[AskSource]
    generated_by: Literal["llm", "archive"]


# 9. Notifications
class Notification(BaseModel):
    id: str
    type: Literal["comment", "like", "reward", "status", "welcome"]
    title: str
    message: str
    link: str | None = None
    created_at: datetime


# 10. Collectable cards
class Card(BaseModel):
    id: str
    name: str
    scientific_name: str
    rarity: Literal["Common", "Rare", "Epic", "Legendary"]
    price: int
    color: str
    image: str | None = None
    icon: str
    habitat: str
    description: str
    iucn_status: str | None = None
    owned: bool = False


class CardCollection(BaseModel):
    coin_balance: int
    cards: list[Card]
