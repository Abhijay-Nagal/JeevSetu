"""In-app notifications, derived from activity that's already recorded.

There's no separate notifications table: comments and likes on your posts,
coin awards and status changes all live in their own tables already, so the
feed is assembled from those on read and can never drift out of sync.
"""

NOTIFICATION_LIMIT = 50

# Coin reasons worth a notification of their own. Post likes already appear
# as "like" notifications, and creating a post is the user's own action.
REWARD_MESSAGES = {
    "welcome_bonus": (
        "Welcome to JeevSetu!",
        "You received {amount} coins to start your collection.",
    ),
    "daily_question_correct": ("Daily question answered", "Correct answer -- +{amount} coins."),
    "streak_milestone": (
        "Streak milestone!",
        "You kept your streak alive -- +{amount} bonus coins.",
    ),
    "community_joined": ("Joined a community", "+{amount} coins for joining."),
    "community_created": ("Community created", "+{amount} coins for starting a community."),
    "card_collected": ("New card collected", "You spent {spent} coins on a collectable card."),
}

STATUS_MESSAGES = {
    "under_review": "is being reviewed by BNHS staff",
    "forwarded": "has been forwarded to a BNHS researcher",
    "responded": "has received a response from BNHS",
    "submitted": "was re-opened",
}


def notify_contributor(observation_id: str, new_status: str) -> None:
    """Status changes are recorded in status_events, which list_notifications
    reads -- nothing extra to deliver in-app. Kept as the hook for email."""


def _describe_post(post: dict) -> str:
    return f"“{post['species']}”" if post.get("species") else "your post"


def list_notifications(supabase, user_id: str) -> list[dict]:
    posts = (
        supabase.table("observations")
        .select("id, species, created_at")
        .eq("user_id", user_id)
        .execute()
        .data
    )
    posts_by_id = {post["id"]: post for post in posts}
    post_ids = list(posts_by_id)

    comments, likes, events = [], [], []
    if post_ids:
        comments = (
            supabase.table("observation_comments")
            .select("*")
            .in_("observation_id", post_ids)
            .execute()
            .data
        )
        likes = (
            supabase.table("observation_likes")
            .select("*")
            .in_("observation_id", post_ids)
            .execute()
            .data
        )
        events = (
            supabase.table("status_events")
            .select("*")
            .in_("observation_id", post_ids)
            .execute()
            .data
        )
    comments = [c for c in comments if c["user_id"] != user_id]
    likes = [like for like in likes if like["user_id"] != user_id]

    actor_ids = list({row["user_id"] for row in comments + likes})
    names = {}
    if actor_ids:
        for row in (
            supabase.table("users").select("id, name, username").in_("id", actor_ids).execute().data
        ):
            names[row["id"]] = row.get("name") or row.get("username") or "Someone"

    notifications: list[dict] = []
    for comment in comments:
        snippet = (
            comment["content"]
            if len(comment["content"]) <= 120
            else comment["content"][:117] + "..."
        )
        notifications.append(
            {
                "id": f"comment-{comment['id']}",
                "type": "comment",
                "title": f"{names.get(comment['user_id'], 'Someone')} commented",
                "message": f"On {_describe_post(posts_by_id[comment['observation_id']])}: {snippet}",
                "link": "/submissions",
                "created_at": comment["created_at"],
            }
        )
    for like in likes:
        notifications.append(
            {
                "id": f"like-{like['observation_id']}-{like['user_id']}",
                "type": "like",
                "title": f"{names.get(like['user_id'], 'Someone')} liked your post",
                "message": f"{_describe_post(posts_by_id[like['observation_id']]).capitalize()} got a like.",
                "link": "/submissions",
                "created_at": like.get("created_at")
                or posts_by_id[like["observation_id"]]["created_at"],
            }
        )
    for event in events:
        post = posts_by_id[event["observation_id"]]
        message = f"{_describe_post(post).capitalize()} {STATUS_MESSAGES.get(event['new_status'], 'was updated')}."
        if event.get("note"):
            message += f" Note: {event['note']}"
        notifications.append(
            {
                "id": f"status-{event['id']}",
                "type": "status",
                "title": "Submission update",
                "message": message,
                "link": "/submissions",
                "created_at": event["created_at"],
            }
        )

    transactions = (
        supabase.table("coin_transactions")
        .select("*")
        .eq("user_id", user_id)
        .in_("reason", list(REWARD_MESSAGES))
        .execute()
        .data
    )
    for tx in transactions:
        title, template = REWARD_MESSAGES[tx["reason"]]
        notifications.append(
            {
                "id": f"reward-{tx['id']}",
                "type": "welcome" if tx["reason"] == "welcome_bonus" else "reward",
                "title": title,
                "message": template.format(amount=tx["amount"], spent=abs(tx["amount"])),
                "link": "/cards" if tx["reason"] == "card_collected" else "/rewards",
                "created_at": tx["created_at"],
            }
        )

    notifications.sort(key=lambda item: item["created_at"], reverse=True)
    return notifications[:NOTIFICATION_LIMIT]
