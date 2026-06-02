"""
AI StudyMate — FastAPI backend entry point.
Run with: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
"""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import recommend, solve, stats, calendar

# Load backend/.env before services read environment variables
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed sheet + export Coral CSV on startup when credentials exist."""
    try:
        from app.services.coral_sync import export_sheet_to_coral
        from app.services.sheets_service import get_sheets_service

        sheets = get_sheets_service()
        sheets.seed_if_empty()
        export_sheet_to_coral(sheets.get_all_rows())
    except Exception:
        # Credentials may not be configured yet — app still starts for health checks
        pass
    yield


app = FastAPI(
    title="AI StudyMate API",
    description="Track LeetCode progress, sync Sheets/Notion, get AI recommendations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://studymate1-wres.onrender.com",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(solve.router, tags=["solve"])
app.include_router(recommend.router, tags=["recommend"])
app.include_router(stats.router, tags=["stats"])
app.include_router(calendar.router, tags=["calendar"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "AI StudyMate", "version": "1.1.0"}
