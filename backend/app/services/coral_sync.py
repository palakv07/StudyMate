"""Export Google Sheets data to a local CSV for Coral file source (sheets.leetcode_progress)."""

from __future__ import annotations

import csv
from pathlib import Path

CORAL_DATA_DIR = Path(__file__).resolve().parents[2] / "coral" / "data"
CSV_PATH = CORAL_DATA_DIR / "leetcode_progress.csv"

TABLE_NAME = "leetcode_progress"


def export_sheet_to_coral(rows: list[dict]) -> Path:
    """Write sheet rows to CSV so Coral can query sheets.leetcode_progress."""
    CORAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "problem",
        "topic",
        "difficulty",
        "status",
        "time_taken",
        "weakness_score",
        "date_solved",
    ]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    return CSV_PATH


def get_coral_csv_path() -> Path:
    return CSV_PATH
