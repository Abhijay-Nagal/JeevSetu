import pytest
from fastapi import HTTPException

from app.core.auth import CurrentUser, require_role


async def test_require_role_allows_matching_role():
    user = CurrentUser(id="user-1", email="staff@example.com", role="staff")
    dependency = require_role("staff", "researcher")

    result = await dependency(user)

    assert result is user


async def test_require_role_rejects_other_role():
    user = CurrentUser(id="user-1", email="contributor@example.com", role="contributor")
    dependency = require_role("staff")

    with pytest.raises(HTTPException) as exc_info:
        await dependency(user)

    assert exc_info.value.status_code == 403
