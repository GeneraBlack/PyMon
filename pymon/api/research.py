"""ESI Research Agents API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class ResearchAPI:
    """Agent research ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_agents_research(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get character's research agents and accumulated RP."""
        return await self.client.get(
            f"/characters/{character_id}/agents_research/",
            token=token,
        )
