"""Staff-only analytics endpoints — engagement predictions + SHAP explanations."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import CurrentUser, require_role
from app.models.schema import EngagementDashboard, UserEngagementProfile
from app.services import analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/engagement", response_model=EngagementDashboard)
async def engagement_dashboard(
    _user: CurrentUser = Depends(require_role("staff")),
):
    """Returns all users with churn risk scores, SHAP explanations, and KPIs.

    Staff-only. The model is trained on-the-fly from live Supabase data.
    """
    return analytics.get_engagement_dashboard()


@router.get("/engagement/{user_id}", response_model=UserEngagementProfile)
async def user_engagement(
    user_id: str,
    _user: CurrentUser = Depends(require_role("staff")),
):
    """Returns a single user's detailed risk profile with full SHAP breakdown."""
    result = analytics.get_user_engagement(user_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or insufficient data for analysis",
        )
    return result
