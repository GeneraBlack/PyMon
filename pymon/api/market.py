"""ESI Market API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class MarketAPI:
    """Market-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_character_orders(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get character's active market orders."""
        return await self.client.get(
            f"/characters/{character_id}/orders/", token=token
        )

    async def get_region_orders(
        self, region_id: int, type_id: int | None = None, order_type: str = "all", page: int = 1
    ) -> list[dict[str, Any]]:
        """Get market orders in a region (auto-paginates when type_id is set)."""
        params: dict[str, Any] = {"order_type": order_type, "page": page}
        if type_id is not None:
            params["type_id"] = type_id
        first_page = await self.client.get(
            f"/markets/{region_id}/orders/", params=params
        )
        # If a specific type was requested, auto-paginate to get all orders
        if type_id is not None and isinstance(first_page, list) and len(first_page) >= 1000:
            all_orders = list(first_page)
            pg = 2
            while True:
                params["page"] = pg
                next_page = await self.client.get(
                    f"/markets/{region_id}/orders/", params=params
                )
                if not next_page:
                    break
                all_orders.extend(next_page)
                if len(next_page) < 1000:
                    break
                pg += 1
            return all_orders
        return first_page

    async def get_market_prices(self) -> list[dict[str, Any]]:
        """Get global market price averages."""
        return await self.client.get("/markets/prices/")

    async def get_market_history(
        self, region_id: int, type_id: int
    ) -> list[dict[str, Any]]:
        """Get market history for a type in a region."""
        return await self.client.get(
            f"/markets/{region_id}/history/",
            params={"type_id": type_id},
        )
