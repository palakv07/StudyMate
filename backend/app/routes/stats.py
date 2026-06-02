"""GET /stats — progress summary."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import StatsResponse
from app.services.recommendation_service import compute_stats
from app.services.sheets_service import get_sheets_service
from app.services.status_utils import is_solved

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    try:
        sheets = get_sheets_service()
        sheets.seed_if_empty()
        rows = sheets.get_all_rows()
        data = compute_stats(rows)
        try:
            data["sheet_name"] = sheets.sheet_name
            data["sheet_url"] = sheets.get_spreadsheet_url()
        except Exception:
            data["sheet_name"] = sheets.sheet_name
            data["sheet_url"] = ""
        return StatsResponse(**data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sheet-info")
def sheet_info():
    """Which Google Sheet the app is reading (for debugging)."""
    sheets = get_sheets_service()
    rows = sheets.get_all_rows()
    solved = sum(1 for r in rows if is_solved(r))
    return {
        "sheet_name": sheets.sheet_name,
        "sheet_url": sheets.get_spreadsheet_url(),
        "total_problems": len(rows),
        "solved_count": solved,
    }


@router.get("/problems")
def list_problems():
    """All rows from Google Sheets (for dashboard)."""
    sheets = get_sheets_service()
    sheets.seed_if_empty()
    return {"problems": sheets.get_all_rows()}
