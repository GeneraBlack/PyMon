"""ESI Bookmarks API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class BookmarksAPI:
    """Bookmarks-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_character_bookmarks(
        self, character_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get character bookmarks (paginated)."""
        return await self.client.get(
            f"/characters/{character_id}/bookmarks/",
            token=token,
            params={"page": page},
        )

    async def get_character_bookmark_folders(
        self, character_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get character bookmark folders."""
        return await self.client.get(
            f"/characters/{character_id}/bookmarks/folders/",
            token=token,
            params={"page": page},
        )

    async def get_corporation_bookmarks(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation bookmarks (paginated)."""
        return await self.client.get(
            f"/corporations/{corporation_id}/bookmarks/",
            token=token,
            params={"page": page},
        )

    async def get_corporation_bookmark_folders(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation bookmark folders."""
        return await self.client.get(
            f"/corporations/{corporation_id}/bookmarks/folders/",
            token=token,
            params={"page": page},
        )
