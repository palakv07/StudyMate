#!/usr/bin/env python3
"""
Create / verify Google Sheet with required columns.
Run once after placing credentials.json in backend/

Usage (from project root):
  python scripts/setup_google_sheet.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.services.sheets_service import COLUMNS, get_sheets_service  # noqa: E402
from app.services.status_utils import is_solved  # noqa: E402


def main() -> None:
    print("AI StudyMate — Google Sheets setup")
    print("Expected columns:", ", ".join(COLUMNS))
    try:
        sheets = get_sheets_service()
        sheets.ensure_header()
        sheets.seed_if_empty()
        rows = sheets.get_all_rows()
        solved = sum(1 for r in rows if is_solved(r))
        url = sheets.get_spreadsheet_url()
        print(f"OK: Sheet '{sheets.sheet_name}' — {len(rows)} rows, {solved} solved")
        print(f"URL: {url}")
        print("\nIMPORTANT: Edit THIS Google Sheet in your browser.")
        print("Microsoft Excel (.xlsx) is NOT connected — only Google Sheets.")
        print("\nStatus column: use 'Accepted' or 'Solved' for completed problems.")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
