"""ESI Loyalty API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class LoyaltyAPI:
    """Loyalty-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_loyalty_points(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get LP balances for all corporations the character has LP with."""
        return await self.client.get(
            f"/characters/{character_id}/loyalty/points/",
            token=token,
        )

    async def get_loyalty_store_offers(
        self, corporation_id: int
    ) -> list[dict[str, Any]]:
        """Get loyalty store offers for a corporation (public, no token needed)."""
        return await self.client.get(
            f"/loyalty/stores/{corporation_id}/offers/",
        )
