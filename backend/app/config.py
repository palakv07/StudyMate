"""Load and normalize environment variables from backend/.env"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV_PATH)


def env(key: str, default: str = "") -> str:
    """Read env var and strip surrounding quotes (common in hand-edited .env files)."""
    value = os.getenv(key, default)
    if not value:
        return default
    return value.strip().strip('"').strip("'")
