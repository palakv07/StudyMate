"""POST /solve — mark a LeetCode problem as solved and sync everywhere."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import SolveRequest, SolveResponse
from app.services.coral_sync import export_sheet_to_coral
from app.services.notion_service import get_notion_service
from app.services.sheets_service import get_sheets_service
from app.services.weakness_service import calculate_weakness_score, topic_weakness_averages

router = APIRouter()


@router.post("/solve", response_model=SolveResponse)
def mark_solved(body: SolveRequest) -> SolveResponse:
    sheets = get_sheets_service()
    notion = get_notion_service()

    try:
        sheets.seed_if_empty()
        weakness = calculate_weakness_score(body.time_taken, body.difficulty)
        sheets.append_solved(
            problem=body.problem,
            topic=body.topic,
            difficulty=body.difficulty,
            time_taken=body.time_taken,
            weakness_score=weakness,
        )

        # If this topic is already weak, bump related unsolved problems
        rows = sheets.get_all_rows()
        avgs = topic_weakness_averages(rows)
        topic_avg = avgs.get(body.topic, 0)
        if topic_avg >= 40 or weakness >= 50:
            sheets.update_weakness_for_topic(body.topic, delta=5.0)

        rows = sheets.get_all_rows()
        export_sheet_to_coral(rows)

        notion_msg = "Notion skipped (not configured)"
        try:
            notion_result = notion.upsert_solved(
                problem=body.problem,
                topic=body.topic,
                difficulty=body.difficulty,
                time_taken=body.time_taken,
            )
            if notion_result.get("skipped"):
                notion_msg = "Notion skipped (not configured)"
            else:
                notion_msg = "synced to Notion"
        except Exception as notion_err:
            notion_msg = f"Notion failed: {notion_err} (fix database ID / share with integration)"

        return SolveResponse(
            ok=True,
            problem=body.problem,
            weakness_score=weakness,
            message=f"Saved to Google Sheets. {notion_msg}.",
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
