"""ESI Universe API endpoints (stations, structures, systems, types)."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class UniverseAPI:
    """Universe-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_station(self, station_id: int) -> dict[str, Any]:
        """Get NPC station info."""
        return await self.client.get(f"/universe/stations/{station_id}/")

    async def get_structure(self, structure_id: int, token: str) -> dict[str, Any]:
        """Get player structure info (requires auth)."""
        return await self.client.get(
            f"/universe/structures/{structure_id}/", token=token
        )

    async def get_system(self, system_id: int) -> dict[str, Any]:
        """Get solar system info."""
        return await self.client.get(f"/universe/systems/{system_id}/")

    async def get_type(self, type_id: int) -> dict[str, Any]:
        """Get item type info."""
        return await self.client.get(f"/universe/types/{type_id}/")

    async def get_names(self, ids: list[int]) -> list[dict[str, Any]]:
        """Resolve IDs to names (up to 1000)."""
        return await self.client.post("/universe/names/", json_data=ids)

    async def get_constellation(self, constellation_id: int) -> dict[str, Any]:
        """Get constellation info."""
        return await self.client.get(f"/universe/constellations/{constellation_id}/")

    async def get_region(self, region_id: int) -> dict[str, Any]:
        """Get region info."""
        return await self.client.get(f"/universe/regions/{region_id}/")
