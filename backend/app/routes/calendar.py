from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.services.calendar_service import (
    get_auth_url,
    is_connected,
    save_credentials_from_authorization_response,
    schedule_recommendations,
)

router = APIRouter()


@router.get("/calendar/status")
def calendar_status():
    return {"connected": is_connected()}


@router.get("/calendar/auth_url")
def calendar_auth_url():
    try:
        url = get_auth_url()
        return {"url": url}
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/calendar/oauth2callback", response_class=HTMLResponse)
def oauth2callback(request: Request):
    # Google redirects here with code and state. Persist credentials.
    try:
        full = str(request.url)
        save_credentials_from_authorization_response(full)
        return HTMLResponse("<html><body><h3>Calendar connected. You can close this tab.</h3></body></html>")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/calendar/schedule")
def calendar_schedule(payload: dict = None):
    """Schedule study sessions.

    Payload (optional): {items: [{title, duration_mins}], start_time: ISO8601 str}
    If no payload provided, return 400.
    """
    try:
        data = payload or {}
        items = data.get("items") if isinstance(data, dict) else None
        if not items:
            raise HTTPException(status_code=400, detail="No items to schedule")
        results = schedule_recommendations(items)
        return JSONResponse({"scheduled": [r.get("id") for r in results]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
