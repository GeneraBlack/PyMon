"""ESI Contracts API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class ContractsAPI:
    """Contracts-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_contracts(
        self, character_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get character contracts."""
        return await self.client.get(
            f"/characters/{character_id}/contracts/",
            token=token,
            params={"page": page},
        )

    async def get_contract_items(
        self, character_id: int, token: str, contract_id: int
    ) -> list[dict[str, Any]]:
        """Get items in a contract."""
        return await self.client.get(
            f"/characters/{character_id}/contracts/{contract_id}/items/",
            token=token,
        )

    async def get_contract_bids(
        self, character_id: int, token: str, contract_id: int
    ) -> list[dict[str, Any]]:
        """Get bids on an auction contract."""
        return await self.client.get(
            f"/characters/{character_id}/contracts/{contract_id}/bids/",
            token=token,
        )
