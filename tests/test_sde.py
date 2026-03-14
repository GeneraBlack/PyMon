"""Tests for the SDE database module."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from pymon.sde.database import SDEDatabase


def test_sde_database_not_loaded():
    """SDEDatabase reports not loaded when no file exists."""
    db = SDEDatabase(Path("/nonexistent/path/sde.db"))
    assert db.is_loaded() is False


def test_sde_type_name_unknown():
    """Unknown type IDs return a placeholder string."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    # Create minimal tables
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE types (type_id INTEGER PRIMARY KEY, name_en TEXT)")
    conn.execute("CREATE TABLE sde_meta (key TEXT PRIMARY KEY, build_number INTEGER, release_date TEXT)")
    conn.execute("INSERT INTO sde_meta VALUES ('sde', 1, '2026-01-01')")
    conn.commit()
    conn.close()

    sde = SDEDatabase(db_path)
    assert sde.is_loaded() is True
    assert sde.get_type_name(99999) == "Unknown Type #99999"
    sde.close()
    db_path.unlink()


def test_sde_type_name_found():
    """Known type IDs return their name."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE types (type_id INTEGER PRIMARY KEY, name_en TEXT)")
    conn.execute("INSERT INTO types VALUES (587, 'Rifter')")
    conn.execute("CREATE TABLE sde_meta (key TEXT PRIMARY KEY, build_number INTEGER, release_date TEXT)")
    conn.execute("INSERT INTO sde_meta VALUES ('sde', 1, '2026-01-01')")
    conn.commit()
    conn.close()

    sde = SDEDatabase(db_path)
    assert sde.get_type_name(587) == "Rifter"
    sde.close()
    db_path.unlink()
