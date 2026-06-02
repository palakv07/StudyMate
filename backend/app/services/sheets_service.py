"""Google Sheets as the primary structured database."""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path
from typing import Any

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from app.config import env

# Column order must match setup_google_sheet.py
COLUMNS = [
    "problem",
    "topic",
    "difficulty",
    "status",
    "time_taken",
    "weakness_score",
    "date_solved",
]

# Accept common header names when the sheet was edited manually
HEADER_ALIASES: dict[str, list[str]] = {
    "problem": ["problem", "problem name", "question", "title", "name", "leetcode"],
    "topic": ["topic", "category", "pattern", "tag"],
    "difficulty": ["difficulty", "level", "diff"],
    "status": ["status", "state", "progress", "acceptance"],
    "time_taken": ["time_taken", "time taken", "time", "minutes", "mins"],
    "weakness_score": ["weakness_score", "weakness score", "weakness", "priority"],
    "date_solved": ["date_solved", "date solved", "date", "solved date"],
}

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

CACHE_TTL_SECONDS = 20

# Starter problems for recommendations (unsolved until user marks them)
SEED_PROBLEMS = [
    ("Two Sum", "Arrays", "Easy", "Unsolved", 0, 25, ""),
    ("Valid Parentheses", "Stack", "Easy", "Unsolved", 0, 20, ""),
    ("Merge Intervals", "Intervals", "Medium", "Unsolved", 0, 35, ""),
    ("Coin Change", "DP", "Medium", "Unsolved", 0, 45, ""),
    ("Longest Increasing Subsequence", "DP", "Medium", "Unsolved", 0, 50, ""),
    ("Word Break", "DP", "Medium", "Unsolved", 0, 48, ""),
    ("Course Schedule", "Graph", "Medium", "Unsolved", 0, 40, ""),
    ("Number of Islands", "Graph", "Medium", "Unsolved", 0, 38, ""),
    ("Binary Tree Level Order", "Trees", "Medium", "Unsolved", 0, 32, ""),
    ("Trapping Rain Water", "Two Pointers", "Hard", "Unsolved", 0, 55, ""),
]


