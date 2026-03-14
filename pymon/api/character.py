"""ESI Character API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class CharacterAPI:
    """Character-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_character(self, character_id: int) -> dict[str, Any]:
        """Get public character info."""
        return await self.client.get(f"/characters/{character_id}/")

    async def get_portrait(self, character_id: int) -> dict[str, Any]:
        """Get character portrait URLs."""
        return await self.client.get(f"/characters/{character_id}/portrait/")

    async def get_corporation(self, corporation_id: int) -> dict[str, Any]:
        """Get corporation info."""
        return await self.client.get(f"/corporations/{corporation_id}/")

    async def get_alliance(self, alliance_id: int) -> dict[str, Any]:
        """Get alliance info."""
        return await self.client.get(f"/alliances/{alliance_id}/")

    async def get_attributes(self, character_id: int, token: str) -> dict[str, Any]:
        """Get character attributes (intelligence, memory, etc.)."""
        return await self.client.get(
            f"/characters/{character_id}/attributes/", token=token
        )

    async def get_online(self, character_id: int, token: str) -> dict[str, Any]:
        """Check if character is online."""
        return await self.client.get(
            f"/characters/{character_id}/online/", token=token
        )

    async def get_corporation_history(self, character_id: int) -> list[dict[str, Any]]:
        """Get character employment history (public, no auth needed)."""
        return await self.client.get(f"/characters/{character_id}/corporationhistory/")

    async def get_medals(self, character_id: int, token: str) -> list[dict[str, Any]]:
        """Get character medals."""
        return await self.client.get(
            f"/characters/{character_id}/medals/", token=token
        )

    async def get_titles(self, character_id: int, token: str) -> list[dict[str, Any]]:
        """Get character corporation titles."""
        return await self.client.get(
            f"/characters/{character_id}/titles/", token=token
        )
