"""Manual smoke test against a running local backend + the real Supabase project.

Usage:
    cd backend
    cp .env.example .env   # fill in real Supabase keys first
    uvicorn app.main:app --reload &
    python scripts/smoke_test.py
"""

import sys
import uuid
from pathlib import Path

import httpx
from supabase import create_client

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings  # noqa: E402

BASE_URL = "http://localhost:8000"


def main() -> None:
    settings = get_settings()
    admin = create_client(settings.supabase_url, settings.supabase_service_role_key)

    email = f"smoke-test-{uuid.uuid4().hex[:8]}@example.com"
    password = uuid.uuid4().hex

    created = admin.auth.admin.create_user(
        {"email": email, "password": password, "email_confirm": True}
    )
    user_id = created.user.id
    print(f"created test user {email} ({user_id})")

    try:
        session = admin.auth.sign_in_with_password({"email": email, "password": password})
        token = session.session.access_token
        headers = {"Authorization": f"Bearer {token}"}

        response = httpx.post(
            f"{BASE_URL}/observations",
            json={"species": "Cheetah", "description": "smoke test"},
            headers=headers,
        )
        assert response.status_code == 201, response.text
        observation_id = response.json()["id"]
        print("POST /observations -> 201 OK")

        response = httpx.get(f"{BASE_URL}/observations/mine", headers=headers)
        assert response.status_code == 200, response.text
        assert any(row["id"] == observation_id for row in response.json())
        print("GET /observations/mine -> 200 OK")

        response = httpx.get(f"{BASE_URL}/observations", headers=headers)
        assert response.status_code == 403, response.text
        print("GET /observations as contributor -> 403 OK")

        admin.table("users").update({"role": "staff"}).eq("id", user_id).execute()

        response = httpx.get(f"{BASE_URL}/observations", headers=headers)
        assert response.status_code == 200, response.text
        print("GET /observations as staff -> 200 OK")

        response = httpx.patch(
            f"{BASE_URL}/observations/{observation_id}",
            json={"status": "under_review", "note": "smoke test"},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "under_review"
        print("PATCH /observations/{id} -> 200 OK")

        print("\nAll smoke tests passed.")
    finally:
        admin.auth.admin.delete_user(user_id)
        print(f"cleaned up test user {user_id}")


if __name__ == "__main__":
    main()
