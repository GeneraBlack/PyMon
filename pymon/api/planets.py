"""ESI Planetary Interaction (PI) API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class PlanetsAPI:
    """Planetary Interaction (PI) ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_colonies(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get list of character's planetary colonies."""
        return await self.client.get(
            f"/characters/{character_id}/planets/",
            token=token,
        )

    async def get_colony_layout(
        self, character_id: int, token: str, planet_id: int
    ) -> dict[str, Any]:
        """Get detailed layout of a specific colony."""
        return await self.client.get(
            f"/characters/{character_id}/planets/{planet_id}/",
            token=token,
        )

    async def get_customs_offices(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation customs offices."""
        return await self.client.get(
            f"/corporations/{corporation_id}/customs_offices/",
            token=token,
            params={"page": page},
        )

    async def get_schematic(self, schematic_id: int) -> dict[str, Any]:
        """Get schematic information (public, no token needed)."""
        return await self.client.get(
            f"/universe/schematics/{schematic_id}/",
        )
