"""ESI Calendar API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class CalendarAPI:
    """Calendar-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_events(
        self, character_id: int, token: str, from_event: int | None = None
    ) -> list[dict[str, Any]]:
        """Get up to 50 upcoming calendar events."""
        params: dict[str, Any] = {}
        if from_event is not None:
            params["from_event"] = from_event
        return await self.client.get(
            f"/characters/{character_id}/calendar/",
            token=token,
            params=params or None,
        )

    async def get_event(
        self, character_id: int, token: str, event_id: int
    ) -> dict[str, Any]:
        """Get details for a specific calendar event."""
        return await self.client.get(
            f"/characters/{character_id}/calendar/{event_id}/",
            token=token,
        )

    async def get_event_attendees(
        self, character_id: int, token: str, event_id: int
    ) -> list[dict[str, Any]]:
        """Get attendees for a calendar event."""
        return await self.client.get(
            f"/characters/{character_id}/calendar/{event_id}/attendees/",
            token=token,
        )
