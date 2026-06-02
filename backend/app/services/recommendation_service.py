"""Rule-based recommendations from sheet data (Coral SQL examples in README)."""

from __future__ import annotations

from typing import Any

from app.services.status_utils import is_solved
from app.services.weakness_service import topic_weakness_averages


def _is_solved(row: dict) -> bool:
    return is_solved(row)


def get_recommendations(rows: list[dict], limit: int = 5) -> tuple[list[dict], list[dict]]:
    """
    Return top unsolved problems by weakness_score and list of weak topics.
    Mirrors Coral SQL:
      SELECT problem, difficulty FROM sheets.leetcode_progress
      WHERE status != 'Solved' ORDER BY weakness_score DESC LIMIT 5;
    """
    topic_avgs = topic_weakness_averages(rows)
    weak_topics = sorted(
        [{"topic": t, "avg_weakness": s} for t, s in topic_avgs.items()],
        key=lambda x: x["avg_weakness"],
        reverse=True,
    )[:5]

    unsolved = [r for r in rows if not _is_solved(r)]
    # Boost unsolved in weak topics
    weak_set = {w["topic"].lower() for w in weak_topics[:3]}
    def sort_key(r: dict) -> float:
        try:
            score = float(r.get("weakness_score") or 0)
        except (TypeError, ValueError):
            score = 0.0
        topic = str(r.get("topic", "")).lower()
        if topic in weak_set:
            score += 15.0
        return score

    unsolved.sort(key=sort_key, reverse=True)
    recs: list[dict[str, Any]] = []
    for r in unsolved[:limit]:
        recs.append(
            {
                "problem": r.get("problem", ""),
                "topic": r.get("topic", ""),
                "difficulty": r.get("difficulty", ""),
                "weakness_score": float(r.get("weakness_score") or 0),
                "status": r.get("status", "Unsolved"),
            }
        )
    return recs, weak_topics


def compute_stats(rows: list[dict]) -> dict:
    solved = [r for r in rows if _is_solved(r)]
    topic_dist: dict[str, int] = {}
    times: list[float] = []
    for r in solved:
        t = str(r.get("topic", "Unknown"))
        topic_dist[t] = topic_dist.get(t, 0) + 1
        try:
            times.append(float(r.get("time_taken") or 0))
        except (TypeError, ValueError):
            pass
    topic_avgs = topic_weakness_averages(rows)
    weak_topics = sorted(
        [{"topic": t, "avg_weakness": s} for t, s in topic_avgs.items()],
        key=lambda x: x["avg_weakness"],
        reverse=True,
    )[:5]
    avg_time = round(sum(times) / len(times), 1) if times else 0.0
    return {
        "solved_count": len(solved),
        "total_problems": len(rows),
        "topic_distribution": topic_dist,
        "weak_topics": weak_topics,
        "average_solve_time": avg_time,
    }
