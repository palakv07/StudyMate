"""Shared status helpers for Google Sheet rows."""

SOLVED_STATUSES = {
    "solved",
    "done",
    "complete",
    "completed",
    "yes",
    "accepted",
    "ac",
}


def is_solved(row: dict) -> bool:
    status = str(row.get("status", "")).strip().lower()
    if status in SOLVED_STATUSES:
        return True
    if not status and str(row.get("date_solved", "")).strip():
        return True
    unsolved_markers = (
        "wrong",
        "fail",
        "timeout",
        "tle",
        "mle",
        "rejected",
        "unsolved",
        "todo",
        "pending",
    )
    if status and any(x in status for x in unsolved_markers):
        return False
    return False
