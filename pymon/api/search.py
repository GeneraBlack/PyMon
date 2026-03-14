"""ESI Search API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class SearchAPI:
    """Search ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def search(
        self,
        character_id: int,
        token: str,
        search_string: str,
        categories: list[str],
        strict: bool = False,
    ) -> dict[str, Any]:
        """Search for entities matching a string (authenticated).

        Categories can include: agent, alliance, character, constellation,
        corporation, faction, inventory_type, region, solar_system, station,
        structure.
        """
        params: dict[str, Any] = {
            "search": search_string,
            "categories": ",".join(categories),
            "strict": str(strict).lower(),
        }
        return await self.client.get(
            f"/characters/{character_id}/search/",
            token=token,
            params=params,
        )
