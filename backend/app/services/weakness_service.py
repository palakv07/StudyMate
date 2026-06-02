"""Compute weakness scores from solve time and difficulty."""

from app.services.status_utils import is_solved

DIFFICULTY_BONUS = {"Easy": 0, "Medium": 10, "Hard": 20}


def calculate_weakness_score(time_taken: int, difficulty: str) -> float:
    """
    Higher score = more struggle. Used to prioritize review and recommendations.
    time_taken is in minutes.
    """
    diff = difficulty.strip().title()
    bonus = DIFFICULTY_BONUS.get(diff, 10)
    # 30 min baseline -> score ~30; longer times increase score (cap 100)
    base = min(70.0, (time_taken / 30.0) * 35.0)
    return round(min(100.0, base + bonus), 2)


def topic_weakness_averages(rows: list[dict]) -> dict[str, float]:
    """Average weakness_score per topic for solved rows only."""
    by_topic: dict[str, list[float]] = {}
    for row in rows:
        if not is_solved(row):
            continue
        topic = str(row.get("topic", "Unknown")).strip() or "Unknown"
        try:
            score = float(row.get("weakness_score") or 0)
        except (TypeError, ValueError):
            score = 0.0
        by_topic.setdefault(topic, []).append(score)
    return {
        t: round(sum(scores) / len(scores), 2) if scores else 0.0
        for t, scores in by_topic.items()
    }
