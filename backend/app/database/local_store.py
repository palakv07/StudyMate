"""Optional JSON backup when Google Sheets is temporarily unavailable."""

from __future__ import annotations

import json
from pathlib import Path

STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "backup.json"


def save_backup(rows: list[dict]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def load_backup() -> list[dict]:
    if not STORE_PATH.exists():
        return []
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))
