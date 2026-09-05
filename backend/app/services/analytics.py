"""Predictive engagement analytics — XGBoost churn model with SHAP explainability.

Pulls behavioural features from existing Supabase tables (no new data collection),
trains a lightweight XGBoost classifier to flag at-risk users, and uses SHAP
TreeExplainer to provide human-readable reasons behind each prediction.

The model is retrained on every call (dataset is small — all users in a single
Supabase project). No persistent model file is needed.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.model_selection import cross_val_score

from app.core.supabase_client import get_supabase

logger = logging.getLogger(__name__)

# A user with no activity for this many days is labelled as "churned".
CHURN_THRESHOLD_DAYS = 7

FEATURE_COLUMNS = [
    "total_posts",
    "total_likes_received",
    "total_likes_given",
    "total_coins",
    "coin_velocity_7d",
    "current_streak",
    "longest_streak",
    "freezes_used",
    "communities_joined",
    "communities_created",
    "daily_questions_answered",
    "daily_questions_correct",
    "days_since_last_activity",
    "account_age_days",
]


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def _fetch_user_features() -> pd.DataFrame:
    """Pull per-user behavioural features from existing Supabase tables."""
    supabase = get_supabase()
    now = datetime.now(timezone.utc)

    # ------ raw pulls ------
    users = supabase.table("users").select("id, created_at").execute().data or []
    observations = supabase.table("observations").select("id, user_id, created_at").execute().data or []
    likes = supabase.table("observation_likes").select("user_id, observation_id").execute().data or []
    coin_txns = supabase.table("coin_transactions").select("user_id, amount, created_at").execute().data or []
    streaks = supabase.table("user_streaks").select("user_id, current_streak, longest_streak, freezes_used_total, last_answered_date").execute().data or []
    members = supabase.table("community_members").select("user_id, role").execute().data or []
    dq_attempts = supabase.table("daily_question_attempts").select("user_id, is_correct, answered_at").execute().data or []

    if not users:
        return pd.DataFrame(columns=["user_id"] + FEATURE_COLUMNS)

    # ------ index by user ------
    user_ids = [u["id"] for u in users]
    created_map = {u["id"]: u["created_at"] for u in users}

    # Posts per user
    posts_count: dict[str, int] = {}
    post_owner: dict[str, str] = {}
    latest_activity: dict[str, datetime] = {}
    for obs in observations:
        uid = obs["user_id"]
        posts_count[uid] = posts_count.get(uid, 0) + 1
        post_owner[obs["id"]] = uid
        ts = _parse_ts(obs["created_at"])
        if ts and (uid not in latest_activity or ts > latest_activity[uid]):
            latest_activity[uid] = ts

    # Likes given / received
    likes_given: dict[str, int] = {}
    likes_received: dict[str, int] = {}
    for like in likes:
        liker = like["user_id"]
        likes_given[liker] = likes_given.get(liker, 0) + 1
        author = post_owner.get(like["observation_id"])
        if author:
            likes_received[author] = likes_received.get(author, 0) + 1

    # Coins total + 7-day velocity
    total_coins: dict[str, int] = {}
    coin_vel: dict[str, int] = {}
    for txn in coin_txns:
        uid = txn["user_id"]
        total_coins[uid] = total_coins.get(uid, 0) + txn["amount"]
        ts = _parse_ts(txn["created_at"])
        if ts and (now - ts).days <= 7:
            coin_vel[uid] = coin_vel.get(uid, 0) + txn["amount"]
        if ts and (uid not in latest_activity or ts > latest_activity[uid]):
            latest_activity[uid] = ts

    # Streaks
    streak_map = {s["user_id"]: s for s in streaks}

    # Communities
    comm_joined: dict[str, int] = {}
    comm_created: dict[str, int] = {}
    for m in members:
        uid = m["user_id"]
        comm_joined[uid] = comm_joined.get(uid, 0) + 1
        if m["role"] == "creator":
            comm_created[uid] = comm_created.get(uid, 0) + 1

    # Daily questions
    dq_answered: dict[str, int] = {}
    dq_correct: dict[str, int] = {}
    for attempt in dq_attempts:
        uid = attempt["user_id"]
        dq_answered[uid] = dq_answered.get(uid, 0) + 1
        if attempt["is_correct"]:
            dq_correct[uid] = dq_correct.get(uid, 0) + 1
        ts = _parse_ts(attempt.get("answered_at"))
        if ts and (uid not in latest_activity or ts > latest_activity[uid]):
            latest_activity[uid] = ts

    # ------ assemble dataframe ------
    rows = []
    for uid in user_ids:
        created_ts = _parse_ts(created_map.get(uid))
        account_age = (now - created_ts).days if created_ts else 0
        last_act = latest_activity.get(uid)
        days_since = (now - last_act).days if last_act else account_age

        s = streak_map.get(uid, {})
        rows.append({
            "user_id": uid,
            "total_posts": posts_count.get(uid, 0),
            "total_likes_received": likes_received.get(uid, 0),
            "total_likes_given": likes_given.get(uid, 0),
            "total_coins": total_coins.get(uid, 0),
            "coin_velocity_7d": coin_vel.get(uid, 0),
            "current_streak": s.get("current_streak", 0),
            "longest_streak": s.get("longest_streak", 0),
            "freezes_used": s.get("freezes_used_total", 0),
            "communities_joined": comm_joined.get(uid, 0),
            "communities_created": comm_created.get(uid, 0),
            "daily_questions_answered": dq_answered.get(uid, 0),
            "daily_questions_correct": dq_correct.get(uid, 0),
            "days_since_last_activity": days_since,
            "account_age_days": account_age,
        })

    return pd.DataFrame(rows)


def _parse_ts(value) -> datetime | None:
    """Flexibly parse a timestamp string from Supabase."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    try:
        # Supabase typically returns ISO 8601
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Model training + SHAP
# ---------------------------------------------------------------------------

