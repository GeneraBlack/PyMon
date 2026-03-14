"""ESI Fittings API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class FittingsAPI:
    """Fittings-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_fittings(self, character_id: int, token: str) -> list[dict[str, Any]]:
        """Get character ship fittings."""
        return await self.client.get(
            f"/characters/{character_id}/fittings/", token=token
        )
