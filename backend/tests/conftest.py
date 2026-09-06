from __future__ import annotations

import os


def pytest_configure() -> None:
    """Keep the default test container independent from a developer's .env.local."""
    os.environ["CFO_GOVERNANCE_DATABASE_URL"] = ""
    os.environ.pop("CFO_GOVERNANCE_DATABASE_PATH", None)
