"""ESI Jump Fatigue API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class FatigueAPI:
    """Jump fatigue ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_jump_fatigue(
        self, character_id: int, token: str
    ) -> dict[str, Any]:
        """Get character jump fatigue information."""
        return await self.client.get(
            f"/characters/{character_id}/fatigue/",
            token=token,
        )
