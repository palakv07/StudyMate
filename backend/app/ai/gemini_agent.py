"""Gemini-powered study advice using the google-genai SDK."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from app.config import env

# gemini-2.5-flash works on the current free API tier (2026)
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
GEMINI_TIMEOUT_SECONDS = 12


def generate_study_advice(
    weak_topics: list[dict],
    recommendations: list[dict],
    stats: dict,
) -> str:
    api_key = env("GEMINI_API_KEY")
    if not api_key:
        return _fallback_advice(weak_topics, recommendations)

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_call_gemini, api_key, weak_topics, recommendations, stats)
            text = future.result(timeout=GEMINI_TIMEOUT_SECONDS)
            return text if text else _fallback_advice(weak_topics, recommendations)
    except FuturesTimeoutError:
        return _fallback_advice(weak_topics, recommendations)
    except Exception as exc:
        return _fallback_advice(weak_topics, recommendations) + f" ({_friendly_gemini_error(exc)})"


def _call_gemini(
    api_key: str,
    weak_topics: list[dict],
    recommendations: list[dict],
    stats: dict,
) -> str:
    from google import genai

    client = genai.Client(api_key=api_key)
    prompt = _build_prompt(weak_topics, recommendations, stats)
    last_error: Exception | None = None

    for model in GEMINI_MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            text = (response.text or "").strip()
            if text:
                return text
        except Exception as exc:
            last_error = exc
            if _is_quota_error(exc):
                continue
            if _is_model_not_found(exc):
                continue
            raise

    if last_error:
        raise last_error
    return ""


def _is_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "429" in msg or "quota" in msg or "resource_exhausted" in msg


def _is_model_not_found(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "404" in msg or "not found" in msg


def _friendly_gemini_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if "429" in msg or "quota" in msg:
        return "Gemini free quota reached today — using rule-based advice"
    if "api key" in msg or "401" in msg or "403" in msg:
        return "Check GEMINI_API_KEY in backend/.env"
    if "404" in msg or "not found" in msg:
        return "Gemini model unavailable — using rule-based advice"
    return "AI offline — using rule-based advice"


def _build_prompt(
    weak_topics: list[dict],
    recommendations: list[dict],
    stats: dict,
) -> str:
    weak = ", ".join(f"{w['topic']} ({w['avg_weakness']})" for w in weak_topics[:5]) or "none yet"
    recs = ", ".join(r["problem"] for r in recommendations[:5]) or "none"
    return f"""You are a friendly LeetCode coding coach for a beginner.
Given this progress data, write 2-3 short sentences of study advice.
Be specific about topics and next problems. Do not use markdown.

Weak topics (higher avg weakness = more struggle): {weak}
Suggested next problems: {recs}
Solved count: {stats.get('solved_count', 0)}
Total problems: {stats.get('total_problems', 0)}
Average solve time (minutes): {stats.get('average_solve_time', 0)}
"""


def _fallback_advice(weak_topics: list[dict], recommendations: list[dict]) -> str:
    if weak_topics:
        top = weak_topics[0]["topic"]
        msg = f"You are struggling most in {top}. Focus on medium-level {top} questions next."
    else:
        msg = "Great start! Keep solving easy problems to build consistency."
    if recommendations:
        names = ", ".join(r["problem"] for r in recommendations[:3])
        msg += f" Try these next: {names}."
    return msg
