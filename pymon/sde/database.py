"""SDE database query interface.

Provides convenient methods to look up items, systems, and other
static data from the imported SDE SQLite database.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SDEDatabase:
    """Query interface for the SDE SQLite database."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self.db_path), check_same_thread=False
            )
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _get_row(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        """Execute a query and return the first row as a dict, or None."""
        try:
            row = self.conn.execute(sql, params).fetchone()
            return dict(row) if row else None
        except sqlite3.OperationalError:
            return None

    def _get_rows(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        """Execute a query and return all rows as dicts."""
        try:
            return [dict(r) for r in self.conn.execute(sql, params).fetchall()]
        except sqlite3.OperationalError:
            return []

    def _get_name(
        self, table: str, id_col: str, id_val: int,
        name_col: str = "name_en", fallback: str = "Unknown",
    ) -> str:
        """Generic name lookup helper."""
        row = self._get_row(
            f"SELECT {name_col} FROM {table} WHERE {id_col} = ?", (id_val,)
        )
        if row and row.get(name_col):
            return row[name_col]
        return f"{fallback} #{id_val}"

    # ── Meta ────────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        """Check if the SDE database has been imported."""
        if not self.db_path.exists():
            return False
        try:
            row = self.conn.execute("SELECT build_number FROM sde_meta LIMIT 1").fetchone()
            return row is not None
        except sqlite3.OperationalError:
            return False

    def get_build_number(self) -> int | None:
        """Get the SDE build number."""
        row = self._get_row("SELECT build_number FROM sde_meta LIMIT 1")
        return row["build_number"] if row else None

    def get_release_date(self) -> str | None:
        """Get the SDE release date."""
        row = self._get_row("SELECT release_date FROM sde_meta LIMIT 1")
        return row["release_date"] if row else None

    # ── Type lookups ────────────────────────────────────────────

    def get_type_name(self, type_id: int, lang: str = "en") -> str:
        """Get the name of an item type."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        row = self._get_row(
            f"SELECT {col}, name_en FROM types WHERE type_id = ?", (type_id,)
        )
        if row:
            return row[col] or row["name_en"] or f"Unknown Type #{type_id}"
        return f"Unknown Type #{type_id}"

    def get_type(self, type_id: int) -> dict[str, Any] | None:
        """Get full type info."""
        return self._get_row("SELECT * FROM types WHERE type_id = ?", (type_id,))

    def search_types(
        self, query: str, published_only: bool = True, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Search types by name."""
        sql = "SELECT * FROM types WHERE name_en LIKE ?"
        if published_only:
            sql += " AND published = 1"
        sql += f" LIMIT {limit}"
        return self._get_rows(sql, (f"%{query}%",))

    def get_types_by_group(self, group_id: int) -> list[dict[str, Any]]:
        """Get all types in a group."""
        return self._get_rows(
            "SELECT * FROM types WHERE group_id = ? ORDER BY name_en", (group_id,)
        )

    def get_types_by_category(self, category_id: int) -> list[dict[str, Any]]:
        """Get all types in a category (via groups)."""
        return self._get_rows(
            """SELECT t.* FROM types t
               JOIN groups g ON t.group_id = g.group_id
               WHERE g.category_id = ? ORDER BY t.name_en""",
            (category_id,),
        )

    def get_types_by_market_group(self, market_group_id: int) -> list[dict[str, Any]]:
        """Get all types in a market group."""
        return self._get_rows(
            "SELECT * FROM types WHERE market_group_id = ? ORDER BY name_en",
            (market_group_id,),
        )

    # ── Group / Category lookups ────────────────────────────────

    def get_group(self, group_id: int) -> dict[str, Any] | None:
        """Get group info."""
        return self._get_row("SELECT * FROM groups WHERE group_id = ?", (group_id,))

    def get_group_name(self, group_id: int, lang: str = "en") -> str:
        """Get group name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name("groups", "group_id", group_id, col, "Unknown Group")

    def get_category(self, category_id: int) -> dict[str, Any] | None:
        """Get category info."""
        return self._get_row(
            "SELECT * FROM categories WHERE category_id = ?", (category_id,)
        )

    def get_category_name(self, category_id: int, lang: str = "en") -> str:
        """Get category name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name("categories", "category_id", category_id, col, "Unknown Category")

    def get_category_for_type(self, type_id: int) -> dict[str, Any] | None:
        """Get the category a type belongs to (type → group → category)."""
        return self._get_row(
            """SELECT c.* FROM categories c
               JOIN groups g ON c.category_id = g.category_id
               JOIN types t ON t.group_id = g.group_id
               WHERE t.type_id = ?""",
            (type_id,),
        )

    # ── Map lookups ─────────────────────────────────────────────

    def get_system_name(self, system_id: int) -> str:
        """Get solar system name."""
        return self._get_name(
            "map_solar_systems", "system_id", system_id, "name_en", "Unknown System"
        )

    def get_system(self, system_id: int) -> dict[str, Any] | None:
        """Get full solar system info."""
        return self._get_row(
            "SELECT * FROM map_solar_systems WHERE system_id = ?", (system_id,)
        )

    def get_systems_in_region(self, region_id: int) -> list[dict[str, Any]]:
        """Get all solar systems in a region."""
        return self._get_rows(
            "SELECT * FROM map_solar_systems WHERE region_id = ? ORDER BY name_en",
            (region_id,),
        )

    def get_systems_in_constellation(self, constellation_id: int) -> list[dict[str, Any]]:
        """Get all solar systems in a constellation."""
        return self._get_rows(
            "SELECT * FROM map_solar_systems WHERE constellation_id = ? ORDER BY name_en",
            (constellation_id,),
        )

    def get_region_name(self, region_id: int) -> str:
        """Get region name."""
        return self._get_name(
            "map_regions", "region_id", region_id, "name_en", "Unknown Region"
        )

    def get_region(self, region_id: int) -> dict[str, Any] | None:
        """Get full region info."""
        return self._get_row(
            "SELECT * FROM map_regions WHERE region_id = ?", (region_id,)
        )

    def get_all_regions(self) -> list[dict[str, Any]]:
        """Get all regions."""
        return self._get_rows("SELECT * FROM map_regions ORDER BY name_en")

    def get_constellation_name(self, constellation_id: int) -> str:
        """Get constellation name."""
        return self._get_name(
            "map_constellations", "constellation_id", constellation_id,
            "name_en", "Unknown Constellation",
        )

    def get_constellation(self, constellation_id: int) -> dict[str, Any] | None:
        """Get full constellation info."""
        return self._get_row(
            "SELECT * FROM map_constellations WHERE constellation_id = ?",
            (constellation_id,),
        )

    def get_constellations_in_region(self, region_id: int) -> list[dict[str, Any]]:
        """Get all constellations in a region."""
        return self._get_rows(
            "SELECT * FROM map_constellations WHERE region_id = ? ORDER BY name_en",
            (region_id,),
        )

    def get_planet(self, planet_id: int) -> dict[str, Any] | None:
        """Get planet info."""
        return self._get_row(
            "SELECT * FROM map_planets WHERE planet_id = ?", (planet_id,)
        )

    def get_planets_in_system(self, system_id: int) -> list[dict[str, Any]]:
        """Get all planets in a solar system."""
        return self._get_rows(
            "SELECT * FROM map_planets WHERE solar_system_id = ? ORDER BY celestial_index",
            (system_id,),
        )

    def get_planet_name(self, planet_id: int) -> str:
        """Get planet name (constructed from system name + index)."""
        row = self._get_row(
            """SELECT p.celestial_index, s.name_en
               FROM map_planets p
               JOIN map_solar_systems s ON p.solar_system_id = s.system_id
               WHERE p.planet_id = ?""",
            (planet_id,),
        )
        if row:
            return f"{row['name_en']} {_roman(row['celestial_index'])}"
        return f"Unknown Planet #{planet_id}"

    def get_moon(self, moon_id: int) -> dict[str, Any] | None:
        """Get moon info."""
        return self._get_row("SELECT * FROM map_moons WHERE moon_id = ?", (moon_id,))

    def get_moons_in_system(self, system_id: int) -> list[dict[str, Any]]:
        """Get all moons in a solar system."""
        return self._get_rows(
            "SELECT * FROM map_moons WHERE solar_system_id = ? ORDER BY celestial_index, orbit_index",
            (system_id,),
        )

    def get_moon_name(self, moon_id: int) -> str:
        """Get moon name (system name + planet index + moon index)."""
        row = self._get_row(
            """SELECT m.celestial_index, m.orbit_index, s.name_en
               FROM map_moons m
               JOIN map_solar_systems s ON m.solar_system_id = s.system_id
               WHERE m.moon_id = ?""",
            (moon_id,),
        )
        if row:
            return f"{row['name_en']} {_roman(row['celestial_index'])} - Moon {row['orbit_index']}"
        return f"Unknown Moon #{moon_id}"

    def get_stargate(self, stargate_id: int) -> dict[str, Any] | None:
        """Get stargate info."""
        return self._get_row(
            "SELECT * FROM map_stargates WHERE stargate_id = ?", (stargate_id,)
        )

    def get_star(self, system_id: int) -> dict[str, Any] | None:
        """Get star info for a solar system."""
        return self._get_row(
            "SELECT * FROM map_stars WHERE solar_system_id = ?", (system_id,)
        )

    def get_landmark(self, landmark_id: int) -> dict[str, Any] | None:
        """Get landmark info."""
        return self._get_row(
            "SELECT * FROM map_landmarks WHERE landmark_id = ?", (landmark_id,)
        )

    def get_security_status(self, system_id: int) -> float | None:
        """Get security status for a system."""
        row = self._get_row(
            "SELECT security_status FROM map_solar_systems WHERE system_id = ?",
            (system_id,),
        )
        return row["security_status"] if row else None

    def get_region_for_system(self, system_id: int) -> dict[str, Any] | None:
        """Get the region a system belongs to."""
        sys_info = self.get_system(system_id)
        if sys_info and sys_info.get("region_id"):
            return self.get_region(sys_info["region_id"])
        return None

    # ── Station lookups ─────────────────────────────────────────

    def get_station(self, station_id: int) -> dict[str, Any] | None:
        """Get NPC station info."""
        return self._get_row(
            "SELECT * FROM npc_stations WHERE station_id = ?", (station_id,)
        )

    def get_station_name(self, station_id: int) -> str:
        """Get NPC station name (constructed: system + owner corp)."""
        row = self._get_row(
            """SELECT s.station_id, sys.name_en as system_name,
                      c.name_en as owner_name, t.name_en as type_name
               FROM npc_stations s
               JOIN map_solar_systems sys ON s.solar_system_id = sys.system_id
               LEFT JOIN npc_corporations c ON s.owner_id = c.corporation_id
               LEFT JOIN types t ON s.type_id = t.type_id
               WHERE s.station_id = ?""",
            (station_id,),
        )
        if row:
            parts = [row["system_name"] or ""]
            if row.get("owner_name"):
                parts.append(row["owner_name"])
            if row.get("type_name"):
                parts.append(row["type_name"])
            return " - ".join(p for p in parts if p)
        return f"Unknown Station #{station_id}"

    def get_stations_in_system(self, system_id: int) -> list[dict[str, Any]]:
        """Get all NPC stations in a solar system."""
        return self._get_rows(
            "SELECT * FROM npc_stations WHERE solar_system_id = ?", (system_id,)
        )

    # ── Faction lookups ─────────────────────────────────────────

    def get_faction(self, faction_id: int) -> dict[str, Any] | None:
        """Get faction info."""
        return self._get_row(
            "SELECT * FROM factions WHERE faction_id = ?", (faction_id,)
        )

    def get_faction_name(self, faction_id: int, lang: str = "en") -> str:
        """Get faction name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name("factions", "faction_id", faction_id, col, "Unknown Faction")

    def get_all_factions(self) -> list[dict[str, Any]]:
        """Get all factions."""
        return self._get_rows("SELECT * FROM factions ORDER BY name_en")

    # ── Race lookups ────────────────────────────────────────────

    def get_race(self, race_id: int) -> dict[str, Any] | None:
        """Get race info."""
        return self._get_row("SELECT * FROM races WHERE race_id = ?", (race_id,))

    def get_race_name(self, race_id: int, lang: str = "en") -> str:
        """Get race name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name("races", "race_id", race_id, col, "Unknown Race")

    def get_all_races(self) -> list[dict[str, Any]]:
        """Get all races."""
        return self._get_rows("SELECT * FROM races ORDER BY name_en")

    # ── Bloodline lookups ───────────────────────────────────────

    def get_bloodline(self, bloodline_id: int) -> dict[str, Any] | None:
        """Get bloodline info."""
        return self._get_row(
            "SELECT * FROM bloodlines WHERE bloodline_id = ?", (bloodline_id,)
        )

    def get_bloodline_name(self, bloodline_id: int, lang: str = "en") -> str:
        """Get bloodline name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name(
            "bloodlines", "bloodline_id", bloodline_id, col, "Unknown Bloodline"
        )

    def get_bloodlines_for_race(self, race_id: int) -> list[dict[str, Any]]:
        """Get all bloodlines for a race."""
        return self._get_rows(
            "SELECT * FROM bloodlines WHERE race_id = ? ORDER BY name_en",
            (race_id,),
        )

    # ── Ancestry lookups ───────────────────────────────────────

    def get_ancestry(self, ancestry_id: int) -> dict[str, Any] | None:
        """Get ancestry info."""
        return self._get_row(
            "SELECT * FROM ancestries WHERE ancestry_id = ?", (ancestry_id,)
        )

    def get_ancestry_name(self, ancestry_id: int, lang: str = "en") -> str:
        """Get ancestry name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name(
            "ancestries", "ancestry_id", ancestry_id, col, "Unknown Ancestry"
        )

    def get_ancestries_for_bloodline(self, bloodline_id: int) -> list[dict[str, Any]]:
        """Get all ancestries for a bloodline."""
        return self._get_rows(
            "SELECT * FROM ancestries WHERE bloodline_id = ? ORDER BY name_en",
            (bloodline_id,),
        )

    # ── NPC Corporation lookups ─────────────────────────────────

    def get_npc_corporation(self, corporation_id: int) -> dict[str, Any] | None:
        """Get NPC corporation info."""
        return self._get_row(
            "SELECT * FROM npc_corporations WHERE corporation_id = ?",
            (corporation_id,),
        )

    def get_npc_corporation_name(self, corporation_id: int, lang: str = "en") -> str:
        """Get NPC corporation name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name(
            "npc_corporations", "corporation_id", corporation_id,
            col, "Unknown Corporation",
        )

    def get_npc_corporations_for_faction(self, faction_id: int) -> list[dict[str, Any]]:
        """Get all NPC corps belonging to a faction."""
        return self._get_rows(
            "SELECT * FROM npc_corporations WHERE faction_id = ? ORDER BY name_en",
            (faction_id,),
        )

    # ── NPC Character lookups ───────────────────────────────────

    def get_npc_character(self, character_id: int) -> dict[str, Any] | None:
        """Get NPC character info."""
        return self._get_row(
            "SELECT * FROM npc_characters WHERE character_id = ?", (character_id,)
        )

    def get_npc_character_name(self, character_id: int, lang: str = "en") -> str:
        """Get NPC character name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name(
            "npc_characters", "character_id", character_id, col, "Unknown NPC"
        )

    # ── Market group lookups ────────────────────────────────────

    def get_market_group(self, market_group_id: int) -> dict[str, Any] | None:
        """Get market group info."""
        return self._get_row(
            "SELECT * FROM market_groups WHERE market_group_id = ?",
            (market_group_id,),
        )

    def get_market_group_name(self, market_group_id: int, lang: str = "en") -> str:
        """Get market group name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name(
            "market_groups", "market_group_id", market_group_id,
            col, "Unknown Market Group",
        )

    def get_market_group_tree(self, market_group_id: int) -> list[dict[str, Any]]:
        """Get market group hierarchy from root to this group."""
        path: list[dict[str, Any]] = []
        current_id: int | None = market_group_id
        visited: set[int] = set()
        while current_id is not None and current_id not in visited:
            visited.add(current_id)
            group = self.get_market_group(current_id)
            if group is None:
                break
            path.insert(0, group)
            current_id = group.get("parent_group_id")
        return path

    def get_market_group_children(self, parent_id: int | None) -> list[dict[str, Any]]:
        """Get child market groups (pass None for root groups)."""
        if parent_id is None:
            return self._get_rows(
                "SELECT * FROM market_groups WHERE parent_group_id IS NULL ORDER BY name_en"
            )
        return self._get_rows(
            "SELECT * FROM market_groups WHERE parent_group_id = ? ORDER BY name_en",
            (parent_id,),
        )

    # ── Meta group lookups ──────────────────────────────────────

    def get_meta_group(self, meta_group_id: int) -> dict[str, Any] | None:
        """Get meta group info (Tech I, Tech II, Faction, etc.)."""
        return self._get_row(
            "SELECT * FROM meta_groups WHERE meta_group_id = ?", (meta_group_id,)
        )

    def get_meta_group_name(self, meta_group_id: int, lang: str = "en") -> str:
        """Get meta group name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name(
            "meta_groups", "meta_group_id", meta_group_id, col, "Unknown Meta"
        )

    # ── Dogma lookups ───────────────────────────────────────────

    def get_dogma_attribute(self, attribute_id: int) -> dict[str, Any] | None:
        """Get dogma attribute info."""
        return self._get_row(
            "SELECT * FROM dogma_attributes WHERE attribute_id = ?",
            (attribute_id,),
        )

    def get_dogma_attribute_name(self, attribute_id: int) -> str:
        """Get dogma attribute display name."""
        row = self._get_row(
            "SELECT display_name_en, name FROM dogma_attributes WHERE attribute_id = ?",
            (attribute_id,),
        )
        if row:
            return row["display_name_en"] or row["name"] or f"Attr #{attribute_id}"
        return f"Attr #{attribute_id}"

    def get_dogma_effect(self, effect_id: int) -> dict[str, Any] | None:
        """Get dogma effect info."""
        return self._get_row(
            "SELECT * FROM dogma_effects WHERE effect_id = ?", (effect_id,)
        )

    def get_dogma_unit(self, unit_id: int) -> dict[str, Any] | None:
        """Get dogma unit info."""
        return self._get_row(
            "SELECT * FROM dogma_units WHERE unit_id = ?", (unit_id,)
        )

    def get_dogma_unit_name(self, unit_id: int) -> str:
        """Get dogma unit display name (e.g. 'm', 'HP', 'MW')."""
        row = self._get_row(
            "SELECT display_name_en, name FROM dogma_units WHERE unit_id = ?",
            (unit_id,),
        )
        if row:
            return row["display_name_en"] or row["name"] or ""
        return ""

    def get_dogma_attribute_category(self, category_id: int) -> dict[str, Any] | None:
        """Get dogma attribute category."""
        return self._get_row(
            "SELECT * FROM dogma_attribute_categories WHERE category_id = ?",
            (category_id,),
        )

    def get_type_dogma_attributes(self, type_id: int) -> list[dict[str, Any]]:
        """Get all dogma attributes for a type with display info."""
        return self._get_rows(
            """SELECT tda.attribute_id, tda.value,
                      da.name, da.display_name_en, da.unit_id, da.high_is_good
               FROM type_dogma_attributes tda
               JOIN dogma_attributes da ON tda.attribute_id = da.attribute_id
               WHERE tda.type_id = ?
               ORDER BY da.display_name_en""",
            (type_id,),
        )

    def get_type_dogma_effects(self, type_id: int) -> list[dict[str, Any]]:
        """Get all dogma effects for a type."""
        return self._get_rows(
            """SELECT tde.effect_id, tde.is_default, de.name, de.guid
               FROM type_dogma_effects tde
               JOIN dogma_effects de ON tde.effect_id = de.effect_id
               WHERE tde.type_id = ?""",
            (type_id,),
        )

    # ── Blueprint lookups ───────────────────────────────────────

    def get_blueprint(self, blueprint_type_id: int) -> dict[str, Any] | None:
        """Get blueprint info."""
        return self._get_row(
            "SELECT * FROM blueprints WHERE blueprint_type_id = ?",
            (blueprint_type_id,),
        )

    def get_blueprint_materials(self, blueprint_type_id: int) -> list[dict[str, Any]]:
        """Get manufacturing materials for a blueprint."""
        return self._get_rows(
            """SELECT bm.type_id, bm.quantity, t.name_en as type_name
               FROM blueprint_materials bm
               LEFT JOIN types t ON bm.type_id = t.type_id
               WHERE bm.blueprint_type_id = ?""",
            (blueprint_type_id,),
        )

    def get_blueprint_products(self, blueprint_type_id: int) -> list[dict[str, Any]]:
        """Get manufacturing products for a blueprint."""
        return self._get_rows(
            """SELECT bp.type_id, bp.quantity, t.name_en as type_name
               FROM blueprint_products bp
               LEFT JOIN types t ON bp.type_id = t.type_id
               WHERE bp.blueprint_type_id = ?""",
            (blueprint_type_id,),
        )

    def get_blueprint_invention_products(self, blueprint_type_id: int) -> list[dict[str, Any]]:
        """Get invention products for a blueprint."""
        return self._get_rows(
            """SELECT bip.type_id, bip.quantity, bip.probability,
                      t.name_en as type_name
               FROM blueprint_invention_products bip
               LEFT JOIN types t ON bip.type_id = t.type_id
               WHERE bip.blueprint_type_id = ?""",
            (blueprint_type_id,),
        )

    def get_blueprint_for_product(self, product_type_id: int) -> dict[str, Any] | None:
        """Find the blueprint that manufactures a given product type."""
        row = self._get_row(
            """SELECT bp.blueprint_type_id, t.name_en as blueprint_name
               FROM blueprint_products bp
               LEFT JOIN types t ON bp.blueprint_type_id = t.type_id
               WHERE bp.type_id = ?""",
            (product_type_id,),
        )
        return row

    # ── Type materials (reprocessing) ───────────────────────────

    def get_type_materials(self, type_id: int) -> list[dict[str, Any]]:
        """Get reprocessing/recycling materials for a type."""
        return self._get_rows(
            """SELECT tm.material_type_id, tm.quantity,
                      t.name_en as material_name
               FROM type_materials tm
               LEFT JOIN types t ON tm.material_type_id = t.type_id
               WHERE tm.type_id = ?""",
            (type_id,),
        )

    # ── Type bonuses ────────────────────────────────────────────

    def get_type_role_bonuses(self, type_id: int) -> list[dict[str, Any]]:
        """Get role bonuses for a ship/structure type."""
        return self._get_rows(
            "SELECT * FROM type_role_bonuses WHERE type_id = ? ORDER BY importance",
            (type_id,),
        )

    def get_type_trait_bonuses(self, type_id: int) -> list[dict[str, Any]]:
        """Get trait (skill-based) bonuses for a ship type."""
        return self._get_rows(
            """SELECT ttb.*, t.name_en as skill_name
               FROM type_trait_bonuses ttb
               LEFT JOIN types t ON ttb.skill_type_id = t.type_id
               WHERE ttb.type_id = ? ORDER BY ttb.skill_type_id, ttb.importance""",
            (type_id,),
        )

    # ── Compressed types ────────────────────────────────────────

    def get_compressed_type(self, type_id: int) -> int | None:
        """Get the compressed version of a type (ore compression)."""
        row = self._get_row(
            "SELECT compressed_type_id FROM compressible_types WHERE type_id = ?",
            (type_id,),
        )
        return row["compressed_type_id"] if row else None

    # ── Certificates ────────────────────────────────────────────

    def get_certificate(self, certificate_id: int) -> dict[str, Any] | None:
        """Get certificate info."""
        return self._get_row(
            "SELECT * FROM certificates WHERE certificate_id = ?",
            (certificate_id,),
        )

    def get_certificate_name(self, certificate_id: int, lang: str = "en") -> str:
        """Get certificate name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name(
            "certificates", "certificate_id", certificate_id, col, "Unknown Certificate"
        )

    def get_all_certificates(self) -> list[dict[str, Any]]:
        """Get all certificates, ordered by name."""
        return self._get_rows(
            "SELECT * FROM certificates ORDER BY name_en"
        )

    def get_certificates_by_group(self, group_id: int) -> list[dict[str, Any]]:
        """Get certificates belonging to a specific group."""
        return self._get_rows(
            "SELECT * FROM certificates WHERE group_id = ? ORDER BY name_en",
            (group_id,),
        )

    def get_certificate_groups(self) -> list[dict[str, Any]]:
        """Get unique certificate group IDs with their names (from groups table)."""
        return self._get_rows(
            """SELECT DISTINCT c.group_id, g.name_en as group_name
               FROM certificates c
               LEFT JOIN groups g ON c.group_id = g.group_id
               ORDER BY g.name_en"""
        )

    def get_certificate_skills(self, certificate_id: int) -> list[dict[str, Any]]:
        """Get skill requirements for a certificate with skill names."""
        return self._get_rows(
            """SELECT cs.*, t.name_en as skill_name
               FROM certificate_skills cs
               LEFT JOIN types t ON cs.skill_type_id = t.type_id
               WHERE cs.certificate_id = ?
               ORDER BY t.name_en""",
            (certificate_id,),
        )

    def get_certificate_recommended_types(self, certificate_id: int) -> list[dict[str, Any]]:
        """Get recommended ship types for a certificate."""
        return self._get_rows(
            """SELECT crt.type_id, t.name_en as type_name
               FROM certificate_recommended_types crt
               LEFT JOIN types t ON crt.type_id = t.type_id
               WHERE crt.certificate_id = ?
               ORDER BY t.name_en""",
            (certificate_id,),
        )

    # ── Masteries ───────────────────────────────────────────────

    def get_ship_masteries(self, type_id: int) -> list[dict[str, Any]]:
        """Get mastery certificates for a ship type, all levels."""
        return self._get_rows(
            """SELECT mc.mastery_level, mc.certificate_id,
                      c.name_en as cert_name, c.description_en
               FROM mastery_certificates mc
               LEFT JOIN certificates c ON mc.certificate_id = c.certificate_id
               WHERE mc.type_id = ?
               ORDER BY mc.mastery_level, c.name_en""",
            (type_id,),
        )

    def get_ships_with_masteries(self) -> list[dict[str, Any]]:
        """Get all ship types that have mastery definitions."""
        return self._get_rows(
            """SELECT DISTINCT mc.type_id, t.name_en as type_name,
                      g.name_en as group_name, g.group_id
               FROM mastery_certificates mc
               LEFT JOIN types t ON mc.type_id = t.type_id
               LEFT JOIN groups g ON t.group_id = g.group_id
               ORDER BY g.name_en, t.name_en"""
        )

    # ── Character attributes ────────────────────────────────────

    def get_character_attribute(self, attribute_id: int) -> dict[str, Any] | None:
        """Get character attribute info (Intelligence, Memory, etc.)."""
        return self._get_row(
            "SELECT * FROM character_attributes WHERE attribute_id = ?",
            (attribute_id,),
        )

    # ── Planet / PI lookups ─────────────────────────────────────

    def get_planet_schematic(self, schematic_id: int) -> dict[str, Any] | None:
        """Get planet schematic info."""
        return self._get_row(
            "SELECT * FROM planet_schematics WHERE schematic_id = ?",
            (schematic_id,),
        )

    def get_planet_schematic_name(self, schematic_id: int, lang: str = "en") -> str:
        """Get planet schematic name."""
        col = f"name_{lang}" if lang != "en" else "name_en"
        return self._get_name(
            "planet_schematics", "schematic_id", schematic_id,
            col, "Unknown Schematic",
        )

    def get_planet_schematic_types(self, schematic_id: int) -> list[dict[str, Any]]:
        """Get input/output types for a planet schematic."""
        return self._get_rows(
            """SELECT pst.type_id, pst.quantity, pst.is_input,
                      t.name_en as type_name
               FROM planet_schematic_types pst
               LEFT JOIN types t ON pst.type_id = t.type_id
               WHERE pst.schematic_id = ?""",
            (schematic_id,),
        )

    # ── SKIN lookups ────────────────────────────────────────────

    def get_skin(self, skin_id: int) -> dict[str, Any] | None:
        """Get SKIN info."""
        return self._get_row("SELECT * FROM skins WHERE skin_id = ?", (skin_id,))

    def get_skin_material(self, material_id: int) -> dict[str, Any] | None:
        """Get SKIN material info."""
        return self._get_row(
            "SELECT * FROM skin_materials WHERE material_id = ?", (material_id,)
        )

    def get_skin_material_name(self, material_id: int, lang: str = "en") -> str:
        """Get SKIN material display name."""
        col = f"display_name_{lang}" if lang != "en" else "display_name_en"
        return self._get_name(
            "skin_materials", "material_id", material_id, col, "Unknown Material"
        )

    def get_skins_for_type(self, type_id: int) -> list[dict[str, Any]]:
        """Get all SKINs available for a ship type."""
        return self._get_rows(
            """SELECT s.*, sm.display_name_en as material_name
               FROM skin_types st
               JOIN skins s ON st.skin_id = s.skin_id
               LEFT JOIN skin_materials sm ON s.skin_material_id = sm.material_id
               WHERE st.type_id = ? AND s.visible_tranquility = 1""",
            (type_id,),
        )

    # ── Station services & operations ───────────────────────────

    def get_station_service(self, service_id: int) -> dict[str, Any] | None:
        """Get station service info."""
        return self._get_row(
            "SELECT * FROM station_services WHERE service_id = ?", (service_id,)
        )

    def get_station_operation(self, operation_id: int) -> dict[str, Any] | None:
        """Get station operation info."""
        return self._get_row(
            "SELECT * FROM station_operations WHERE operation_id = ?",
            (operation_id,),
        )

    # ── Corporation activity lookups ────────────────────────────

    def get_corporation_activity(self, activity_id: int) -> dict[str, Any] | None:
        """Get corporation activity info."""
        return self._get_row(
            "SELECT * FROM corporation_activities WHERE activity_id = ?",
            (activity_id,),
        )

    # ── Clone grade lookups ─────────────────────────────────────

    def get_clone_grade(self, clone_grade_id: int) -> dict[str, Any] | None:
        """Get clone grade info."""
        return self._get_row(
            "SELECT * FROM clone_grades WHERE clone_grade_id = ?",
            (clone_grade_id,),
        )

    # ── Agent type lookups ──────────────────────────────────────

    def get_agent_type(self, agent_type_id: int) -> dict[str, Any] | None:
        """Get agent type info."""
        return self._get_row(
            "SELECT * FROM agent_types WHERE agent_type_id = ?", (agent_type_id,)
        )

    # ── Dynamic item attributes (abyssal/mutaplasmid) ──────────

    def get_dynamic_item_attributes(self, type_id: int) -> list[dict[str, Any]]:
        """Get dynamic attribute ranges for an abyssal mutaplasmid type."""
        return self._get_rows(
            """SELECT dia.attribute_id, dia.min_value, dia.max_value,
                      da.display_name_en, da.name, da.unit_id
               FROM dynamic_item_attributes dia
               LEFT JOIN dogma_attributes da ON dia.attribute_id = da.attribute_id
               WHERE dia.type_id = ?""",
            (type_id,),
        )

    # ── Contraband lookups ──────────────────────────────────────

    def get_contraband_factions(self, type_id: int) -> list[dict[str, Any]]:
        """Get contraband status for a type across factions."""
        return self._get_rows(
            """SELECT cf.*, f.name_en as faction_name
               FROM contraband_factions cf
               LEFT JOIN factions f ON cf.faction_id = f.faction_id
               WHERE cf.type_id = ?""",
            (type_id,),
        )

    def is_contraband(self, type_id: int, faction_id: int | None = None) -> bool:
        """Check if a type is contraband (optionally for a specific faction)."""
        if faction_id:
            row = self._get_row(
                "SELECT 1 FROM contraband_factions WHERE type_id = ? AND faction_id = ?",
                (type_id, faction_id),
            )
        else:
            row = self._get_row(
                "SELECT 1 FROM contraband_factions WHERE type_id = ?", (type_id,)
            )
        return row is not None

    # ── Sovereignty ─────────────────────────────────────────────

    def get_sovereignty_upgrade(self, type_id: int) -> dict[str, Any] | None:
        """Get sovereignty upgrade info."""
        return self._get_row(
            "SELECT * FROM sovereignty_upgrades WHERE type_id = ?", (type_id,)
        )

    # ── Graphics / Icons ────────────────────────────────────────

    def get_graphic(self, graphic_id: int) -> dict[str, Any] | None:
        """Get graphic info."""
        return self._get_row(
            "SELECT * FROM graphics WHERE graphic_id = ?", (graphic_id,)
        )

    def get_icon(self, icon_id: int) -> dict[str, Any] | None:
        """Get icon info."""
        return self._get_row("SELECT * FROM icons WHERE icon_id = ?", (icon_id,))

    def get_icon_file(self, icon_id: int) -> str | None:
        """Get icon file path."""
        row = self._get_row(
            "SELECT icon_file FROM icons WHERE icon_id = ?", (icon_id,)
        )
        return row["icon_file"] if row else None

    # ── Utility: entity name resolution ─────────────────────────

    def resolve_npc_entity_name(self, entity_id: int) -> str | None:
        """Try to resolve an entity ID to a name from SDE data.

        Tries NPC corporations, factions, NPC characters in order.
        Returns None if not found (the entity may be a player).
        """
        # NPC corporation?
        row = self._get_row(
            "SELECT name_en FROM npc_corporations WHERE corporation_id = ?",
            (entity_id,),
        )
        if row and row["name_en"]:
            return row["name_en"]

        # Faction?
        row = self._get_row(
            "SELECT name_en FROM factions WHERE faction_id = ?", (entity_id,)
        )
        if row and row["name_en"]:
            return row["name_en"]

        # NPC character?
        row = self._get_row(
            "SELECT name_en FROM npc_characters WHERE character_id = ?",
            (entity_id,),
        )
        if row and row["name_en"]:
            return row["name_en"]

        return None

    # ── Statistics ──────────────────────────────────────────────

    def get_table_counts(self) -> dict[str, int]:
        """Get record counts for all SDE tables (for diagnostics)."""
        counts: dict[str, int] = {}
        try:
            tables = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            for t in tables:
                name = t["name"]
                row = self.conn.execute(f"SELECT COUNT(*) as cnt FROM {name}").fetchone()
                counts[name] = row["cnt"] if row else 0
        except sqlite3.OperationalError:
            pass
        return counts

    # ── Skill Explorer ──────────────────────────────────────────

    def get_types_requiring_skill(self, skill_type_id: int) -> list[dict[str, Any]]:
        """Find all types that require a given skill (via dogma attributes).

        In EVE, skill requirements are stored as dogma attribute pairs:
        - requiredSkill1..6 (attr IDs 182,183,184,1285,1289,1290) = skill type_id
        - requiredSkill1Level..6Level (attr IDs 277,278,279,1286,1287,1288) = required level

        Returns list of dicts with type_id, type_name, group_name, category_name,
        required_level for each item that needs the skill.
        """
        skill_attr_ids = [182, 183, 184, 1285, 1289, 1290]  # requiredSkill1..6
        level_attr_ids = [277, 278, 279, 1286, 1287, 1288]  # corresponding levels

        results = []
        for skill_attr_id, level_attr_id in zip(skill_attr_ids, level_attr_ids):
            rows = self._get_rows(
                """SELECT DISTINCT t.type_id, t.name_en AS type_name,
                          g.name_en AS group_name, c.name_en AS category_name,
                          lvl.value AS required_level
                   FROM type_dogma_attributes tda
                   JOIN types t ON tda.type_id = t.type_id AND t.published = 1
                   LEFT JOIN groups g ON t.group_id = g.group_id
                   LEFT JOIN categories c ON g.category_id = c.category_id
                   LEFT JOIN type_dogma_attributes lvl
                       ON lvl.type_id = t.type_id AND lvl.attribute_id = ?
                   WHERE tda.attribute_id = ? AND CAST(tda.value AS INTEGER) = ?""",
                (level_attr_id, skill_attr_id, skill_type_id),
            )
            results.extend(rows)

        # Deduplicate by type_id (keep highest required level)
        by_type: dict[int, dict] = {}
        for r in results:
            tid = r["type_id"]
            if tid not in by_type or (r.get("required_level") or 0) > (by_type[tid].get("required_level") or 0):
                by_type[tid] = r
        return sorted(by_type.values(), key=lambda x: (x.get("category_name", ""), x.get("group_name", ""), x.get("type_name", "")))

    # ── Lifecycle ───────────────────────────────────────────────

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


# ── Helpers ─────────────────────────────────────────────────────────

def _roman(n: int) -> str:
    """Convert small integer to Roman numeral (for planet names)."""
    if n <= 0 or n > 20:
        return str(n)
    vals = [
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    result = ""
    for val, numeral in vals:
        while n >= val:
            result += numeral
            n -= val
    return result
