import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow

# Allow HTTP localhost OAuth during development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

ROOT = Path(__file__).resolve().parents[2]

CLIENT_SECRETS = ROOT / "google_oauth_client.json"
TOKEN_PATH = ROOT / ".calendar_token.json"
PKCE_PATH = ROOT / ".calendar_pkce.json"

REDIRECT_URI = "http://127.0.0.1:8000/calendar/oauth2callback"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def _load_credentials() -> Optional[Credentials]:
    if not TOKEN_PATH.exists():
        return None

    data = json.loads(TOKEN_PATH.read_text())

    creds = Credentials.from_authorized_user_info(
        data,
        SCOPES,
    )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())

    return creds


def get_auth_url() -> str:
    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRETS),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    PKCE_PATH.write_text(
        json.dumps(
            {
                "state": state,
                "code_verifier": flow.code_verifier,
            }
        )
    )

    return auth_url


def save_credentials_from_authorization_response(
    authorization_response: str,
) -> Credentials:

    if not PKCE_PATH.exists():
        raise RuntimeError(
            "PKCE file missing. Click Connect Google Calendar again."
        )

    pkce = json.loads(PKCE_PATH.read_text())

    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRETS),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    flow.code_verifier = pkce["code_verifier"]

    flow.fetch_token(
        authorization_response=authorization_response
    )

    creds = flow.credentials

    TOKEN_PATH.write_text(creds.to_json())

    try:
        PKCE_PATH.unlink()
    except Exception:
        pass

    return creds


def is_connected() -> bool:
    return TOKEN_PATH.exists()


def _get_service():
    creds = _load_credentials()

    if not creds:
        raise RuntimeError("Calendar not connected")

    return build(
        "calendar",
        "v3",
        credentials=creds,
    )


def create_event(
    summary: str,
    start_dt: datetime,
    end_dt: datetime,
    timezone: str = "UTC",
) -> Dict:

    service = _get_service()

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": timezone,
        },
    }

    return (
        service.events()
        .insert(
            calendarId="primary",
            body=event,
        )
        .execute()
    )


def schedule_recommendations(
    items: List[Dict],
    start_time: Optional[datetime] = None,
) -> List[Dict]:

    if start_time is None:
        start_time = datetime.utcnow() + timedelta(hours=1)

    results = []

    cursor = start_time

    for item in items:
        title = (
            item.get("title")
            or item.get("summary")
            or "Study Session"
        )

        duration = int(
            item.get("duration_mins", 60)
        )

        end_time = cursor + timedelta(
            minutes=duration
        )

        created = create_event(
            title,
            cursor,
            end_time,
            timezone="UTC",
        )

        results.append(created)

        cursor = end_time + timedelta(
            minutes=10
        )

    return results