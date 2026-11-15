"""
Export and synchronizes prepared NASA datasets into the application runtime directory.
Allows backend API, routing algorithms, and map layers to immediately consume authentic datasets.
"""
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
RUNTIME_DIR = ROOT_DIR / "backend" / "app" / "data"

def export_datasets():
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Export CTX Regional DEM (primary routing DEM)
    src_dem = DATA_DIR / "elevation" / "ctx" / "jezero_ctx_dem.tif"
    dst_dem = RUNTIME_DIR / "jezero_crater_dem.tif"
    if src_dem.exists():
        shutil.copy2(src_dem, dst_dem)
        print(f"Exported CTX DEM -> {dst_dem}")

    # 2. Export Rover Traverse GeoJSON
    src_trav = DATA_DIR / "vector" / "traverse" / "perseverance_traverse_sols_0_1230.geojson"
    dst_trav = RUNTIME_DIR / "nasa_perseverance_traverse.geojson"
    if src_trav.exists():
        shutil.copy2(src_trav, dst_trav)
        print(f"Exported Rover Traverse GeoJSON -> {dst_trav}")

    # 3. Export Scientific Discoveries GeoJSON
    src_disc = DATA_DIR / "vector" / "discoveries" / "scientific_discoveries.geojson"
    dst_disc = RUNTIME_DIR / "scientific_discoveries.geojson"
    if src_disc.exists():
        shutil.copy2(src_disc, dst_disc)
        print(f"Exported Scientific Discoveries GeoJSON -> {dst_disc}")

    # 4. Export MEDA Environmental Summaries
    src_meda = DATA_DIR / "environmental" / "meda" / "meda_daily_summaries.json"
    dst_meda = RUNTIME_DIR / "meda_daily_summaries.json"
    if src_meda.exists():
        shutil.copy2(src_meda, dst_meda)
        print(f"Exported MEDA Summaries -> {dst_meda}")

    print("All NASA geospatial datasets exported to platform runtime successfully.")

if __name__ == "__main__":
    export_datasets()
