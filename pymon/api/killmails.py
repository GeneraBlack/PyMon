"""ESI Killmails API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class KillmailsAPI:
    """Killmails-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_character_killmails(
        self, character_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get character killmail hashes."""
        return await self.client.get(
            f"/characters/{character_id}/killmails/recent/",
            token=token,
            params={"page": page},
        )

    async def get_killmail(self, killmail_id: int, killmail_hash: str) -> dict[str, Any]:
        """Get full killmail details."""
        return await self.client.get(
            f"/killmails/{killmail_id}/{killmail_hash}/",
        )
