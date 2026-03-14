"""ESI Assets API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class AssetsAPI:
    """Assets-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_assets(self, character_id: int, token: str, page: int = 1) -> list[dict[str, Any]]:
        """Get character assets (paginated, 1000 items per page)."""
        return await self.client.get(
            f"/characters/{character_id}/assets/",
            token=token,
            params={"page": page},
        )

    async def get_asset_names(
        self, character_id: int, token: str, item_ids: list[int]
    ) -> list[dict[str, Any]]:
        """Get names for specific asset items."""
        return await self.client.post(
            f"/characters/{character_id}/assets/names/",
            token=token,
            json_data=item_ids,
        )

    async def get_asset_locations(
        self, character_id: int, token: str, item_ids: list[int]
    ) -> list[dict[str, Any]]:
        """Get locations for specific asset items."""
        return await self.client.post(
            f"/characters/{character_id}/assets/locations/",
            token=token,
            json_data=item_ids,
        )
