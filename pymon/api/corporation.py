"""ESI Corporation API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class CorporationAPI:
    """Corporation-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_corporation(self, corporation_id: int) -> dict[str, Any]:
        """Get corporation public info (no token needed)."""
        return await self.client.get(
            f"/corporations/{corporation_id}/",
        )

    async def get_members(
        self, corporation_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get corporation member list (director+ role)."""
        return await self.client.get(
            f"/corporations/{corporation_id}/members/",
            token=token,
        )

    async def get_member_tracking(
        self, corporation_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get member tracking data (director+ role)."""
        return await self.client.get(
            f"/corporations/{corporation_id}/membertracking/",
            token=token,
        )

    async def get_divisions(
        self, corporation_id: int, token: str
    ) -> dict[str, Any]:
        """Get corporation divisions (hangar & wallet names)."""
        return await self.client.get(
            f"/corporations/{corporation_id}/divisions/",
            token=token,
        )

    async def get_titles(
        self, corporation_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get corporation titles."""
        return await self.client.get(
            f"/corporations/{corporation_id}/titles/",
            token=token,
        )

    async def get_starbases(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation starbases (POS)."""
        return await self.client.get(
            f"/corporations/{corporation_id}/starbases/",
            token=token,
            params={"page": page},
        )

    async def get_structures(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation structures."""
        return await self.client.get(
            f"/corporations/{corporation_id}/structures/",
            token=token,
            params={"page": page},
        )

    async def get_facilities(
        self, corporation_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get corporation industry facilities."""
        return await self.client.get(
            f"/corporations/{corporation_id}/facilities/",
            token=token,
        )

    async def get_medals(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation medals."""
        return await self.client.get(
            f"/corporations/{corporation_id}/medals/",
            token=token,
            params={"page": page},
        )

    async def get_container_logs(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation container audit logs."""
        return await self.client.get(
            f"/corporations/{corporation_id}/containers/logs/",
            token=token,
            params={"page": page},
        )

    async def get_fw_stats(
        self, corporation_id: int, token: str
    ) -> dict[str, Any]:
        """Get corporation faction warfare stats."""
        return await self.client.get(
            f"/corporations/{corporation_id}/fw/stats/",
            token=token,
        )
