"""ESI Industry API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class IndustryAPI:
    """Industry-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_character_jobs(
        self, character_id: int, token: str, include_completed: bool = False
    ) -> list[dict[str, Any]]:
        """Get character industry jobs."""
        params: dict[str, Any] = {}
        if include_completed:
            params["include_completed"] = "true"
        return await self.client.get(
            f"/characters/{character_id}/industry/jobs/",
            token=token,
            params=params or None,
        )

    async def get_industry_systems(self) -> list[dict[str, Any]]:
        """Get industry system cost indices."""
        return await self.client.get("/industry/systems/")
