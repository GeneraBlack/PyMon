"""ESI Faction Warfare API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class FactionWarfareAPI:
    """Faction Warfare ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_character_fw_stats(
        self, character_id: int, token: str
    ) -> dict[str, Any]:
        """Get character faction warfare stats."""
        return await self.client.get(
            f"/characters/{character_id}/fw/stats/",
            token=token,
        )

    async def get_fw_wars(self) -> list[dict[str, Any]]:
        """Get active faction warfare wars (public)."""
        return await self.client.get("/fw/wars/")

    async def get_fw_stats(self) -> list[dict[str, Any]]:
        """Get faction warfare leaderboard stats (public)."""
        return await self.client.get("/fw/stats/")

    async def get_fw_systems(self) -> list[dict[str, Any]]:
        """Get faction warfare systems and ownership (public)."""
        return await self.client.get("/fw/systems/")
