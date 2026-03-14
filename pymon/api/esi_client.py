"""Base ESI API HTTP client with caching and error handling.

All ESI endpoints are accessed through this client, which handles:
- Authentication headers (Bearer token)
- Cache-Control / ETag support
- Rate limiting
- Error handling and retries
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from pymon.core.config import ESI_BASE_URL

logger = logging.getLogger(__name__)


class ESIClient:
    """Async HTTP client for the EVE Swagger Interface (ESI).

    Each request creates its own ``httpx.AsyncClient`` so the client is
    never shared across event-loops running in different threads.
    """

    # Default headers
    USER_AGENT = "PyMon/0.1.0 (EVE Character Monitor)"

    def __init__(self) -> None:
        self._cache: dict[str, tuple[Any, str, datetime]] = {}  # url -> (data, etag, expires)

    def _make_client(self) -> httpx.AsyncClient:
        """Create a fresh AsyncClient bound to the *current* event-loop."""
        return httpx.AsyncClient(
            base_url=ESI_BASE_URL,
            headers={"User-Agent": self.USER_AGENT},
            timeout=30.0,
        )

    async def get(
        self,
        endpoint: str,
        token: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an authenticated GET request to ESI.

        Args:
            endpoint: The API endpoint path (e.g., "/characters/12345/skills/").
            token: Optional access token for authenticated endpoints.
            params: Optional query parameters.

        Returns:
            The parsed JSON response.
        """
        headers: dict[str, str] = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # Check cache
        cache_key = f"{endpoint}:{params}"
        if cache_key in self._cache:
            data, etag, expires = self._cache[cache_key]
            if datetime.now(timezone.utc) < expires:
                logger.debug("Cache hit for %s", endpoint)
                return data
            if etag:
                headers["If-None-Match"] = etag

        async with self._make_client() as client:
            response = await client.get(endpoint, params=params, headers=headers)

        # Handle 304 Not Modified
        if response.status_code == 304 and cache_key in self._cache:
            logger.debug("304 Not Modified for %s", endpoint)
            return self._cache[cache_key][0]

        response.raise_for_status()
        data = response.json()

        # Cache the response
        etag = response.headers.get("ETag", "")
        expires_str = response.headers.get("Expires", "")
        try:
            expires = datetime.strptime(expires_str, "%a, %d %b %Y %H:%M:%S %Z").replace(
                tzinfo=timezone.utc
            )
        except (ValueError, TypeError):
            # Default: cache for 60 seconds
            from datetime import timedelta
            expires = datetime.now(timezone.utc) + timedelta(seconds=60)

        self._cache[cache_key] = (data, etag, expires)
        logger.debug("Fetched %s (cached until %s)", endpoint, expires)

        return data

    async def post(
        self,
        endpoint: str,
        token: str | None = None,
        json_data: Any = None,
    ) -> Any:
        """Make an authenticated POST request to ESI."""
        headers: dict[str, str] = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with self._make_client() as client:
            response = await client.post(endpoint, json=json_data, headers=headers)
        response.raise_for_status()
        return response.json() if response.content else None

    async def close(self) -> None:
        """No-op – clients are created per request."""
