"""ESI Notifications API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class NotificationsAPI:
    """Notifications-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_notifications(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get character notifications (up to 500, cached 10 min)."""
        return await self.client.get(
            f"/characters/{character_id}/notifications/",
            token=token,
        )

    async def get_contact_notifications(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get contact notifications."""
        return await self.client.get(
            f"/characters/{character_id}/notifications/contacts/",
            token=token,
        )
