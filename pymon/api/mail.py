"""ESI Mail API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class MailAPI:
    """Mail-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_mail_headers(
        self, character_id: int, token: str, last_mail_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Get mail headers (up to 50 at a time)."""
        params: dict[str, Any] = {}
        if last_mail_id is not None:
            params["last_mail_id"] = last_mail_id
        return await self.client.get(
            f"/characters/{character_id}/mail/",
            token=token,
            params=params or None,
        )

    async def get_mail(
        self, character_id: int, token: str, mail_id: int
    ) -> dict[str, Any]:
        """Get a specific mail body."""
        return await self.client.get(
            f"/characters/{character_id}/mail/{mail_id}/", token=token
        )

    async def get_mail_labels(self, character_id: int, token: str) -> dict[str, Any]:
        """Get mail labels and unread counts."""
        return await self.client.get(
            f"/characters/{character_id}/mail/labels/", token=token
        )

    async def get_mailing_lists(self, character_id: int, token: str) -> list[dict[str, Any]]:
        """Get mailing list subscriptions."""
        return await self.client.get(
            f"/characters/{character_id}/mail/lists/", token=token
        )
