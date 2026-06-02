#!/usr/bin/env python3
"""
Verify Notion connection and print database property checklist.

Usage:
  python scripts/setup_notion.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.config import env

REQUIRED_PROPS = [
    ("Problem Name", "title"),
    ("Topic", "rich_text"),
    ("Difficulty", "select"),
    ("Status", "select"),
    ("Time Taken", "number"),
    ("Date", "date"),
    ("Platform", "select"),
]


def main() -> None:
    key = env("NOTION_API_KEY")
    db_id = env("NOTION_DATABASE_ID").replace("-", "")
    ds_id = env("NOTION_DATA_SOURCE_ID").replace("-", "")

    print("AI StudyMate — Notion setup")
    if not key:
        print("ERROR: Set NOTION_API_KEY in backend/.env")
        sys.exit(1)
    if not db_id and not ds_id:
        print("ERROR: Set NOTION_DATABASE_ID or NOTION_DATA_SOURCE_ID in backend/.env")
        sys.exit(1)

    from notion_client import Client

    client = Client(auth=key)

    if ds_id:
        ds = client.data_sources.retrieve(ds_id)
        title = ""
        for t in ds.get("title", []):
            title += t.get("plain_text", "")
        print(f"Connected to data source: {title or ds_id}")
        props = ds.get("properties", {})
    else:
        db = client.databases.retrieve(db_id)
        title = ""
        for t in db.get("title", []):
            title += t.get("plain_text", "")
        print(f"Connected to database: {title or db_id}")
        sources = db.get("data_sources") or []
        if sources:
            print(f"Data source ID (auto-detected): {sources[0]['id']}")
        props = {}
        if sources:
            ds = client.data_sources.retrieve(sources[0]["id"].replace("-", ""))
            props = ds.get("properties", {})

    print("\nProperty checklist:")
    for name, expected_type in REQUIRED_PROPS:
        if name in props:
            actual = props[name].get("type", "?")
            ok = (
                "OK"
                if actual == expected_type or (name == "Problem Name" and actual == "title")
                else f"type={actual}"
            )
        else:
            ok = "MISSING — add in Notion UI"
        print(f"  [{ok}] {name} ({expected_type})")

    print("\nShare the database with your integration (⋯ → Connections).")
    print("Select options for Difficulty: Easy, Medium, Hard")
    print("Select options for Status: Solved, Unsolved, In Progress")
    print("Select options for Platform: LeetCode")


if __name__ == "__main__":
    main()
