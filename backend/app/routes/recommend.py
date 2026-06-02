"""GET /recommend — top 5 next problems + Gemini advice."""

from fastapi import APIRouter, HTTPException

from app.ai.gemini_agent import generate_study_advice
from app.models.schemas import RecommendResponse, RecommendationItem
from app.services.recommendation_service import compute_stats, get_recommendations
from app.services.sheets_service import get_sheets_service

router = APIRouter()


@router.get("/recommend", response_model=RecommendResponse)
def recommend() -> RecommendResponse:
    try:
        sheets = get_sheets_service()
        sheets.seed_if_empty()
        rows = sheets.get_all_rows()
        recs, weak_topics = get_recommendations(rows, limit=5)
        stats = compute_stats(rows)
        advice = generate_study_advice(weak_topics, recs, stats)
        items = [RecommendationItem(**r) for r in recs]
        return RecommendResponse(
            recommendations=items,
            ai_advice=advice,
            weak_topics=weak_topics,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