def _train_and_explain(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, dict]:
    """Train XGBoost, compute SHAP values, return (risk_scores, shap_values, cv_metrics)."""
    X = df[FEATURE_COLUMNS].values.astype(float)
    y = (df["days_since_last_activity"] >= CHURN_THRESHOLD_DAYS).astype(int).values

    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )

    # Cross-validation metrics (only if enough samples)
    cv_metrics: dict = {}
    if len(y) >= 10 and len(np.unique(y)) > 1:
        try:
            scores = cross_val_score(model, X, y, cv=min(10, len(y)), scoring="f1")
            cv_metrics = {
                "cv_f1_mean": round(float(np.mean(scores)), 4),
                "cv_f1_std": round(float(np.std(scores)), 4),
                "cv_folds": len(scores),
            }
        except Exception as e:
            logger.warning("CV failed (non-critical): %s", e)

    # Fit on full dataset
    model.fit(X, y)

    # Risk scores (probability of churn)
    risk_scores = model.predict_proba(X)[:, 1]

    # SHAP explanations
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    return risk_scores, shap_values, cv_metrics


def _risk_label(score: float) -> str:
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    return "low"


def _top_shap_features(shap_row: np.ndarray, feature_values: np.ndarray, top_n: int = 3) -> list[dict]:
    """Return the top-N SHAP contributors for a single user."""
    abs_shap = np.abs(shap_row)
    top_indices = abs_shap.argsort()[-top_n:][::-1]
    return [
        {
            "feature_name": FEATURE_COLUMNS[i],
            "shap_value": round(float(shap_row[i]), 4),
            "feature_value": round(float(feature_values[i]), 2),
        }
        for i in top_indices
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_engagement_dashboard() -> dict:
    """Full dashboard: all users with risk scores, SHAP explanations, and KPIs."""
    df = _fetch_user_features()

    if df.empty:
        return {
            "total_users": 0,
            "at_risk_count": 0,
            "avg_risk_score": 0.0,
            "cv_metrics": {},
            "users": [],
        }

    # Need at least 2 users with different labels to train
    churn_labels = (df["days_since_last_activity"] >= CHURN_THRESHOLD_DAYS).astype(int)
    if len(df) < 2 or churn_labels.nunique() < 2:
        # Not enough data to train — return raw features with no ML
        users = []
        for _, row in df.iterrows():
            users.append({
                "user_id": row["user_id"],
                "features": {col: round(float(row[col]), 2) for col in FEATURE_COLUMNS},
                "risk_score": 0.5,
                "risk_label": "unknown",
                "shap_explanations": [],
            })
        return {
            "total_users": len(df),
            "at_risk_count": 0,
            "avg_risk_score": 0.5,
            "cv_metrics": {"note": "Insufficient data for model training"},
            "users": users,
        }

    risk_scores, shap_values, cv_metrics = _train_and_explain(df)
    X = df[FEATURE_COLUMNS].values.astype(float)

    users = []
    at_risk = 0
    for i, (_, row) in enumerate(df.iterrows()):
        score = float(risk_scores[i])
        label = _risk_label(score)
        if label in ("high", "medium"):
            at_risk += 1
        users.append({
            "user_id": row["user_id"],
            "features": {col: round(float(row[col]), 2) for col in FEATURE_COLUMNS},
            "risk_score": round(score, 4),
            "risk_label": label,
            "shap_explanations": _top_shap_features(shap_values[i], X[i]),
        })

    # Sort by risk score descending (most at-risk first)
    users.sort(key=lambda u: u["risk_score"], reverse=True)

    return {
        "total_users": len(df),
        "at_risk_count": at_risk,
        "avg_risk_score": round(float(np.mean(risk_scores)), 4),
        "cv_metrics": cv_metrics,
        "users": users,
    }


def get_user_engagement(user_id: str) -> dict | None:
    """Single-user risk profile with full SHAP breakdown."""
    dashboard = get_engagement_dashboard()
    for user in dashboard["users"]:
        if user["user_id"] == user_id:
            return {
                **user,
                "cv_metrics": dashboard["cv_metrics"],
            }
    return None
