"""ESI Skills API endpoints."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class SkillsAPI:
    """Skills-related ESI endpoints."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_skills(self, character_id: int, token: str) -> dict[str, Any]:
        """Get character skills.

        Returns dict with:
            - total_sp: Total skillpoints
            - unallocated_sp: Unallocated skillpoints
            - skills: List of {skill_id, active_skill_level, trained_skill_level, skillpoints_in_skill}
        """
        return await self.client.get(
            f"/characters/{character_id}/skills/", token=token
        )

    async def get_skill_queue(self, character_id: int, token: str) -> list[dict[str, Any]]:
        """Get character skill queue.

        Returns list of:
            - skill_id, finished_level, queue_position
            - start_date, finish_date
            - training_start_sp, level_start_sp, level_end_sp
        """
        return await self.client.get(
            f"/characters/{character_id}/skillqueue/", token=token
        )
