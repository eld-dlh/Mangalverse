import pyogrio
from pathlib import Path

gdb = "data/originals/geology/sim3464_extracted/sim3464_JezeroNili_FINAL/Geodatabase/Nili.gdb"
layers = pyogrio.list_layers(gdb)

print("--- ALL FEATURE CLASSES IN Nili.gdb ---")
for name, geom_type in layers:
    info = pyogrio.read_info(gdb, layer=name)
    print(f"  {name:20s}: {geom_type:15s} ({info['features']} features)")

meta, _, geoms, field_data = pyogrio.raw.read(gdb, layer="GeoUnits_v1")
field_names = list(meta["fields"])
unit_idx = field_names.index("unit")
name_idx = field_names.index("name")

units = [field_data[unit_idx][i] for i in range(len(geoms)) if field_data[unit_idx][i]]
names = [field_data[name_idx][i] for i in range(len(geoms)) if field_data[name_idx][i]]
distinct_units = sorted(list(set(units)))
distinct_names = sorted(list(set(names)))

print(f"\nTotal polygon features in GeoUnits_v1: {len(geoms)}")
print(f"Distinct geological unit codes: {len(distinct_units)}")
print("Unit codes:", distinct_units)
print(f"Distinct formation names: {len(distinct_names)}")
for u in distinct_units[:10]:
    sample_name = next((names[i] for i in range(len(units)) if units[i] == u), "Unknown")
    print(f"  {u:10s}: {sample_name}")
