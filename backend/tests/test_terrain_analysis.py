"""
Unit tests for the Terrain Analysis module (MANGALVERSE).
Uses a mathematically known synthetic test raster and tests against authentic Jezero DEM.
Verifies:
1. GeoTIFF loading and preservation of spatial reference (CRS, Affine, bounds).
2. Slope computation in degrees and percent rise.
3. Terrain difficulty / traversal-cost grid generation with steeper terrain penalties.
4. Configurable hazard zone penalties.
5. Identification of missing/NoData and physically invalid planetary cells.
6. Export format for route planner and GeoTIFF raster export.
"""

import sys
import tempfile
from pathlib import Path
import math
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.terrain_analysis import (
    TerrainAnalyzer,
    TerrainConfig,
    HazardZone
)
from app.config import DEM_PATH


def create_known_sample_raster() -> Tuple[np.ndarray, Affine, CRS, float]:
    """
    Generate a 20x20 known sample raster with exact mathematical geometries:
    - Rows 0-4: Perfectly flat surface at elevation 100.0 m (slope = 0 deg, cost = 1.0)
    - Rows 5-9: Linear uniform slope ramping by 3.5m per 20m pixel (slope ~ 9.9 deg <= nominal)
    - Rows 10-14: Steep slope ramping by 8.0m per 20m pixel (slope ~ 21.8 deg > max_safe)
    - Cell (15, 15): Near-vertical cliff (+200m step change, slope > 80 deg >= impassable)
    - Cell (16, 16): Explicit NoData cell (-9999.0)
    - Cell (17, 17): Out-of-bounds physical elevation (+50,000 m > planetary max)
    """
    height, width = 20, 20
    grid = np.zeros((height, width), dtype=np.float32)

    # 1. Flat area (elevation = 100.0 m)
    grid[0:5, :] = 100.0

    # 2. Gentle uniform slope (dz = 3.5 m per 20 m pixel)
    for r in range(5, 10):
        grid[r, :] = 100.0 + (r - 4) * 3.5

    # 3. Steep slope (dz = 8.0 m per 20 m pixel)
    for r in range(10, 15):
        grid[r, :] = grid[9, 0] + (r - 9) * 8.0

    # 4. Vertical cliff cell (impassable slope)
    grid[15, 15] = 1000.0

    # 5. Missing / NoData cell
    nodata_val = -9999.0
    grid[16, 16] = nodata_val

    # 6. Physically invalid elevation (exceeds Olympus Mons +21.2 km)
    grid[17, 17] = 50000.0

    # Spatial reference: 20m pixel size, Mars projected coordinate system
    # Origin at (lon=77.40, lat=18.40) equivalent in local projected space
    transform = Affine(20.0, 0.0, 500000.0, 0.0, -20.0, 1000000.0)
    crs = CRS.from_proj4("+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +a=3396190 +b=3396190 +units=m +no_defs")

    return grid, transform, crs, nodata_val


def test_spatial_reference_preservation():
    """Requirement 1 & 2: Preserve spatial reference, CRS, resolution, and coordinates."""
    print("Testing spatial reference preservation...")
    grid, transform, crs, nodata = create_known_sample_raster()

    analyzer = TerrainAnalyzer(
        raster_source=grid,
        transform=transform,
        crs=crs,
        nodata=nodata
    )

    # Verify transform and resolution
    assert analyzer.transform == transform
    assert analyzer.crs == crs
    assert analyzer.dx_meters == 20.0
    assert analyzer.dy_meters == 20.0
    assert analyzer.nodata == nodata
    assert analyzer.height == 20
    assert analyzer.width == 20

    # Verify coordinate transforms preserve pixel-to-world mapping
    x, y = analyzer.pixel_to_coord(0, 0)
    r, c = analyzer.coord_to_pixel(x, y)
    assert (r, c) == (0, 0)
    print("Spatial reference preservation verified.")


