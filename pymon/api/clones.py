"""ESI Clones API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class ClonesAPI:
    """Clones-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_clones(self, character_id: int, token: str) -> dict[str, Any]:
        """Get character clones (home location + jump clones)."""
        return await self.client.get(
            f"/characters/{character_id}/clones/", token=token
        )

    async def get_implants(self, character_id: int, token: str) -> list[int]:
        """Get active implant type IDs."""
        return await self.client.get(
            f"/characters/{character_id}/implants/", token=token
        )
