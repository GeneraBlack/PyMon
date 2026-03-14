"""ESI Fleet API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class FleetAPI:
    """Fleet-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_character_fleet(
        self, character_id: int, token: str
    ) -> dict[str, Any]:
        """Get the fleet the character is in, if any."""
        return await self.client.get(
            f"/characters/{character_id}/fleet/",
            token=token,
        )

    async def get_fleet(
        self, fleet_id: int, token: str
    ) -> dict[str, Any]:
        """Get fleet details."""
        return await self.client.get(
            f"/fleets/{fleet_id}/",
            token=token,
        )

    async def get_fleet_members(
        self, fleet_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get fleet members."""
        return await self.client.get(
            f"/fleets/{fleet_id}/members/",
            token=token,
        )

    async def get_fleet_wings(
        self, fleet_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get fleet wings and squads."""
        return await self.client.get(
            f"/fleets/{fleet_id}/wings/",
            token=token,
        )
