"""ESI Blueprints API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class BlueprintsAPI:
    """Blueprints-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_character_blueprints(
        self, character_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get character blueprints (paginated)."""
        return await self.client.get(
            f"/characters/{character_id}/blueprints/",
            token=token,
            params={"page": page},
        )

    async def get_corporation_blueprints(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation blueprints (paginated)."""
        return await self.client.get(
            f"/corporations/{corporation_id}/blueprints/",
            token=token,
            params={"page": page},
        )
