"""ESI Contacts API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class ContactsAPI:
    """Contacts-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_contacts(
        self, character_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get character contacts (paginated)."""
        return await self.client.get(
            f"/characters/{character_id}/contacts/",
            token=token,
            params={"page": page},
        )

    async def get_contact_labels(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get contact labels."""
        return await self.client.get(
            f"/characters/{character_id}/contacts/labels/",
            token=token,
        )

    async def get_standings(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get character standings towards factions, corps, agents."""
        return await self.client.get(
            f"/characters/{character_id}/standings/",
            token=token,
        )

    async def get_corporation_contacts(
        self, corporation_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get corporation contacts (paginated)."""
        return await self.client.get(
            f"/corporations/{corporation_id}/contacts/",
            token=token,
            params={"page": page},
        )

    async def get_alliance_contacts(
        self, alliance_id: int, token: str, page: int = 1
    ) -> list[dict[str, Any]]:
        """Get alliance contacts (paginated)."""
        return await self.client.get(
            f"/alliances/{alliance_id}/contacts/",
            token=token,
            params={"page": page},
        )
