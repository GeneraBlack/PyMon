"""Token storage and refresh management.

Securely stores OAuth2 tokens in the local database and handles
automatic token refresh before expiry.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from pymon.auth.sso import EVEAuth, SSOResult
from pymon.core.database import Database

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages token storage, retrieval, and refresh."""

    # Refresh tokens 5 minutes before they expire
    REFRESH_MARGIN = timedelta(minutes=5)

    def __init__(self, db: Database, auth: EVEAuth) -> None:
        self.db = db
        self.auth = auth

    def store_tokens(self, result: SSOResult) -> None:
        """Store tokens for a character after SSO login."""
        expiry = datetime.now(timezone.utc) + timedelta(seconds=result.expires_in)

        self.db.conn.execute(
            """
            INSERT INTO characters (character_id, character_name, access_token,
                                    refresh_token, token_expiry, scopes, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(character_id) DO UPDATE SET
                character_name = excluded.character_name,
                access_token = excluded.access_token,
                refresh_token = excluded.refresh_token,
                token_expiry = excluded.token_expiry,
                scopes = excluded.scopes,
                last_updated = datetime('now')
            """,
            (
                result.character_id,
                result.character_name,
                result.access_token,
                result.refresh_token,
                expiry.isoformat(),
                " ".join(result.scopes),
            ),
        )
        self.db.conn.commit()
        logger.info("Stored tokens for %s", result.character_name)

    async def get_valid_token(self, character_id: int) -> str | None:
        """Get a valid access token, refreshing if needed.

        Args:
            character_id: The EVE character ID.

        Returns:
            A valid access token, or None if no token is stored.
        """
        row = self.db.conn.execute(
            "SELECT access_token, refresh_token, token_expiry FROM characters WHERE character_id = ?",
            (character_id,),
        ).fetchone()

        if not row:
            return None

        access_token = row["access_token"]
        refresh_token = row["refresh_token"]
        expiry_str = row["token_expiry"]

        if not expiry_str or not refresh_token:
            return access_token

        expiry = datetime.fromisoformat(expiry_str)
        now = datetime.now(timezone.utc)

        # If token is still valid (with margin), return it
        if now + self.REFRESH_MARGIN < expiry:
            return access_token

        # Token expired or about to expire – refresh it
        logger.info("Refreshing token for character %d", character_id)
        try:
            result = await self.auth.refresh_access_token(refresh_token)
            self.store_tokens(result)
            return result.access_token
        except Exception:
            logger.error("Failed to refresh token for character %d", character_id, exc_info=True)
            return None

    def get_all_characters(self) -> list[dict]:
        """Get all stored characters."""
        rows = self.db.conn.execute(
            "SELECT character_id, character_name, scopes, last_updated FROM characters"
        ).fetchall()
        return [dict(row) for row in rows]

    def remove_character(self, character_id: int) -> None:
        """Remove a character and all associated data."""
        self.db.conn.execute("DELETE FROM characters WHERE character_id = ?", (character_id,))
        self.db.conn.commit()
        logger.info("Removed character %d", character_id)
