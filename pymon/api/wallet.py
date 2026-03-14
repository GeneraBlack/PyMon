"""ESI Wallet API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class WalletAPI:
    """Wallet-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_balance(self, character_id: int, token: str) -> float:
        """Get character wallet balance."""
        return await self.client.get(
            f"/characters/{character_id}/wallet/", token=token
        )

    async def get_journal(
        self, character_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get wallet journal entries (paginated)."""
        return await self.client.get(
            f"/characters/{character_id}/wallet/journal/",
            token=token,
            params={"page": page},
        )

    async def get_transactions(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get wallet transactions."""
        return await self.client.get(
            f"/characters/{character_id}/wallet/transactions/", token=token
        )