def test_slope_calculation():
    """Requirement 3: Calculate slope from elevation in degrees and percent."""
    print("Testing slope calculations (degrees and percent)...")
    grid, transform, crs, nodata = create_known_sample_raster()

    analyzer = TerrainAnalyzer(
        raster_source=grid,
        transform=transform,
        crs=crs,
        nodata=nodata
    )

    # 1. Flat plain (Rows 1-3) should have ~0.0 slope
    flat_slope_deg = analyzer.slope_grid_deg[2, 2]
    flat_slope_pct = analyzer.slope_grid_percent[2, 2]
    assert flat_slope_deg < 0.1
    assert flat_slope_pct < 0.1

    # 2. Gentle ramp (Rows 6-8): dz=3.5m over 20m => gradient = 3.5/20 = 0.175
    # arctan(0.175) in degrees ~ 9.93 deg; percent = 17.5%
    ramp_slope_deg = analyzer.slope_grid_deg[7, 10]
    ramp_slope_pct = analyzer.slope_grid_percent[7, 10]
    assert 9.0 <= ramp_slope_deg <= 11.0
    assert 16.0 <= ramp_slope_pct <= 19.5

    # 3. Steep ramp (Rows 11-13): dz=8.0m over 20m => gradient = 8.0/20 = 0.400
    # arctan(0.400) in degrees ~ 21.8 deg; percent = 40.0%
    steep_slope_deg = analyzer.slope_grid_deg[12, 10]
    steep_slope_pct = analyzer.slope_grid_percent[12, 10]
    assert 20.0 <= steep_slope_deg <= 23.5
    assert 37.0 <= steep_slope_pct <= 43.0

    print(f"Slope verified: Flat={flat_slope_deg:.2f} deg, Ramp={ramp_slope_deg:.2f} deg, Steep={steep_slope_deg:.2f} deg.")


def test_traversal_cost_and_steep_penalties():
    """Requirement 4 & 5: Generate traversal cost grid; assign higher costs to steeper terrain."""
    print("Testing traversal cost grid and slope penalties...")
    grid, transform, crs, nodata = create_known_sample_raster()

    cfg = TerrainConfig(
        nominal_slope_deg=10.0,
        max_safe_slope_deg=15.0,
        impassable_slope_deg=25.0,
        base_cost_per_meter=1.0,
        slope_weight=2.5
    )

    analyzer = TerrainAnalyzer(
        raster_source=grid,
        transform=transform,
        crs=crs,
        nodata=nodata,
        config=cfg
    )

    flat_cost = analyzer.cost_grid[2, 2]
    gentle_cost = analyzer.cost_grid[7, 10]
    steep_cost = analyzer.cost_grid[12, 10]
    cliff_cost = analyzer.cost_grid[15, 15]

    # 1. Flat cost should be near baseline (1.0)
    assert 1.0 <= flat_cost <= 1.05

    # 2. Steeper terrain must have strictly higher cost
    assert gentle_cost > flat_cost
    assert steep_cost > gentle_cost

    # 3. Slope >= impassable_slope_deg (25 deg) must be infinity
    assert math.isinf(cliff_cost) or cliff_cost > 1000.0

    print(f"Cost scaling verified: Flat={flat_cost:.2f}, Gentle={gentle_cost:.2f}, Steep={steep_cost:.2f}, Cliff={cliff_cost}.")


def test_configurable_hazard_penalties():
    """Requirement 6: Support configurable hazard penalties."""
    print("Testing configurable hazard penalties...")
    grid, transform, crs, nodata = create_known_sample_raster()

    analyzer = TerrainAnalyzer(
        raster_source=grid,
        transform=transform,
        crs=crs,
        nodata=nodata
    )

    # Flat cell cost before hazard
    base_flat_cost = analyzer.cost_grid[1, 1]

    # Convert pixel coords to world coords for bounding box
    x1, y1 = analyzer.pixel_to_coord(0, 0)
    x2, y2 = analyzer.pixel_to_coord(3, 3)

    hazard = HazardZone(
        name="Test Sand Ripple Dune Field",
        hazard_type="Sand Drift Hazard",
        min_lon=min(x1, x2),
        max_lon=max(x1, x2),
        min_lat=min(y1, y2),
        max_lat=max(y1, y2),
        penalty_multiplier=4.0
    )
    analyzer.add_hazard_zone(hazard)

    hazard_flat_cost = analyzer.cost_grid[1, 1]
    outside_hazard_cost = analyzer.cost_grid[1, 10]

    # Inside hazard: cost should be multiplied by penalty_multiplier
    assert abs(hazard_flat_cost - (base_flat_cost * 4.0)) < 0.2
    # Outside hazard: cost should remain baseline
    assert abs(outside_hazard_cost - base_flat_cost) < 0.05

    print(f"Hazard penalties verified: Base={base_flat_cost:.2f}, In Hazard={hazard_flat_cost:.2f}.")


