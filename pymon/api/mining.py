"""ESI Mining API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class MiningAPI:
    """Mining-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_character_mining(
        self, character_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get character mining ledger (last 30 days)."""
        return await self.client.get(
            f"/characters/{character_id}/mining/",
            token=token,
            params={"page": page},
        )

    async def get_corporation_mining(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation mining ledger."""
        return await self.client.get(
            f"/corporation/{corporation_id}/mining/observers/",
            token=token,
            params={"page": page},
        )

    async def get_corporation_mining_observer(
        self, corporation_id: int, token: str, observer_id: int, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get details of a specific mining observer."""
        return await self.client.get(
            f"/corporation/{corporation_id}/mining/observers/{observer_id}/",
            token=token,
            params={"page": page},
        )
