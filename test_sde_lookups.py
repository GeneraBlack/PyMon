"""Quick verification of all SDE lookup methods."""
from pathlib import Path
from pymon.sde.database import SDEDatabase

db = SDEDatabase(Path(r"C:\Users\Gener\AppData\Local\PyMon\PyMon\sde.db"))

print(f"=== SDE Build: {db.get_build_number()}, Released: {db.get_release_date()} ===\n")

# Type lookups
print(f"Type 587 (Rifter): {db.get_type_name(587)}")
print(f"Type 587 (DE): {db.get_type_name(587, 'de')}")
print(f"Type info: {db.get_type(587) is not None}")
print(f"Search 'Rifter': {len(db.search_types('Rifter'))} results")
print(f"Types in group 25: {len(db.get_types_by_group(25))} types")

# Group / Category
g = db.get_group(25)
print(f"\nGroup 25: {db.get_group_name(25)} (cat: {g['category_id'] if g else '?'})")
print(f"Category 6: {db.get_category_name(6)}")
cat = db.get_category_for_type(587)
print(f"Category for Rifter: {cat['name_en'] if cat else '?'}")

# Map
print(f"\nSystem 30000142 (Jita): {db.get_system_name(30000142)}")
print(f"Security: {db.get_security_status(30000142):.1f}")
sys_info = db.get_system(30000142)
print(f"Region for Jita: {db.get_region_name(sys_info['region_id']) if sys_info else '?'}")
print(f"Constellation: {db.get_constellation_name(sys_info['constellation_id']) if sys_info else '?'}")
print(f"Regions total: {len(db.get_all_regions())}")
print(f"Constellations in Forge: {len(db.get_constellations_in_region(10000002))}")
print(f"Systems in Kimotoro: {len(db.get_systems_in_constellation(20000020))}")

# Planets, Moons
planets = db.get_planets_in_system(30000142)
print(f"\nPlanets in Jita: {len(planets)}")
if planets:
    print(f"  Planet name: {db.get_planet_name(planets[0]['planet_id'])}")
moons = db.get_moons_in_system(30000142)
print(f"Moons in Jita: {len(moons)}")
if moons:
    print(f"  Moon name: {db.get_moon_name(moons[0]['moon_id'])}")

# Stars
star = db.get_star(30000142)
print(f"Star in Jita: spectral={star['spectral_class'] if star else '?'}")

# Stations
print(f"\nStation 60003760: {db.get_station_name(60003760)}")
stations_jita = db.get_stations_in_system(30000142)
print(f"Stations in Jita: {len(stations_jita)}")

# Factions
print(f"\nFaction 500001 (Caldari): {db.get_faction_name(500001)}")
print(f"Factions total: {len(db.get_all_factions())}")

# Races
print(f"Race 1 (Caldari): {db.get_race_name(1)}")
print(f"Races total: {len(db.get_all_races())}")

# Bloodlines
print(f"Bloodline 1: {db.get_bloodline_name(1)}")
bls = db.get_bloodlines_for_race(1)
print(f"Caldari bloodlines: {[db.get_bloodline_name(b['bloodline_id']) for b in bls]}")

# Ancestries
print(f"Ancestry 1: {db.get_ancestry_name(1)}")

# NPC Corporations
print(f"\nNPC Corp 1000035: {db.get_npc_corporation_name(1000035)}")
caldari_corps = db.get_npc_corporations_for_faction(500001)
print(f"Caldari NPC corps: {len(caldari_corps)}")

# NPC Characters
print(f"NPC Char 3000001: {db.get_npc_character_name(3000001)}")

# Meta Groups
print(f"\nMeta group 1: {db.get_meta_group_name(1)}")
print(f"Meta group 2: {db.get_meta_group_name(2)}")

# Dogma
attr = db.get_dogma_attribute(37)
print(f"\nDogma attr 37: {attr['display_name_en'] if attr else '?'}")
print(f"Dogma attr name: {db.get_dogma_attribute_name(37)}")
eff = db.get_dogma_effect(4)
print(f"Dogma effect 4: {eff['name'] if eff else '?'}")
unit = db.get_dogma_unit(1)
print(f"Dogma unit 1: {db.get_dogma_unit_name(1)}")
print(f"Type dogma attrs for Rifter: {len(db.get_type_dogma_attributes(587))} attrs")
print(f"Type dogma effects for Rifter: {len(db.get_type_dogma_effects(587))} effects")

# Blueprints
bp = db.get_blueprint(681)
print(f"\nBlueprint 681: mfg_time={bp['manufacturing_time'] if bp else '?'}s")
mats = db.get_blueprint_materials(681)
print(f"  Materials: {[(m['type_name'], m['quantity']) for m in mats]}")
prods = db.get_blueprint_products(681)
print(f"  Products: {[(p['type_name'], p['quantity']) for p in prods]}")
bp_for = db.get_blueprint_for_product(587)
print(f"  Blueprint for Rifter: type_id={bp_for['blueprint_type_id'] if bp_for else '?'}")

# Type materials (reprocessing)
repro = db.get_type_materials(587)
print(f"Reprocessing Rifter: {len(repro)} materials")

# Ship bonuses
role_b = db.get_type_role_bonuses(587)
print(f"Rifter role bonuses: {len(role_b)}")
trait_b = db.get_type_trait_bonuses(587)
print(f"Rifter trait bonuses: {len(trait_b)}")

# Certificates
cert = db.get_certificate(50)
print(f"\nCertificate 50: {db.get_certificate_name(50)}")

# PI
sch = db.get_planet_schematic(65)
print(f"PI Schematic 65: {db.get_planet_schematic_name(65)}")
sch_types = db.get_planet_schematic_types(65)
print(f"  Types: {[(t['type_name'], t['is_input']) for t in sch_types[:3]]}")

# Compressed types
comp = db.get_compressed_type(1230)  # Veldspar
print(f"\nCompressed Veldspar: type_id={comp}")

# Entity name resolution
print(f"\nResolve 500001 (faction): {db.resolve_npc_entity_name(500001)}")
print(f"Resolve 1000035 (corp): {db.resolve_npc_entity_name(1000035)}")
print(f"Resolve 3000001 (npc): {db.resolve_npc_entity_name(3000001)}")
print(f"Resolve 99999999 (unknown): {db.resolve_npc_entity_name(99999999)}")

# Contraband
print(f"\nIs type 3713 contraband? {db.is_contraband(3713)}")
cf = db.get_contraband_factions(3713)
print(f"  Factions: {[(c.get('faction_name', '?'), c['standing_loss']) for c in cf]}")

# SKINs
skins = db.get_skins_for_type(587)  # Rifter skins
print(f"\nSKINs for Rifter: {len(skins)}")

# Table counts
counts = db.get_table_counts()
print(f"\n=== Total tables: {len(counts)}, total records: {sum(counts.values()):,} ===")
for name, cnt in sorted(counts.items()):
    print(f"  {name}: {cnt:,}")

db.close()
print("\n✅ All lookups passed!")
