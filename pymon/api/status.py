"""ESI Server Status API endpoint."""

from __future__ import annotations

from typing import Any

from pymon.api.esi_client import ESIClient


class StatusAPI:
    """Server status ESI endpoint."""

    def __init__(self, client: ESIClient) -> None:
        self.client = client

    async def get_server_status(self) -> dict[str, Any]:
        """Get Tranquility server status.

        Returns dict with:
            - players: Number of online players
            - server_version: Current server version string
            - start_time: Server start time (ISO 8601)
            - vip: Whether server is in VIP mode (optional)
        """
        return await self.client.get("/status/")
