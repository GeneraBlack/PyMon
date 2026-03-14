"""ESI Location API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class LocationAPI:
    """Location-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_location(self, character_id: int, token: str) -> dict[str, Any]:
        """Get current character location (solar system, station/structure)."""
        return await self.client.get(
            f"/characters/{character_id}/location/", token=token
        )

    async def get_ship(self, character_id: int, token: str) -> dict[str, Any]:
        """Get current ship type and name."""
        return await self.client.get(
            f"/characters/{character_id}/ship/", token=token
        )

    async def get_online(self, character_id: int, token: str) -> dict[str, Any]:
        """Check if character is currently online."""
        return await self.client.get(
            f"/characters/{character_id}/online/", token=token
        )
