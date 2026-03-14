"""SQLite database manager for PyMon."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Manages the local SQLite database for character data and tokens."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        """Get or create the database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self.db_path), check_same_thread=False
            )
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def initialize(self) -> None:
        """Create database tables if they don't exist."""
        logger.info("Initializing database at %s", self.db_path)
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS characters (
                character_id    INTEGER PRIMARY KEY,
                character_name  TEXT NOT NULL,
                corporation_id  INTEGER,
                alliance_id     INTEGER,
                access_token    TEXT,
                refresh_token   TEXT,
                token_expiry    TEXT,
                scopes          TEXT,
                added_at        TEXT DEFAULT (datetime('now')),
                last_updated    TEXT
            );

            CREATE TABLE IF NOT EXISTS skill_queue (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id    INTEGER NOT NULL,
                skill_id        INTEGER NOT NULL,
                finished_level  INTEGER NOT NULL,
                queue_position  INTEGER NOT NULL,
                start_date      TEXT,
                finish_date     TEXT,
                training_start_sp   INTEGER,
                level_start_sp      INTEGER,
                level_end_sp        INTEGER,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS skills (
                character_id    INTEGER NOT NULL,
                skill_id        INTEGER NOT NULL,
                active_skill_level  INTEGER NOT NULL DEFAULT 0,
                trained_skill_level INTEGER NOT NULL DEFAULT 0,
                skillpoints_in_skill INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (character_id, skill_id),
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS assets (
                item_id         INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                type_id         INTEGER NOT NULL,
                location_id     INTEGER,
                location_type   TEXT,
                location_flag   TEXT,
                quantity        INTEGER DEFAULT 1,
                is_singleton    INTEGER DEFAULT 0,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS wallet_journal (
                id              INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                date            TEXT NOT NULL,
                ref_type        TEXT,
                amount          REAL,
                balance         REAL,
                description     TEXT,
                first_party_id  INTEGER,
                second_party_id INTEGER,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS wallet_transactions (
                transaction_id  INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                date            TEXT,
                type_id         INTEGER,
                quantity        INTEGER,
                unit_price      REAL,
                client_id       INTEGER,
                location_id     INTEGER,
                is_buy          INTEGER DEFAULT 0,
                is_personal     INTEGER DEFAULT 1,
                journal_ref_id  INTEGER,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS mail_headers (
                mail_id         INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                subject         TEXT,
                from_id         INTEGER,
                timestamp       TEXT,
                is_read         INTEGER DEFAULT 0,
                labels          TEXT,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS contracts (
                contract_id     INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                issuer_id       INTEGER,
                assignee_id     INTEGER,
                acceptor_id     INTEGER,
                contract_type   TEXT,
                status          TEXT,
                title           TEXT,
                price           REAL DEFAULT 0,
                reward          REAL DEFAULT 0,
                collateral      REAL DEFAULT 0,
                volume          REAL DEFAULT 0,
                date_issued     TEXT,
                date_expired    TEXT,
                date_completed  TEXT,
                availability    TEXT,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS industry_jobs (
                job_id          INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                activity_id     INTEGER,
                blueprint_type_id INTEGER,
                product_type_id INTEGER,
                status          TEXT,
                runs            INTEGER DEFAULT 0,
                cost            REAL DEFAULT 0,
                start_date      TEXT,
                end_date        TEXT,
                completed_date  TEXT,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS market_orders (
                order_id        INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                type_id         INTEGER,
                location_id     INTEGER,
                is_buy_order    INTEGER DEFAULT 0,
                price           REAL DEFAULT 0,
                volume_remain   INTEGER DEFAULT 0,
                volume_total    INTEGER DEFAULT 0,
                duration        INTEGER DEFAULT 0,
                issued          TEXT,
                state           TEXT DEFAULT 'active',
                escrow          REAL DEFAULT 0,
                min_volume      INTEGER DEFAULT 1,
                range           TEXT,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS blueprints (
                item_id         INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                type_id         INTEGER NOT NULL,
                location_id     INTEGER,
                location_flag   TEXT,
                quantity        INTEGER DEFAULT 0,
                material_efficiency INTEGER DEFAULT 0,
                time_efficiency INTEGER DEFAULT 0,
                runs            INTEGER DEFAULT 0,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS fittings (
                fitting_id      INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                name            TEXT,
                description     TEXT,
                ship_type_id    INTEGER,
                items           TEXT,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS killmails (
                killmail_id     INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                killmail_hash   TEXT,
                killmail_time   TEXT,
                solar_system_id INTEGER,
                victim_ship_type_id INTEGER,
                total_value     REAL DEFAULT 0,
                is_loss         INTEGER DEFAULT 0,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                type            TEXT,
                sender_id       INTEGER,
                sender_type     TEXT,
                timestamp       TEXT,
                text            TEXT,
                is_read         INTEGER DEFAULT 0,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS contacts (
                character_id    INTEGER NOT NULL,
                contact_id      INTEGER NOT NULL,
                contact_type    TEXT,
                standing        REAL DEFAULT 0,
                label_ids       TEXT,
                is_watched      INTEGER DEFAULT 0,
                is_blocked      INTEGER DEFAULT 0,
                PRIMARY KEY (character_id, contact_id),
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS standings (
                character_id    INTEGER NOT NULL,
                from_id         INTEGER NOT NULL,
                from_type       TEXT,
                standing        REAL DEFAULT 0,
                PRIMARY KEY (character_id, from_id),
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS planetary_colonies (
                character_id    INTEGER NOT NULL,
                planet_id       INTEGER NOT NULL,
                solar_system_id INTEGER,
                planet_type     TEXT,
                upgrade_level   INTEGER DEFAULT 0,
                num_pins        INTEGER DEFAULT 0,
                last_update     TEXT,
                PRIMARY KEY (character_id, planet_id),
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS loyalty_points (
                character_id    INTEGER NOT NULL,
                corporation_id  INTEGER NOT NULL,
                loyalty_points  INTEGER DEFAULT 0,
                PRIMARY KEY (character_id, corporation_id),
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS bookmarks (
                bookmark_id     INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                folder_id       INTEGER,
                label           TEXT,
                notes           TEXT,
                location_id     INTEGER,
                creator_id      INTEGER,
                created         TEXT,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS mining_ledger (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id    INTEGER NOT NULL,
                date            TEXT,
                solar_system_id INTEGER,
                type_id         INTEGER,
                quantity        INTEGER DEFAULT 0,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS calendar_events (
                event_id        INTEGER PRIMARY KEY,
                character_id    INTEGER NOT NULL,
                title           TEXT,
                event_date      TEXT,
                event_response  TEXT,
                importance      INTEGER DEFAULT 0,
                owner_id        INTEGER,
                owner_type      TEXT,
                duration        INTEGER DEFAULT 0,
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS settings (
                key     TEXT PRIMARY KEY,
                value   TEXT
            );

            CREATE TABLE IF NOT EXISTS skill_plans (
                plan_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id    INTEGER NOT NULL,
                name            TEXT NOT NULL,
                created         TEXT DEFAULT (datetime('now')),
                updated         TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE,
                UNIQUE(character_id, name)
            );

            CREATE TABLE IF NOT EXISTS skill_plan_entries (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id         INTEGER NOT NULL,
                position        INTEGER NOT NULL,
                type_id         INTEGER NOT NULL,
                skill_name      TEXT NOT NULL,
                target_level    INTEGER NOT NULL,
                notes           TEXT DEFAULT '',
                FOREIGN KEY (plan_id) REFERENCES skill_plans(plan_id) ON DELETE CASCADE
            );
        """)
        self.conn.commit()
        logger.info("Database initialized successfully")

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ══════════════════════════════════════════════════════════════
    #  Skill Plan persistence
    # ══════════════════════════════════════════════════════════════

    def save_skill_plan(
        self,
        character_id: int,
        plan_name: str,
        entries: list[dict],
    ) -> int:
        """Save or update a skill plan.

        Args:
            character_id: The character this plan belongs to.
            plan_name: Plan name (unique per character).
            entries: List of dicts with keys: type_id, skill_name,
                     target_level, notes.

        Returns:
            The plan_id.
        """
        cur = self.conn.cursor()

        # Check if plan already exists
        existing = cur.execute(
            "SELECT plan_id FROM skill_plans WHERE character_id = ? AND name = ?",
            (character_id, plan_name),
        ).fetchone()

        if existing:
            plan_id = existing["plan_id"]
            # Update timestamp
            cur.execute(
                "UPDATE skill_plans SET updated = datetime('now') WHERE plan_id = ?",
                (plan_id,),
            )
            # Remove old entries
            cur.execute("DELETE FROM skill_plan_entries WHERE plan_id = ?", (plan_id,))
        else:
            cur.execute(
                "INSERT INTO skill_plans (character_id, name) VALUES (?, ?)",
                (character_id, plan_name),
            )
            plan_id = cur.lastrowid  # type: ignore[assignment]

        # Insert entries with position
        for pos, entry in enumerate(entries):
            cur.execute(
                """INSERT INTO skill_plan_entries
                   (plan_id, position, type_id, skill_name, target_level, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    plan_id,
                    pos,
                    entry["type_id"],
                    entry["skill_name"],
                    entry["target_level"],
                    entry.get("notes", ""),
                ),
            )

        self.conn.commit()
        logger.info("Saved skill plan '%s' (id=%d) with %d entries",
                     plan_name, plan_id, len(entries))
        return plan_id  # type: ignore[return-value]

    def load_skill_plan(
        self, character_id: int, plan_name: str
    ) -> list[dict] | None:
        """Load a skill plan's entries by name.

        Returns:
            List of entry dicts or None if plan not found.
        """
        row = self.conn.execute(
            "SELECT plan_id FROM skill_plans WHERE character_id = ? AND name = ?",
            (character_id, plan_name),
        ).fetchone()
        if not row:
            return None

        rows = self.conn.execute(
            """SELECT type_id, skill_name, target_level, notes
               FROM skill_plan_entries
               WHERE plan_id = ?
               ORDER BY position""",
            (row["plan_id"],),
        ).fetchall()

        return [dict(r) for r in rows]

    def list_skill_plans(self, character_id: int) -> list[dict]:
        """List all skill plans for a character.

        Returns:
            List of dicts with keys: name, created, updated, entry_count.
        """
        rows = self.conn.execute(
            """SELECT sp.name, sp.created, sp.updated,
                      COUNT(spe.id) as entry_count
               FROM skill_plans sp
               LEFT JOIN skill_plan_entries spe ON spe.plan_id = sp.plan_id
               WHERE sp.character_id = ?
               GROUP BY sp.plan_id
               ORDER BY sp.updated DESC""",
            (character_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_skill_plan(self, character_id: int, plan_name: str) -> bool:
        """Delete a skill plan by name.

        Returns:
            True if deleted, False if not found.
        """
        cur = self.conn.execute(
            "DELETE FROM skill_plans WHERE character_id = ? AND name = ?",
            (character_id, plan_name),
        )
        self.conn.commit()
        deleted = cur.rowcount > 0
        if deleted:
            logger.info("Deleted skill plan '%s' for character %d",
                         plan_name, character_id)
        return deleted

    def rename_skill_plan(
        self, character_id: int, old_name: str, new_name: str
    ) -> bool:
        """Rename a skill plan.

        Returns:
            True if renamed, False if not found or name conflict.
        """
        try:
            cur = self.conn.execute(
                """UPDATE skill_plans SET name = ?, updated = datetime('now')
                   WHERE character_id = ? AND name = ?""",
                (new_name, character_id, old_name),
            )
            self.conn.commit()
            return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False
