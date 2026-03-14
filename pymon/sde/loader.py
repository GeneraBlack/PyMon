"""SDE JSONL file loader – imports EVE static data into SQLite.

Processes **all** JSONL files from the EVE Static Data Export and stores
them in a local SQLite database for fast lookups.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path
from typing import Any

import orjson

logger = logging.getLogger(__name__)


# ── Which JSONL files to import and their table schemas ─────────────
# Each entry maps a SQLite table name to:
#   file     – the JSONL filename
#   columns  – list of (column_name, SQL_type, json_path)
#              json_path supports dotted notation and special "_key"
#   post_import – optional list of custom SQL INSERT callbacks (table name)
#                 for data that needs special handling (1:N nested arrays)
#
# Tables whose source rows contain nested arrays that need to be
# flattened into separate child tables are handled via
# CHILD_TABLES further below.

SDE_TABLES: dict[str, dict[str, Any]] = {
    # ── Core item data ──────────────────────────────────────────
    "types": {
        "file": "types.jsonl",
        "columns": [
            ("type_id", "INTEGER PRIMARY KEY", "_key"),
            ("group_id", "INTEGER", "groupID"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("description_en", "TEXT", "description.en"),
            ("mass", "REAL", "mass"),
            ("volume", "REAL", "volume"),
            ("base_price", "REAL", "basePrice"),
            ("portion_size", "INTEGER", "portionSize"),
            ("published", "INTEGER", "published"),
            ("market_group_id", "INTEGER", "marketGroupID"),
            ("race_id", "INTEGER", "raceID"),
            ("icon_id", "INTEGER", "iconID"),
        ],
    },
    "groups": {
        "file": "groups.jsonl",
        "columns": [
            ("group_id", "INTEGER PRIMARY KEY", "_key"),
            ("category_id", "INTEGER", "categoryID"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("published", "INTEGER", "published"),
            ("icon_id", "INTEGER", "iconID"),
            ("anchorable", "INTEGER", "anchorable"),
            ("anchored", "INTEGER", "anchored"),
            ("use_base_price", "INTEGER", "useBasePrice"),
            ("fittable_non_singleton", "INTEGER", "fittableNonSingleton"),
        ],
    },
    "categories": {
        "file": "categories.jsonl",
        "columns": [
            ("category_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("published", "INTEGER", "published"),
            ("icon_id", "INTEGER", "iconID"),
        ],
    },
    # ── Map data ────────────────────────────────────────────────
    "map_solar_systems": {
        "file": "mapSolarSystems.jsonl",
        "columns": [
            ("system_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("region_id", "INTEGER", "regionID"),
            ("constellation_id", "INTEGER", "constellationID"),
            ("security_status", "REAL", "securityStatus"),
            ("security_class", "TEXT", "securityClass"),
            ("border", "INTEGER", "border"),
            ("hub", "INTEGER", "hub"),
            ("international", "INTEGER", "international"),
            ("luminosity", "REAL", "luminosity"),
        ],
    },
    "map_regions": {
        "file": "mapRegions.jsonl",
        "columns": [
            ("region_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("faction_id", "INTEGER", "factionID"),
        ],
    },
    "map_constellations": {
        "file": "mapConstellations.jsonl",
        "columns": [
            ("constellation_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("region_id", "INTEGER", "regionID"),
            ("faction_id", "INTEGER", "factionID"),
        ],
    },
    "map_planets": {
        "file": "mapPlanets.jsonl",
        "columns": [
            ("planet_id", "INTEGER PRIMARY KEY", "_key"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("celestial_index", "INTEGER", "celestialIndex"),
            ("radius", "REAL", "radius"),
            ("type_id", "INTEGER", "typeID"),
        ],
    },
    "map_moons": {
        "file": "mapMoons.jsonl",
        "columns": [
            ("moon_id", "INTEGER PRIMARY KEY", "_key"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("celestial_index", "INTEGER", "celestialIndex"),
            ("orbit_index", "INTEGER", "orbitIndex"),
            ("orbit_id", "INTEGER", "orbitID"),
            ("radius", "REAL", "radius"),
            ("type_id", "INTEGER", "typeID"),
        ],
    },
    "map_stargates": {
        "file": "mapStargates.jsonl",
        "columns": [
            ("stargate_id", "INTEGER PRIMARY KEY", "_key"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("type_id", "INTEGER", "typeID"),
            ("dest_system_id", "INTEGER", "destination.solarSystemID"),
            ("dest_stargate_id", "INTEGER", "destination.stargateID"),
        ],
    },
    "map_stars": {
        "file": "mapStars.jsonl",
        "columns": [
            ("star_id", "INTEGER PRIMARY KEY", "_key"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("type_id", "INTEGER", "typeID"),
            ("radius", "INTEGER", "radius"),
            ("luminosity", "REAL", "statistics.luminosity"),
            ("spectral_class", "TEXT", "statistics.spectralClass"),
            ("temperature", "REAL", "statistics.temperature"),
        ],
    },
    "map_asteroid_belts": {
        "file": "mapAsteroidBelts.jsonl",
        "columns": [
            ("belt_id", "INTEGER PRIMARY KEY", "_key"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("celestial_index", "INTEGER", "celestialIndex"),
            ("orbit_index", "INTEGER", "orbitIndex"),
        ],
    },
    "map_secondary_suns": {
        "file": "mapSecondarySuns.jsonl",
        "columns": [
            ("secondary_sun_id", "INTEGER PRIMARY KEY", "_key"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("type_id", "INTEGER", "typeID"),
            ("effect_beacon_type_id", "INTEGER", "effectBeaconTypeID"),
        ],
    },
    "map_landmarks": {
        "file": "landmarks.jsonl",
        "columns": [
            ("landmark_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("description_en", "TEXT", "description.en"),
        ],
    },
    # ── Market & economy ────────────────────────────────────────
    "market_groups": {
        "file": "marketGroups.jsonl",
        "columns": [
            ("market_group_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("description_en", "TEXT", "description.en"),
            ("parent_group_id", "INTEGER", "parentGroupID"),
            ("has_types", "INTEGER", "hasTypes"),
            ("icon_id", "INTEGER", "iconID"),
        ],
    },
    "meta_groups": {
        "file": "metaGroups.jsonl",
        "columns": [
            ("meta_group_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
        ],
    },
    # ── Factions, races, bloodlines, ancestries ─────────────────
    "factions": {
        "file": "factions.jsonl",
        "columns": [
            ("faction_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("description_en", "TEXT", "description.en"),
            ("corporation_id", "INTEGER", "corporationID"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("militia_corporation_id", "INTEGER", "militiaCorporationID"),
        ],
    },
    "races": {
        "file": "races.jsonl",
        "columns": [
            ("race_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("description_en", "TEXT", "description.en"),
            ("icon_id", "INTEGER", "iconID"),
        ],
    },
    "bloodlines": {
        "file": "bloodlines.jsonl",
        "columns": [
            ("bloodline_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("description_en", "TEXT", "description.en"),
            ("race_id", "INTEGER", "raceID"),
            ("corporation_id", "INTEGER", "corporationID"),
            ("charisma", "INTEGER", "charisma"),
            ("intelligence", "INTEGER", "intelligence"),
            ("memory", "INTEGER", "memory"),
            ("perception", "INTEGER", "perception"),
            ("willpower", "INTEGER", "willpower"),
            ("icon_id", "INTEGER", "iconID"),
        ],
    },
    "ancestries": {
        "file": "ancestries.jsonl",
        "columns": [
            ("ancestry_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("description_en", "TEXT", "description.en"),
            ("bloodline_id", "INTEGER", "bloodlineID"),
            ("charisma", "INTEGER", "charisma"),
            ("intelligence", "INTEGER", "intelligence"),
            ("memory", "INTEGER", "memory"),
            ("perception", "INTEGER", "perception"),
            ("willpower", "INTEGER", "willpower"),
            ("icon_id", "INTEGER", "iconID"),
        ],
    },
    # ── NPC data ────────────────────────────────────────────────
    "npc_corporations": {
        "file": "npcCorporations.jsonl",
        "columns": [
            ("corporation_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("ceo_id", "INTEGER", "ceoID"),
            ("faction_id", "INTEGER", "factionID"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("station_id", "INTEGER", "stationID"),
            ("deleted", "INTEGER", "deleted"),
            ("icon_id", "INTEGER", "iconID"),
        ],
    },
    "npc_characters": {
        "file": "npcCharacters.jsonl",
        "columns": [
            ("character_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("corporation_id", "INTEGER", "corporationID"),
            ("bloodline_id", "INTEGER", "bloodlineID"),
            ("race_id", "INTEGER", "raceID"),
            ("gender", "INTEGER", "gender"),
            ("ceo", "INTEGER", "ceo"),
            ("location_id", "INTEGER", "locationID"),
        ],
    },
    "npc_corporation_divisions": {
        "file": "npcCorporationDivisions.jsonl",
        "columns": [
            ("division_id", "INTEGER PRIMARY KEY", "_key"),
            ("display_name", "TEXT", "displayName"),
            ("internal_name", "TEXT", "internalName"),
            ("leader_type_en", "TEXT", "leaderTypeName.en"),
        ],
    },
    "npc_stations": {
        "file": "npcStations.jsonl",
        "columns": [
            ("station_id", "INTEGER PRIMARY KEY", "_key"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("owner_id", "INTEGER", "ownerID"),
            ("type_id", "INTEGER", "typeID"),
            ("operation_id", "INTEGER", "operationID"),
            ("reprocessing_efficiency", "REAL", "reprocessingEfficiency"),
            ("reprocessing_stations_take", "REAL", "reprocessingStationsTake"),
        ],
    },
    "agents_in_space": {
        "file": "agentsInSpace.jsonl",
        "columns": [
            ("agent_id", "INTEGER PRIMARY KEY", "_key"),
            ("solar_system_id", "INTEGER", "solarSystemID"),
            ("type_id", "INTEGER", "typeID"),
            ("dungeon_id", "INTEGER", "dungeonID"),
        ],
    },
    "agent_types": {
        "file": "agentTypes.jsonl",
        "columns": [
            ("agent_type_id", "INTEGER PRIMARY KEY", "_key"),
            ("name", "TEXT", "name"),
        ],
    },
    # ── Dogma (attributes, effects, units) ──────────────────────
    "dogma_attributes": {
        "file": "dogmaAttributes.jsonl",
        "columns": [
            ("attribute_id", "INTEGER PRIMARY KEY", "_key"),
            ("name", "TEXT", "name"),
            ("display_name_en", "TEXT", "displayName.en"),
            ("description_en", "TEXT", "description.en"),
            ("attribute_category_id", "INTEGER", "attributeCategoryID"),
            ("data_type", "INTEGER", "dataType"),
            ("default_value", "REAL", "defaultValue"),
            ("unit_id", "INTEGER", "unitID"),
            ("high_is_good", "INTEGER", "highIsGood"),
            ("stackable", "INTEGER", "stackable"),
            ("published", "INTEGER", "published"),
        ],
    },
    "dogma_attribute_categories": {
        "file": "dogmaAttributeCategories.jsonl",
        "columns": [
            ("category_id", "INTEGER PRIMARY KEY", "_key"),
            ("name", "TEXT", "name"),
            ("description", "TEXT", "description"),
        ],
    },
    "dogma_effects": {
        "file": "dogmaEffects.jsonl",
        "columns": [
            ("effect_id", "INTEGER PRIMARY KEY", "_key"),
            ("name", "TEXT", "name"),
            ("guid", "TEXT", "guid"),
            ("effect_category_id", "INTEGER", "effectCategoryID"),
            ("discharge_attribute_id", "INTEGER", "dischargeAttributeID"),
            ("duration_attribute_id", "INTEGER", "durationAttributeID"),
            ("is_assistance", "INTEGER", "isAssistance"),
            ("is_offensive", "INTEGER", "isOffensive"),
            ("is_warp_safe", "INTEGER", "isWarpSafe"),
            ("published", "INTEGER", "published"),
        ],
    },
    "dogma_units": {
        "file": "dogmaUnits.jsonl",
        "columns": [
            ("unit_id", "INTEGER PRIMARY KEY", "_key"),
            ("name", "TEXT", "name"),
            ("display_name_en", "TEXT", "displayName.en"),
            ("description_en", "TEXT", "description.en"),
        ],
    },
    # ── Blueprints ──────────────────────────────────────────────
    "blueprints": {
        "file": "blueprints.jsonl",
        "columns": [
            ("blueprint_type_id", "INTEGER PRIMARY KEY", "_key"),
            ("max_production_limit", "INTEGER", "maxProductionLimit"),
            ("manufacturing_time", "INTEGER", "activities.manufacturing.time"),
            ("copying_time", "INTEGER", "activities.copying.time"),
            ("research_material_time", "INTEGER", "activities.research_material.time"),
            ("research_time_time", "INTEGER", "activities.research_time.time"),
            ("invention_time", "INTEGER", "activities.invention.time"),
            ("reaction_time", "INTEGER", "activities.reaction.time"),
        ],
    },
    # ── Character attributes ────────────────────────────────────
    "character_attributes": {
        "file": "characterAttributes.jsonl",
        "columns": [
            ("attribute_id", "INTEGER PRIMARY KEY", "_key"),
            ("description", "TEXT", "description"),
            ("icon_id", "INTEGER", "iconID"),
            ("name", "TEXT", "shortDescription"),
        ],
    },
    # ── Certificates ────────────────────────────────────────────
    "certificates": {
        "file": "certificates.jsonl",
        "columns": [
            ("certificate_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("description_en", "TEXT", "description.en"),
            ("group_id", "INTEGER", "groupID"),
        ],
    },
    # ── Clone grades ────────────────────────────────────────────
    "clone_grades": {
        "file": "cloneGrades.jsonl",
        "columns": [
            ("clone_grade_id", "INTEGER PRIMARY KEY", "_key"),
            ("name", "TEXT", "name"),
        ],
    },
    # ── Corporation activities ──────────────────────────────────
    "corporation_activities": {
        "file": "corporationActivities.jsonl",
        "columns": [
            ("activity_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
        ],
    },
    # ── Planet schematics (PI) ──────────────────────────────────
    "planet_schematics": {
        "file": "planetSchematics.jsonl",
        "columns": [
            ("schematic_id", "INTEGER PRIMARY KEY", "_key"),
            ("name_en", "TEXT", "name.en"),
            ("name_de", "TEXT", "name.de"),
            ("cycle_time", "INTEGER", "cycleTime"),
        ],
    },
    "planet_resources": {
        "file": "planetResources.jsonl",
        "columns": [
            ("planet_id", "INTEGER PRIMARY KEY", "_key"),
            ("power", "INTEGER", "power"),
        ],
    },
    # ── SKINs ───────────────────────────────────────────────────
    "skins": {
        "file": "skins.jsonl",
        "columns": [
            ("skin_id", "INTEGER PRIMARY KEY", "_key"),
            ("internal_name", "TEXT", "internalName"),
            ("skin_material_id", "INTEGER", "skinMaterialID"),
            ("visible_tranquility", "INTEGER", "visibleTranquility"),
        ],
    },
    "skin_materials": {
        "file": "skinMaterials.jsonl",
        "columns": [
            ("material_id", "INTEGER PRIMARY KEY", "_key"),
            ("display_name_en", "TEXT", "displayName.en"),
            ("display_name_de", "TEXT", "displayName.de"),
        ],
    },
    "skin_licenses": {
        "file": "skinLicenses.jsonl",
        "columns": [
            ("license_type_id", "INTEGER PRIMARY KEY", "_key"),
            ("skin_id", "INTEGER", "skinID"),
            ("duration", "INTEGER", "duration"),
        ],
    },
    # ── Sovereignty ─────────────────────────────────────────────
    "sovereignty_upgrades": {
        "file": "sovereigntyUpgrades.jsonl",
        "columns": [
            ("type_id", "INTEGER PRIMARY KEY", "_key"),
            ("power_allocation", "INTEGER", "powerAllocation"),
            ("workforce_allocation", "INTEGER", "workforceAllocation"),
            ("mutually_exclusive_group", "TEXT", "mutually_exclusive_group"),
        ],
    },
    # ── Station operations & services ───────────────────────────
    "station_operations": {
        "file": "stationOperations.jsonl",
        "columns": [
            ("operation_id", "INTEGER PRIMARY KEY", "_key"),
            ("activity_id", "INTEGER", "activityID"),
            ("description_en", "TEXT", "description.en"),
            ("description_de", "TEXT", "description.de"),
        ],
    },
    "station_services": {
        "file": "stationServices.jsonl",
        "columns": [
            ("service_id", "INTEGER PRIMARY KEY", "_key"),
            ("service_name_en", "TEXT", "serviceName.en"),
            ("service_name_de", "TEXT", "serviceName.de"),
        ],
    },
    # ── Misc / lookup tables ────────────────────────────────────
    "compressible_types": {
        "file": "compressibleTypes.jsonl",
        "columns": [
            ("type_id", "INTEGER PRIMARY KEY", "_key"),
            ("compressed_type_id", "INTEGER", "compressedTypeID"),
        ],
    },
    "graphics": {
        "file": "graphics.jsonl",
        "columns": [
            ("graphic_id", "INTEGER PRIMARY KEY", "_key"),
            ("graphic_file", "TEXT", "graphicFile"),
        ],
    },
    "icons": {
        "file": "icons.jsonl",
        "columns": [
            ("icon_id", "INTEGER PRIMARY KEY", "_key"),
            ("icon_file", "TEXT", "iconFile"),
        ],
    },
    "translation_languages": {
        "file": "translationLanguages.jsonl",
        "columns": [
            ("language_code", "TEXT PRIMARY KEY", "_key"),
            ("name", "TEXT", "name"),
        ],
    },
    # ── Mercenary / Freelance (newer data) ──────────────────────
    "mercenary_operations": {
        "file": "mercenaryTacticalOperations.jsonl",
        "columns": [
            ("operation_id", "INTEGER PRIMARY KEY", "_key"),
            ("description_en", "TEXT", "description.en"),
            ("description_de", "TEXT", "description.de"),
            ("anarchy_impact", "INTEGER", "anarchy_impact"),
        ],
    },
    # ── SDE Meta ────────────────────────────────────────────────
    "sde_meta": {
        "file": "_sde.jsonl",
        "columns": [
            ("key", "TEXT PRIMARY KEY", "_key"),
            ("build_number", "INTEGER", "buildNumber"),
            ("release_date", "TEXT", "releaseDate"),
        ],
    },
}

# ── Child tables: 1:N nested arrays flattened into separate tables ──
# Each entry: parent_jsonl, table_name, parent_key_col, json_array_path,
#             child_columns [(col_name, sql_type, child_json_path)]
CHILD_TABLES: list[dict[str, Any]] = [
    # Blueprint manufacturing materials
    {
        "file": "blueprints.jsonl",
        "table": "blueprint_materials",
        "parent_key": "blueprint_type_id",
        "array_path": "activities.manufacturing.materials",
        "columns": [
            ("type_id", "INTEGER", "typeID"),
            ("quantity", "INTEGER", "quantity"),
        ],
    },
    # Blueprint manufacturing products
    {
        "file": "blueprints.jsonl",
        "table": "blueprint_products",
        "parent_key": "blueprint_type_id",
        "array_path": "activities.manufacturing.products",
        "columns": [
            ("type_id", "INTEGER", "typeID"),
            ("quantity", "INTEGER", "quantity"),
        ],
    },
    # Blueprint invention products
    {
        "file": "blueprints.jsonl",
        "table": "blueprint_invention_products",
        "parent_key": "blueprint_type_id",
        "array_path": "activities.invention.products",
        "columns": [
            ("type_id", "INTEGER", "typeID"),
            ("quantity", "INTEGER", "quantity"),
            ("probability", "REAL", "probability"),
        ],
    },
    # Blueprint invention materials
    {
        "file": "blueprints.jsonl",
        "table": "blueprint_invention_materials",
        "parent_key": "blueprint_type_id",
        "array_path": "activities.invention.materials",
        "columns": [
            ("type_id", "INTEGER", "typeID"),
            ("quantity", "INTEGER", "quantity"),
        ],
    },
    # Blueprint reaction materials
    {
        "file": "blueprints.jsonl",
        "table": "blueprint_reaction_materials",
        "parent_key": "blueprint_type_id",
        "array_path": "activities.reaction.materials",
        "columns": [
            ("type_id", "INTEGER", "typeID"),
            ("quantity", "INTEGER", "quantity"),
        ],
    },
    # Blueprint reaction products
    {
        "file": "blueprints.jsonl",
        "table": "blueprint_reaction_products",
        "parent_key": "blueprint_type_id",
        "array_path": "activities.reaction.products",
        "columns": [
            ("type_id", "INTEGER", "typeID"),
            ("quantity", "INTEGER", "quantity"),
        ],
    },
    # Type materials (reprocessing)
    {
        "file": "typeMaterials.jsonl",
        "table": "type_materials",
        "parent_key": "type_id",
        "array_path": "materials",
        "columns": [
            ("material_type_id", "INTEGER", "materialTypeID"),
            ("quantity", "INTEGER", "quantity"),
        ],
    },
    # Type dogma attributes
    {
        "file": "typeDogma.jsonl",
        "table": "type_dogma_attributes",
        "parent_key": "type_id",
        "array_path": "dogmaAttributes",
        "columns": [
            ("attribute_id", "INTEGER", "attributeID"),
            ("value", "REAL", "value"),
        ],
    },
    # Type dogma effects
    {
        "file": "typeDogma.jsonl",
        "table": "type_dogma_effects",
        "parent_key": "type_id",
        "array_path": "dogmaEffects",
        "columns": [
            ("effect_id", "INTEGER", "effectID"),
            ("is_default", "INTEGER", "isDefault"),
        ],
    },
    # Type bonuses – role bonuses
    {
        "file": "typeBonus.jsonl",
        "table": "type_role_bonuses",
        "parent_key": "type_id",
        "array_path": "roleBonuses",
        "columns": [
            ("bonus", "REAL", "bonus"),
            ("bonus_text_en", "TEXT", "bonusText.en"),
            ("importance", "INTEGER", "importance"),
        ],
    },
    # Type bonuses – trait bonuses (skill-based)
    {
        "file": "typeBonus.jsonl",
        "table": "type_trait_bonuses",
        "parent_key": "type_id",
        "array_path": "traitBonuses",  # will iterate _key => skill type
        "nested_key": True,  # special: traitBonuses is dict of arrays
        "columns": [
            ("skill_type_id", "INTEGER", "_nested_key"),
            ("bonus", "REAL", "bonus"),
            ("bonus_text_en", "TEXT", "bonusText.en"),
            ("importance", "INTEGER", "importance"),
        ],
    },
    # Contraband types → factions
    {
        "file": "contrabandTypes.jsonl",
        "table": "contraband_factions",
        "parent_key": "type_id",
        "array_path": "factions",
        "columns": [
            ("faction_id", "INTEGER", "_key"),
            ("attack_min_sec", "REAL", "attackMinSec"),
            ("confiscate_min_sec", "REAL", "confiscateMinSec"),
            ("fine_by_value", "REAL", "fineByValue"),
            ("standing_loss", "REAL", "standingLoss"),
        ],
    },
    # Planet schematic types (inputs/outputs)
    {
        "file": "planetSchematics.jsonl",
        "table": "planet_schematic_types",
        "parent_key": "schematic_id",
        "array_path": "types",
        "columns": [
            ("type_id", "INTEGER", "typeID"),
            ("quantity", "INTEGER", "quantity"),
            ("is_input", "INTEGER", "isInput"),
        ],
    },
    # Control tower resources
    {
        "file": "controlTowerResources.jsonl",
        "table": "control_tower_resources",
        "parent_key": "type_id",
        "array_path": "resources",
        "columns": [
            ("resource_type_id", "INTEGER", "resourceTypeID"),
            ("purpose", "INTEGER", "purpose"),
            ("quantity", "INTEGER", "quantity"),
        ],
    },
    # Dynamic item attributes (abyssal mutaplasmids)
    {
        "file": "dynamicItemAttributes.jsonl",
        "table": "dynamic_item_attributes",
        "parent_key": "type_id",
        "array_path": "attributeIDs",
        "columns": [
            ("attribute_id", "INTEGER", "_key"),
            ("min_value", "REAL", "min"),
            ("max_value", "REAL", "max"),
        ],
    },
    # Skin types
    {
        "file": "skins.jsonl",
        "table": "skin_types",
        "parent_key": "skin_id",
        "array_path": "types",
        "is_simple_array": True,  # array of plain ints, not dicts
        "columns": [
            ("type_id", "INTEGER", "_value"),
        ],
    },
    # Dbuff collections modifiers
    {
        "file": "dbuffCollections.jsonl",
        "table": "dbuff_item_modifiers",
        "parent_key": "collection_id",
        "array_path": "itemModifiers",
        "columns": [
            ("dogma_attribute_id", "INTEGER", "dogmaAttributeID"),
        ],
    },
    # Certificate skill requirements per mastery level
    {
        "file": "certificates.jsonl",
        "table": "certificate_skills",
        "parent_key": "certificate_id",
        "array_path": "skillTypes",
        "columns": [
            ("skill_type_id", "INTEGER", "_key"),
            ("basic", "INTEGER", "basic"),
            ("standard", "INTEGER", "standard"),
            ("improved", "INTEGER", "improved"),
            ("advanced", "INTEGER", "advanced"),
            ("elite", "INTEGER", "elite"),
        ],
    },
    # Certificate recommended ship types
    {
        "file": "certificates.jsonl",
        "table": "certificate_recommended_types",
        "parent_key": "certificate_id",
        "array_path": "recommendedFor",
        "is_simple_array": True,
        "columns": [
            ("type_id", "INTEGER", "_value"),
        ],
    },
]


def _resolve_nested(data: dict[str, Any], path: str) -> Any:
    """Resolve a dotted path in a nested dict (e.g., 'name.en')."""
    parts = path.split(".")
    current: Any = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _import_child_tables(
    conn: sqlite3.Connection, sde_dir: Path
) -> None:
    """Import child tables that flatten nested arrays from JSONL records."""
    # Group child table definitions by source file to avoid re-reading
    by_file: dict[str, list[dict[str, Any]]] = {}
    for ct in CHILD_TABLES:
        by_file.setdefault(ct["file"], []).append(ct)

    for jsonl_name, child_defs in by_file.items():
        jsonl_file = sde_dir / jsonl_name
        if not jsonl_file.exists():
            logger.warning("SDE file not found for child tables: %s", jsonl_file)
            continue

        # Prepare all child tables for this file
        for ct in child_defs:
            pk_col = ct["parent_key"]
            cols = [(pk_col, "INTEGER")] + [(c[0], c[1]) for c in ct["columns"]]
            col_defs = ", ".join(f"{c[0]} {c[1]}" for c in cols)
            conn.execute(f"DROP TABLE IF EXISTS {ct['table']}")
            conn.execute(f"CREATE TABLE {ct['table']} ({col_defs})")

        # Read the file once, populate all child tables from it
        batches: dict[str, list[tuple[Any, ...]]] = {ct["table"]: [] for ct in child_defs}
        counts: dict[str, int] = {ct["table"]: 0 for ct in child_defs}

        with open(jsonl_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = orjson.loads(line)
                except Exception:
                    continue

                parent_key = record.get("_key")

                for ct in child_defs:
                    arr = _resolve_nested(record, ct["array_path"])
                    if arr is None:
                        continue

                    is_simple = ct.get("is_simple_array", False)
                    nested_key = ct.get("nested_key", False)

                    if nested_key and isinstance(arr, dict):
                        # Dict of arrays: {skill_type_id: [bonus, ...]}
                        for nk, items in arr.items():
                            if not isinstance(items, list):
                                continue
                            for item in items:
                                if not isinstance(item, dict):
                                    continue
                                row_vals: list[Any] = [parent_key]
                                for col in ct["columns"]:
                                    if col[2] == "_nested_key":
                                        row_vals.append(int(nk))
                                    else:
                                        row_vals.append(
                                            _resolve_nested(item, col[2])
                                        )
                                batches[ct["table"]].append(tuple(row_vals))
                                counts[ct["table"]] += 1
                    elif is_simple and isinstance(arr, list):
                        for val in arr:
                            batches[ct["table"]].append((parent_key, val))
                            counts[ct["table"]] += 1
                    elif isinstance(arr, list):
                        for item in arr:
                            if not isinstance(item, dict):
                                continue
                            row_vals2: list[Any] = [parent_key]
                            for col in ct["columns"]:
                                row_vals2.append(
                                    _resolve_nested(item, col[2])
                                )
                            batches[ct["table"]].append(tuple(row_vals2))
                            counts[ct["table"]] += 1

                    # Flush in batches
                    if len(batches[ct["table"]]) >= 5000:
                        pk_col2 = ct["parent_key"]
                        col_names = ", ".join(
                            [pk_col2] + [c[0] for c in ct["columns"]]
                        )
                        ph = ", ".join(
                            "?" for _ in range(1 + len(ct["columns"]))
                        )
                        conn.executemany(
                            f"INSERT OR REPLACE INTO {ct['table']} ({col_names}) VALUES ({ph})",
                            batches[ct["table"]],
                        )
                        batches[ct["table"]].clear()

        # Flush remaining
        for ct in child_defs:
            if batches[ct["table"]]:
                pk_col3 = ct["parent_key"]
                col_names = ", ".join(
                    [pk_col3] + [c[0] for c in ct["columns"]]
                )
                ph = ", ".join("?" for _ in range(1 + len(ct["columns"])))
                conn.executemany(
                    f"INSERT OR REPLACE INTO {ct['table']} ({col_names}) VALUES ({ph})",
                    batches[ct["table"]],
                )
            conn.commit()
            logger.info(
                "Imported %d records into %s", counts[ct["table"]], ct["table"]
            )


def _import_masteries(
    conn: sqlite3.Connection, sde_dir: Path
) -> None:
    """Import masteries.jsonl into a flat mastery_certificates table.

    Each JSONL row: {_key: ship_type_id, _value: [{_key: level(0-4), _value: [cert_id, ...]}]}
    Flattened into: (type_id, mastery_level, certificate_id)
    """
    jsonl_file = sde_dir / "masteries.jsonl"
    if not jsonl_file.exists():
        logger.warning("SDE file not found: %s", jsonl_file)
        return

    conn.execute("DROP TABLE IF EXISTS mastery_certificates")
    conn.execute(
        "CREATE TABLE mastery_certificates ("
        "type_id INTEGER, mastery_level INTEGER, certificate_id INTEGER)"
    )

    batch: list[tuple[int, int, int]] = []
    count = 0

    with open(jsonl_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = orjson.loads(line)
            except Exception:
                continue

            type_id = record.get("_key")
            levels = record.get("_value", [])
            if not isinstance(levels, list):
                continue

            for level_entry in levels:
                if not isinstance(level_entry, dict):
                    continue
                mastery_level = level_entry.get("_key", 0)
                cert_ids = level_entry.get("_value", [])
                if not isinstance(cert_ids, list):
                    continue
                for cert_id in cert_ids:
                    batch.append((type_id, mastery_level, cert_id))
                    count += 1

                    if len(batch) >= 5000:
                        conn.executemany(
                            "INSERT INTO mastery_certificates (type_id, mastery_level, certificate_id) "
                            "VALUES (?, ?, ?)",
                            batch,
                        )
                        batch.clear()

    if batch:
        conn.executemany(
            "INSERT INTO mastery_certificates (type_id, mastery_level, certificate_id) "
            "VALUES (?, ?, ?)",
            batch,
        )
    conn.commit()
    logger.info("Imported %d records into mastery_certificates", count)


def import_sde(sde_dir: str | Path, db_path: str | Path) -> None:
    """Import SDE JSONL files into a SQLite database.

    Args:
        sde_dir: Path to the directory containing JSONL files.
        db_path: Path to the SQLite database to create/update.
    """
    sde_dir = Path(sde_dir)
    db_path = Path(db_path)

    logger.info("Importing SDE from %s into %s", sde_dir, db_path)
    start_time = time.time()

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=OFF")

    # ── Phase 1: flat tables ────────────────────────────────────
    for table_name, schema in SDE_TABLES.items():
        jsonl_file = sde_dir / schema["file"]
        if not jsonl_file.exists():
            logger.warning("SDE file not found: %s", jsonl_file)
            continue

        columns = schema["columns"]
        col_defs = ", ".join(f"{col[0]} {col[1]}" for col in columns)
        col_names = ", ".join(col[0] for col in columns)
        placeholders = ", ".join("?" for _ in columns)

        # Create table
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(f"CREATE TABLE {table_name} ({col_defs})")

        # Import data
        batch: list[tuple[Any, ...]] = []
        count = 0

        with open(jsonl_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = orjson.loads(line)
                except Exception:
                    continue

                row = tuple(_resolve_nested(record, col[2]) for col in columns)
                batch.append(row)
                count += 1

                if len(batch) >= 5000:
                    conn.executemany(
                        f"INSERT OR REPLACE INTO {table_name} ({col_names}) VALUES ({placeholders})",
                        batch,
                    )
                    batch.clear()

        if batch:
            conn.executemany(
                f"INSERT OR REPLACE INTO {table_name} ({col_names}) VALUES ({placeholders})",
                batch,
            )

        conn.commit()
        logger.info("Imported %d records into %s", count, table_name)

    # ── Phase 2: child tables (nested arrays) ───────────────────
    _import_child_tables(conn, sde_dir)

    # ── Phase 2b: masteries (special nested structure) ──────────
    _import_masteries(conn, sde_dir)

    # ── Phase 3: indexes ────────────────────────────────────────
    indexes = [
        ("idx_types_group", "types", "group_id"),
        ("idx_types_market", "types", "market_group_id"),
        ("idx_types_published", "types", "published"),
        ("idx_types_race", "types", "race_id"),
        ("idx_groups_category", "groups", "category_id"),
        ("idx_systems_region", "map_solar_systems", "region_id"),
        ("idx_systems_constellation", "map_solar_systems", "constellation_id"),
        ("idx_constellations_region", "map_constellations", "region_id"),
        ("idx_planets_system", "map_planets", "solar_system_id"),
        ("idx_moons_system", "map_moons", "solar_system_id"),
        ("idx_stargates_system", "map_stargates", "solar_system_id"),
        ("idx_stars_system", "map_stars", "solar_system_id"),
        ("idx_belts_system", "map_asteroid_belts", "solar_system_id"),
        ("idx_stations_system", "npc_stations", "solar_system_id"),
        ("idx_stations_owner", "npc_stations", "owner_id"),
        ("idx_npc_corps_faction", "npc_corporations", "faction_id"),
        ("idx_npc_chars_corp", "npc_characters", "corporation_id"),
        ("idx_bloodlines_race", "bloodlines", "race_id"),
        ("idx_ancestries_bloodline", "ancestries", "bloodline_id"),
        ("idx_factions_corp", "factions", "corporation_id"),
        ("idx_market_groups_parent", "market_groups", "parent_group_id"),
        ("idx_bp_materials_bp", "blueprint_materials", "blueprint_type_id"),
        ("idx_bp_products_bp", "blueprint_products", "blueprint_type_id"),
        ("idx_type_materials_type", "type_materials", "type_id"),
        ("idx_type_dogma_attrs_type", "type_dogma_attributes", "type_id"),
        ("idx_type_dogma_effects_type", "type_dogma_effects", "type_id"),
        ("idx_skin_licenses_skin", "skin_licenses", "skin_id"),
        ("idx_skin_types_skin", "skin_types", "skin_id"),
        ("idx_contraband_type", "contraband_factions", "type_id"),
        ("idx_schematic_types_sch", "planet_schematic_types", "schematic_id"),
        ("idx_cert_skills_cert", "certificate_skills", "certificate_id"),
        ("idx_cert_skills_skill", "certificate_skills", "skill_type_id"),
        ("idx_cert_rec_types_cert", "certificate_recommended_types", "certificate_id"),
        ("idx_cert_rec_types_type", "certificate_recommended_types", "type_id"),
        ("idx_mastery_certs_type", "mastery_certificates", "type_id"),
        ("idx_mastery_certs_cert", "mastery_certificates", "certificate_id"),
    ]
    for idx_name, tbl, col in indexes:
        try:
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS {idx_name} ON {tbl}({col})"
            )
        except sqlite3.OperationalError as e:
            logger.debug("Index %s skipped: %s", idx_name, e)
    conn.commit()

    conn.close()

    elapsed = time.time() - start_time
    logger.info("SDE import completed in %.1f seconds", elapsed)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import EVE SDE JSONL into SQLite")
    parser.add_argument("--sde-dir", required=True, help="Path to SDE JSONL directory")
    parser.add_argument("--db-path", default="sde.db", help="Output SQLite database path")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    import_sde(args.sde_dir, args.db_path)