class SheetsService:
    def __init__(self) -> None:
        self.sheet_name = env("GOOGLE_SHEET_NAME", "AI StudyMate LeetCode Progress")
        backend_dir = Path(__file__).resolve().parents[2]
        cred_path = env("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        self.creds_file = Path(cred_path)
        if not self.creds_file.is_absolute():
            self.creds_file = backend_dir / cred_path
        self._client: gspread.Client | None = None
        self._worksheet: gspread.Worksheet | None = None
        self._cache_rows: list[dict[str, Any]] | None = None
        self._cache_time: float = 0.0

    def _ensure_client(self) -> gspread.Client:
        if self._client:
            return self._client
        creds_json = env("GOOGLE_CREDENTIALS_JSON")
        if creds_json:
           import json

           creds_dict = json.loads(creds_json)

           creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict,SCOPE,)
           self._client = gspread.authorize(creds)
           return self._client
        if not self.creds_file.exists():
            raise FileNotFoundError(
                f"Google credentials not found at {self.creds_file}"
            )
        creds = ServiceAccountCredentials.from_json_keyfile_name(
        str(self.creds_file),
        SCOPE,)
        self._client = gspread.authorize(creds)
        return self._client

    def _service_account_email(self) -> str:
        import json

        data = json.loads(self.creds_file.read_text(encoding="utf-8"))
        return str(data.get("client_email", "service-account"))

    def _open_spreadsheet(self, client: gspread.Client):
        sheet_id = env("GOOGLE_SHEET_ID").replace("-", "")
        errors: list[str] = []

        if sheet_id:
            try:
                return client.open_by_key(sheet_id)
            except gspread.SpreadsheetNotFound:
                errors.append(f"ID {sheet_id} not found or not shared with service account")

        try:
            return client.open(self.sheet_name)
        except gspread.SpreadsheetNotFound:
            errors.append(f"name '{self.sheet_name}' not found or not shared")

        email = self._service_account_email()
        hint = (
            f"Cannot open Google Sheet. Share the spreadsheet with {email} as Editor. "
            f"Tried: {'; '.join(errors)}"
        )
        raise FileNotFoundError(hint)

    def get_spreadsheet_url(self) -> str:
        client = self._ensure_client()
        return self._open_spreadsheet(client).url

    def _get_worksheet(self) -> gspread.Worksheet:
        if self._worksheet:
            return self._worksheet
        client = self._ensure_client()
        spreadsheet = self._open_spreadsheet(client)
        self._worksheet = spreadsheet.sheet1
        return self._worksheet

    def ensure_header(self) -> None:
        ws = self._get_worksheet()
        first_row = ws.row_values(1)
        normalized = [c.strip().lower() for c in first_row if c and c.strip()]
        has_dupes = len(normalized) != len(set(normalized))
        first_cell = first_row[0].strip().lower() if first_row else ""
        valid_start = first_cell in HEADER_ALIASES["problem"]
        if (not first_row or not valid_start or has_dupes) and not has_dupes:
            if not first_row or not valid_start:
                ws.update("A1:G1", [COLUMNS], value_input_option="USER_ENTERED")
        elif has_dupes:
            # Only trim broken extra columns — keep row 1 labels if column A is valid
            ws.batch_clear(["H1:Z1"])

    def _invalidate_cache(self) -> None:
        self._cache_rows = None
        self._cache_time = 0.0

    def _column_map(self, header_row: list[str]) -> dict[str, int]:
        """Map standard column names to sheet column indices."""
        col_map: dict[str, int] = {}
        for i, raw in enumerate(header_row):
            h = raw.strip().lower()
            if not h:
                continue
            for key, aliases in HEADER_ALIASES.items():
                if h in aliases and key not in col_map:
                    col_map[key] = i
        for idx, key in enumerate(COLUMNS):
            col_map.setdefault(key, idx)
        return col_map

    def _parse_raw_values(self, values: list[list[Any]]) -> list[dict[str, Any]]:
        if len(values) < 2:
            return []
        col_map = self._column_map([str(c) for c in values[0]])
        rows: list[dict[str, Any]] = []
        for raw in values[1:]:
            if not any(str(c).strip() for c in raw):
                continue
            row: dict[str, Any] = {}
            for key in COLUMNS:
                idx = col_map.get(key, COLUMNS.index(key))
                row[key] = raw[idx] if idx < len(raw) else ""
            if not str(row.get("problem", "")).strip():
                continue
            rows.append(self._normalize_row(row))
        return rows

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return {key: row.get(key, "") for key in COLUMNS}

    def _fetch_all_rows(self) -> list[dict[str, Any]]:
        ws = self._get_worksheet()
        # Always parse by header names — handles LeetCode exports & extra columns
        values = ws.get_all_values()
        return self._parse_raw_values(values)

    def seed_if_empty(self) -> None:
        self.ensure_header()
        ws = self._get_worksheet()
        if len(ws.get_all_values()) <= 1:
            rows = [list(p) for p in SEED_PROBLEMS]
            ws.append_rows(rows, value_input_option="USER_ENTERED")

    def get_all_rows(self) -> list[dict[str, Any]]:
        self.ensure_header()
        now = time.time()
        if self._cache_rows is not None and now - self._cache_time < CACHE_TTL_SECONDS:
            return self._cache_rows
        rows = self._fetch_all_rows()
        self._cache_rows = rows
        self._cache_time = now
        return rows

    def find_row_index(self, problem: str) -> int | None:
        """1-based sheet row index (including header). None if not found."""
        ws = self._get_worksheet()
        problems = ws.col_values(1)
        target = problem.strip().lower()
        for i, name in enumerate(problems, start=1):
            if i == 1:
                continue
            if name.strip().lower() == target:
                return i
        return None

    def append_solved(
        self,
        problem: str,
        topic: str,
        difficulty: str,
        time_taken: int,
        weakness_score: float,
    ) -> None:
        self.ensure_header()
        ws = self._get_worksheet()
        row_idx = self.find_row_index(problem)
        today = date.today().isoformat()
        values = [
            problem,
            topic,
            difficulty,
            "Solved",
            time_taken,
            weakness_score,
            today,
        ]
        if row_idx:
            ws.update(f"A{row_idx}:G{row_idx}", [values])
        else:
            ws.append_row(values, value_input_option="USER_ENTERED")
        self._invalidate_cache()

    def update_weakness_for_topic(self, topic: str, delta: float) -> None:
        """Bump weakness on unsolved problems in a weak topic."""
        ws = self._get_worksheet()
        records = self.get_all_rows()
        for i, row in enumerate(records, start=2):
            if (
                str(row.get("topic", "")).strip().lower() == topic.strip().lower()
                and not is_solved(row)
            ):
                try:
                    current = float(row.get("weakness_score") or 0)
                except (TypeError, ValueError):
                    current = 0.0
                new_score = min(100.0, round(current + delta, 2))
                ws.update_cell(i, 6, new_score)
        self._invalidate_cache()


_sheets: SheetsService | None = None


def get_sheets_service() -> SheetsService:
    global _sheets
    if _sheets is None:
        _sheets = SheetsService()
    return _sheets