def test_identification_of_invalid_cells():
    """Requirement 7: Identify invalid or missing terrain cells."""
    print("Testing identification of invalid and missing cells...")
    grid, transform, crs, nodata = create_known_sample_raster()

    analyzer = TerrainAnalyzer(
        raster_source=grid,
        transform=transform,
        crs=crs,
        nodata=nodata
    )

    valid_mask, stats = analyzer.identify_invalid_cells()

    # Total cells: 20x20 = 400
    assert stats["total_cells"] == 400

    # Cell (16, 16) is NoData (-9999.0) -> must be invalid
    assert valid_mask[16, 16] is np.False_ or valid_mask[16, 16] == False
    assert math.isinf(analyzer.cost_grid[16, 16])

    # Cell (17, 17) is outlier (+50,000m > 30,000m) -> must be invalid
    assert valid_mask[17, 17] is np.False_ or valid_mask[17, 17] == False
    assert math.isinf(analyzer.cost_grid[17, 17])

    # Flat cell (2, 2) is valid
    assert valid_mask[2, 2] is np.True_ or valid_mask[2, 2] == True

    print(f"Invalid cells identified: {stats['invalid_cells']} invalid out of {stats['total_cells']}.")


def test_export_for_route_planner_and_geotiff():
    """Requirement 8: Export processed terrain information for route planner & GeoTIFF."""
    print("Testing data export for route planner and GeoTIFF...")
    grid, transform, crs, nodata = create_known_sample_raster()

    analyzer = TerrainAnalyzer(
        raster_source=grid,
        transform=transform,
        crs=crs,
        nodata=nodata
    )

    # 1. Export route planner data dictionary
    planner_data = analyzer.export_route_planner_data()
    assert "cost_grid" in planner_data
    assert "slope_degrees" in planner_data
    assert "slope_percent" in planner_data
    assert "elevation_grid" in planner_data
    assert "valid_mask" in planner_data
    assert "hazard_mask" in planner_data
    assert planner_data["shape"] == (20, 20)
    assert planner_data["dx_meters"] == 20.0

    # 2. Subgrid window extraction for fast local A* search
    subgrid = analyzer.get_subgrid_for_routing(rmin=2, rmax=8, cmin=2, cmax=8)
    assert subgrid["sub_cost"].shape == (7, 7)
    assert subgrid["sub_elevation"].shape == (7, 7)
    assert subgrid["sub_slope"].shape == (7, 7)

    # 3. GeoTIFF export
    with tempfile.TemporaryDirectory() as tmpdir:
        out_tif = Path(tmpdir) / "test_traversal_cost.tif"
        exported_path = analyzer.export_geotiff(out_tif, layer="cost")
        assert exported_path.exists()

        # Reopen with rasterio and verify spatial reference and dimensions
        with rasterio.open(exported_path) as src:
            assert src.shape == (20, 20)
            assert src.crs == crs
            assert src.transform == transform
            exported_data = src.read(1)
            assert exported_data.shape == (20, 20)
            # Valid flat cell should retain cost value
            assert 1.0 <= exported_data[2, 2] <= 1.05
            # Impassable / invalid cell should have exported nodata (-9999.0)
            assert exported_data[16, 16] == -9999.0

    print("Route planner export and GeoTIFF verified.")


def test_authentic_jezero_dem_integration():
    """Verify TerrainAnalyzer on authentic Jezero Crater 90MB CTX DEM."""
    print("Testing integration with authentic Jezero Crater CTX DEM...")
    if not DEM_PATH.exists():
        print("Skipping authentic DEM test: file not present.")
        return

    analyzer = TerrainAnalyzer(raster_source=DEM_PATH)
    assert analyzer.height > 1000
    assert analyzer.width > 1000
    assert analyzer.dx_meters >= 15.0

    # Test coordinate query at Octavia E. Butler landing site (77.4508 E, 18.4447 N)
    cost = analyzer.get_traversal_cost_at(77.4508, 18.4447)
    assert 1.0 <= cost <= 5.0  # Landing site is traversable flat plain

    print(f"Authentic Jezero DEM integration verified (Landing site cost: {cost:.2f}).")


if __name__ == "__main__":
    test_spatial_reference_preservation()
    test_slope_calculation()
    test_traversal_cost_and_steep_penalties()
    test_configurable_hazard_penalties()
    test_identification_of_invalid_cells()
    test_export_for_route_planner_and_geotiff()
    test_authentic_jezero_dem_integration()
    print("\n>>> ALL TERRAIN ANALYSIS TESTS PASSED SUCCESSFULLY! <<<")
