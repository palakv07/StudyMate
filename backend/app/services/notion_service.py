"""Notion visual dashboard sync (notion-client v3 / API 2025-09-03)."""

from __future__ import annotations

from datetime import date
from typing import Any

from notion_client import Client
from notion_client.errors import APIResponseError

from app.config import env


class NotionService:
    def __init__(self) -> None:
        self.api_key = env("NOTION_API_KEY")
        self.database_id = env("NOTION_DATABASE_ID").replace("-", "")
        # Optional: paste from Notion → database settings → Copy data source ID
        self.data_source_id = env("NOTION_DATA_SOURCE_ID").replace("-", "")
        self._client: Client | None = None
        self._resolved_data_source_id: str | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and (self.database_id or self.data_source_id))

    def _client_or_raise(self) -> Client:
        if not self.enabled:
            raise ValueError(
                "Notion is not configured. Set NOTION_API_KEY and NOTION_DATABASE_ID in backend/.env"
            )
        if self._client is None:
            self._client = Client(auth=self.api_key)
        return self._client

    def _get_data_source_id(self) -> str:
        """Resolve data source ID (required for notion-client v3 queries)."""
        if self._resolved_data_source_id:
            return self._resolved_data_source_id
        if self.data_source_id:
            self._resolved_data_source_id = self.data_source_id
            return self.data_source_id

        if not self.database_id:
            raise ValueError("Set NOTION_DATABASE_ID or NOTION_DATA_SOURCE_ID in backend/.env")

        client = self._client_or_raise()
        db = client.databases.retrieve(self.database_id)
        sources = db.get("data_sources") or []
        if not sources:
            raise ValueError(
                "No data sources found for this Notion database. "
                "In Notion: open database → ⋯ → Manage data sources → Copy data source ID "
                "and set NOTION_DATA_SOURCE_ID in backend/.env"
            )
        self._resolved_data_source_id = sources[0]["id"].replace("-", "")
        return self._resolved_data_source_id

    def _find_page_by_problem(self, problem: str) -> str | None:
        client = self._client_or_raise()
        data_source_id = self._get_data_source_id()
        try:
            resp = client.data_sources.query(
                data_source_id,
                filter={
                    "property": "Problem Name",
                    "title": {"equals": problem},
                },
            )
        except APIResponseError:
            resp = client.data_sources.query(data_source_id)
            for page in resp.get("results", []):
                props = page.get("properties", {})
                for val in props.values():
                    if val.get("type") == "title":
                        titles = val.get("title", [])
                        if titles and titles[0].get("plain_text", "") == problem:
                            return page["id"]
            return None
        results = resp.get("results", [])
        return results[0]["id"] if results else None

    def upsert_solved(
        self,
        problem: str,
        topic: str,
        difficulty: str,
        time_taken: int,
        status: str = "Solved",
    ) -> dict[str, Any]:
        """Create or update a Notion database entry."""
        if not self.enabled:
            return {"skipped": True, "reason": "Notion not configured"}

        client = self._client_or_raise()
        data_source_id = self._get_data_source_id()
        props = {
            "Problem Name": {"title": [{"text": {"content": problem}}]},
            "Topic": {"rich_text": [{"text": {"content": topic}}]},
            "Difficulty": {"select": {"name": difficulty}},
            "Status": {"select": {"name": status}},
            "Time Taken": {"number": time_taken},
            "Date": {"date": {"start": date.today().isoformat()}},
            "Platform": {"select": {"name": "LeetCode"}},
        }

        page_id = self._find_page_by_problem(problem)
        if page_id:
            page = client.pages.update(page_id=page_id, properties=props)
        else:
            page = client.pages.create(
                parent={"type": "data_source_id", "data_source_id": data_source_id},
                properties=props,
            )
        return {"id": page.get("id"), "url": page.get("url")}


_notion: NotionService | None = None


def get_notion_service() -> NotionService:
    global _notion
    if _notion is None:
        _notion = NotionService()
    return _notion
