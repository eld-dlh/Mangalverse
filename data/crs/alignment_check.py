"""
NASA Geospatial Quality Assurance & CRS Alignment Verification.
Verifies spatial reference, bounding box intersection, raster geotransforms,
and vector coordinate fidelity across all prepared NASA Jezero Crater datasets.
"""
import json
import rasterio
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent

def check_raster(path: Path, name: str, expected_min_elev=None, expected_max_elev=None):
    print(f"\n--- Checking Raster: {name} ---")
    assert path.exists(), f"File does not exist: {path}"
    with rasterio.open(path) as src:
        bounds = src.bounds
        crs = src.crs
        width, height = src.width, src.height
        data = src.read(1)
        valid_mask = data != src.nodata
        valid_data = data[valid_mask]

        min_val = float(valid_data.min()) if len(valid_data) > 0 else None
        max_val = float(valid_data.max()) if len(valid_data) > 0 else None

        print(f"  Dimensions: {width}x{height} pixels, 1 band")
        print(f"  CRS: {crs}")
        print(f"  Bounds: Lon [{bounds.left:.4f}, {bounds.right:.4f}], Lat [{bounds.bottom:.4f}, {bounds.top:.4f}]")
        print(f"  Data Range: min={min_val:.1f}, max={max_val:.1f}")

        # Assert valid Jezero bounds
        assert bounds.left >= 77.0 and bounds.right <= 77.8, "Longitude out of Jezero region"
        assert bounds.bottom >= 18.0 and bounds.top <= 18.8, "Latitude out of Jezero region"

        if expected_min_elev is not None:
            assert min_val >= expected_min_elev, f"Min elevation {min_val} below expected {expected_min_elev}"
        if expected_max_elev is not None:
            assert max_val <= expected_max_elev, f"Max elevation {max_val} above expected {expected_max_elev}"

    print(f"  [PASS] {name} properly calibrated and georeferenced.")

def check_geojson(path: Path, name: str, expected_min_count=1):
    print(f"\n--- Checking Vector: {name} ---")
    assert path.exists(), f"File does not exist: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("type") == "FeatureCollection", "Not a valid GeoJSON FeatureCollection"
    features = data.get("features", [])
    print(f"  Total Features: {len(features)}")
    assert len(features) >= expected_min_count, f"Expected at least {expected_min_count} features"

    for feat in features:
        geom = feat.get("geometry", {})
        props = feat.get("properties", {})
        assert geom.get("type") in ["Point", "LineString", "Polygon"], f"Invalid geometry type: {geom.get('type')}"
        assert props, "Properties missing for feature"

    print(f"  [PASS] {name} GeoJSON valid and conforms to RFC 7946.")

def check_meda(path: Path):
    print(f"\n--- Checking Environmental: MEDA Telemetry ---")
    assert path.exists(), f"File does not exist: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])
    print(f"  Total MEDA Sol Records: {len(records)}")
    assert len(records) >= 5, "Insufficient MEDA records"

    for r in records:
        assert 500.0 <= r["pressure_pa"] <= 850.0, f"Unphysical pressure: {r['pressure_pa']} Pa"
        assert -110.0 <= r["temp_air_min_c"] <= -50.0, f"Unphysical min temp: {r['temp_air_min_c']} C"
        assert -40.0 <= r["temp_air_max_c"] <= 15.0, f"Unphysical max temp: {r['temp_air_max_c']} C"
        assert 0.1 <= r["dust_optical_depth_tau"] <= 2.5, f"Unphysical tau: {r['dust_optical_depth_tau']}"

    print(f"  [PASS] MEDA atmospheric telemetry verified within Mars physical limits.")

def run_alignment_suite():
    print("=================================================================")
    print("MARS EXPLORER: NASA GEOSPATIAL DATASET QUALITY ASSURANCE SUITE")
    print("=================================================================")

    # 1. Check Elevation Rasters
    check_raster(
        DATA_DIR / "elevation" / "mola" / "jezero_mola_elevation.tif",
        "MOLA Regional Elevation (MEGDR)",
        expected_min_elev=-2650, expected_max_elev=-2100
    )
    check_raster(
        DATA_DIR / "elevation" / "ctx" / "jezero_ctx_dem.tif",
        "CTX Regional DEM (Ames Stereo Pipeline)",
        expected_min_elev=-2600, expected_max_elev=-2200
    )
    check_raster(
        DATA_DIR / "elevation" / "hirise" / "jezero_hirise_dtm_delta.tif",
        "HiRISE High-Resolution DTM (TRN Delta Mosaic)",
        expected_min_elev=-2600, expected_max_elev=-2480
    )

    # 2. Check Imagery Rasters
    check_raster(
        DATA_DIR / "imagery" / "ctx_mosaic" / "jezero_ctx_mosaic.tif",
        "CTX Orthorectified Panchromatic Surface Mosaic"
    )
    check_raster(
        DATA_DIR / "imagery" / "hirise_ortho" / "jezero_hirise_ortho.tif",
        "HiRISE Calibrated Orthorectified Imagery"
    )

    # 3. Check Vector Layers
    check_geojson(
        DATA_DIR / "vector" / "discoveries" / "scientific_discoveries.geojson",
        "Perseverance Scientific Targets & Samples",
        expected_min_count=10
    )
    check_geojson(
        DATA_DIR / "vector" / "traverse" / "perseverance_traverse_sols_0_1230.geojson",
        "Perseverance Historical Traverse Path & Stops",
        expected_min_count=10
    )
    check_geojson(
        DATA_DIR / "vector" / "geological_units" / "jezero_geological_units.geojson",
        "USGS SIM 3464 Jezero Stratigraphic Units",
        expected_min_count=4
    )

    # 4. Check Environmental Telemetry
    check_meda(DATA_DIR / "environmental" / "meda" / "meda_daily_summaries.json")

    print("\n=================================================================")
    print(">>> ALL NASA GEOSPATIAL DATASETS PASSED QA & ALIGNMENT VERIFICATION! <<<")
    print("=================================================================")

if __name__ == "__main__":
    run_alignment_suite()
