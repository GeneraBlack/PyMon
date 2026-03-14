"""ESI Opportunities API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class OpportunitiesAPI:
    """Opportunities-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_completed_tasks(
        self, character_id: int, token: str
    ) -> list[dict[str, Any]]:
        """Get completed opportunity tasks for a character."""
        return await self.client.get(
            f"/characters/{character_id}/opportunities/",
            token=token,
        )

    async def get_groups(self) -> list[int]:
        """Get all opportunity group IDs (public)."""
        return await self.client.get("/opportunities/groups/")

    async def get_group(self, group_id: int) -> dict[str, Any]:
        """Get a specific opportunity group (public)."""
        return await self.client.get(f"/opportunities/groups/{group_id}/")

    async def get_tasks(self) -> list[int]:
        """Get all opportunity task IDs (public)."""
        return await self.client.get("/opportunities/tasks/")

    async def get_task(self, task_id: int) -> dict[str, Any]:
        """Get a specific opportunity task (public)."""
        return await self.client.get(f"/opportunities/tasks/{task_id}/")
