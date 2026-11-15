"""
Generate elevation contour lines from the authentic Jezero CTX DEM.
Outputs: data/processed/vector/jezero_contours_50m.geojson (Mars geographic CRS)

Usage:
    python scripts/generate_contours.py

Requirements: rasterio, numpy, pyproj, shapely (or skimage)
"""
import sys
import json
import math
import numpy as np
from pathlib import Path

# Project root (scripts/ is one level below project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEM_PATH = PROJECT_ROOT / "backend" / "app" / "data" / "jezero_crater_dem.tif"
OUT_DIR = PROJECT_ROOT / "data" / "processed" / "vector"
OUT_PATH = OUT_DIR / "jezero_contours_50m.geojson"

CONTOUR_INTERVAL = 50  # metres

def main():
    try:
        import rasterio
        import pyproj
    except ImportError as e:
        print(f"Missing dependency: {e}")
        sys.exit(1)

    # ── Load DEM ─────────────────────────────────────────────────────────────
    print(f"Loading DEM: {DEM_PATH}")
    if not DEM_PATH.exists():
        print(f"ERROR: DEM not found at {DEM_PATH}")
        sys.exit(1)

    with rasterio.open(DEM_PATH) as src:
        grid = src.read(1).astype(np.float64)
        transform = src.transform
        crs = src.crs
        nodata = src.nodata
        height, width = grid.shape
        bounds = src.bounds

    print(f"DEM shape: {height} x {width}, bounds: {bounds}")
    print(f"CRS: {crs}")

    # Mask nodata
    if nodata is not None:
        grid = np.where(grid == nodata, np.nan, grid)

    valid = grid[np.isfinite(grid)]
    elev_min = float(np.nanmin(valid))
    elev_max = float(np.nanmax(valid))
    print(f"Elevation range: {elev_min:.1f} m to {elev_max:.1f} m")

    # ── Setup coordinate transformer (projected → Mars geographic) ───────────
    geo_crs = pyproj.CRS.from_proj4("+proj=longlat +a=3396190 +b=3396190 +no_defs")
    if crs and str(crs) != str(geo_crs):
        transformer = pyproj.Transformer.from_crs(crs, geo_crs, always_xy=True)
    else:
        transformer = None

    def proj_to_lonlat(x, y):
        if transformer:
            return transformer.transform(x, y)
        return x, y

    # ── Generate contour levels ───────────────────────────────────────────────
    # Round min up and max down to nearest interval
    level_start = math.ceil(elev_min / CONTOUR_INTERVAL) * CONTOUR_INTERVAL
    level_end   = math.floor(elev_max / CONTOUR_INTERVAL) * CONTOUR_INTERVAL
    levels = list(range(int(level_start), int(level_end) + 1, CONTOUR_INTERVAL))
    print(f"Generating {len(levels)} contour levels at {CONTOUR_INTERVAL}m interval")

    # ── Marching squares via matplotlib (no extra deps beyond numpy) ──────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.contour import QuadContourSet
        USE_MATPLOTLIB = True
    except ImportError:
        USE_MATPLOTLIB = False

    if not USE_MATPLOTLIB:
        print("ERROR: matplotlib is required for contour generation.")
        print("Install with: pip install matplotlib")
        sys.exit(1)

    print("Running marching-squares contour extraction...")
    fig, ax = plt.subplots(1, 1)

    # matplotlib contour works on col/row index space
    rows = np.arange(height)
    cols = np.arange(width)

    cs = ax.contour(cols, rows, grid, levels=levels)
    plt.close(fig)

    # ── Convert contour paths to GeoJSON ─────────────────────────────────────
    # Support both old (.collections) and new (.allsegs / get_paths) matplotlib APIs
    features = []

    # Preferred: iterate level index and use cs.get_paths() per level (mpl >= 3.8)
    # Fallback: cs.allsegs which is always available
    all_segs = cs.allsegs  # list[list[ndarray]], indexed by level then segment

    for level_idx, level in enumerate(cs.levels):
        elev_m = float(level)
        segs = all_segs[level_idx]  # list of (N, 2) arrays in col,row space
        for seg in segs:
            if len(seg) < 2:
                continue
            coords = []
            for col, row in seg:
                x = transform.c + col * transform.a + row * transform.b
                y = transform.f + col * transform.d + row * transform.e
                lon, lat = proj_to_lonlat(x, y)
                coords.append([round(lon, 6), round(lat, 6)])
            if len(coords) < 2:
                continue
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                },
                "properties": {
                    "elevation_m": elev_m,
                    "interval_m": CONTOUR_INTERVAL,
                    "source": "USGS Mars 2020 CTX DEM 20m/pixel",
                    "datum": "MOLA Areoid (Mars)"
                }
            })

    print(f"Generated {len(features)} contour line segments")

    # ── Write GeoJSON ─────────────────────────────────────────────────────────
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    geojson = {
        "type": "FeatureCollection",
        "name": "jezero_contours_50m",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "metadata": {
            "region": "Jezero Crater, Mars",
            "contour_interval_m": CONTOUR_INTERVAL,
            "elevation_range_m": {"min": elev_min, "max": elev_max},
            "source": "USGS Astrogeology CTX DEM — NASA Mars 2020 Landing Site",
            "feature_count": len(features)
        },
        "features": features
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(geojson, f, separators=(",", ":"))

    size_mb = OUT_PATH.stat().st_size / 1024 / 1024
    print(f"Saved: {OUT_PATH}  ({size_mb:.1f} MB, {len(features)} features)")

if __name__ == "__main__":
    main()
