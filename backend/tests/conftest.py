import os
import tempfile

# Must run before app modules are imported: keep tests away from the real
# data directory and stop startup from seeding demo content.
_tmp = tempfile.mkdtemp(prefix="jeevsetu-tests-")
os.environ["DATA_DIR"] = _tmp
os.environ["DATA_BACKEND"] = "local"
os.environ["SEED_DEMO_DATA"] = "false"
os.environ["GROQ_API_KEY"] = ""
os.environ["AUTH_SECRET"] = "test-secret"

import pytest  # noqa: E402

from app.core.security import limiter  # noqa: E402


@pytest.fixture(autouse=True)
def _no_rate_limits():
    limiter.enabled = False
    yield
    limiter.enabled = True
