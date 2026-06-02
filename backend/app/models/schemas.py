"""Pydantic models for API request/response bodies."""

from pydantic import BaseModel, Field


class SolveRequest(BaseModel):
    problem: str = Field(..., examples=["Coin Change"])
    topic: str = Field(..., examples=["DP"])
    difficulty: str = Field(..., examples=["Medium"])
    time_taken: int = Field(..., ge=1, description="Minutes spent solving")


class SolveResponse(BaseModel):
    ok: bool
    problem: str
    weakness_score: float
    message: str


class RecommendationItem(BaseModel):
    problem: str
    topic: str
    difficulty: str
    weakness_score: float
    status: str


class RecommendResponse(BaseModel):
    recommendations: list[RecommendationItem]
    ai_advice: str
    weak_topics: list[dict]


class StatsResponse(BaseModel):
    solved_count: int
    total_problems: int
    topic_distribution: dict[str, int]
    weak_topics: list[dict]
    average_solve_time: float
    sheet_name: str = ""
    sheet_url: str = ""
