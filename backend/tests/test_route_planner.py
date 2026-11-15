"""
Unit and integration tests for the Martian Terrain-Aware Route-Planning Engine (MARS EXPLORER).
Verifies:
1. Synthetic elevation grid A* routing:
   - SAFEST routes around high-cost obstacles/steep terrain.
   - SHORTEST prioritises minimal travel distance.
   - BALANCED provides optimal trade-off.
2. Checkpoint sequencing (ordered traversal through multiple scientific waypoints).
3. Transparent terrain difficulty scoring and safety warnings.
4. Astronaut safety disclaimers (not claiming guaranteed safety for real humans).
5. Unreachable destination and barrier handling.
6. Integration with authentic Jezero Crater CTX DEM.
"""

import sys
from pathlib import Path
import math
import numpy as np

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.pathfinding import (
    TerrainPathfinder,
    RoutePreference,
    RouteLegStatus,
    ASTRONAUT_SAFETY_DISCLAIMER
)
from app.services.dem_service import jezero_dem_service


class MockSyntheticDEMService:
    """Mock DEM service providing a known 30x30 synthetic elevation raster."""
    def __init__(self):
        self.height = 30
        self.width = 30
        self.dx_meters = 20.0
        self.dy_meters = 20.0
        self.elevation_grid = np.zeros((30, 30), dtype=np.float32)
        self.slope_grid_deg = np.zeros((30, 30), dtype=np.float32)

        # Baseline flat elevation = 100.0m
        self.elevation_grid[:] = 100.0

        # Construct a high-cost steep obstacle ridge across columns 12-16, rows 2-8
        # Direct line from (5, 5) to (5, 25) must cross this ridge
        self.elevation_grid[2:9, 12:17] = 250.0  # +150m cliff
        self.slope_grid_deg[2:9, 12:17] = 28.0   # Steep impassable slope (> 25 deg)

        # Gentle ramp below row 10
        self.elevation_grid[9:, :] = 100.0
        self.slope_grid_deg[9:, :] = 0.0

    def coord_to_pixel(self, lon: float, lat: float):
        # Maps coordinates [77.0 + c*0.01, 18.0 + r*0.01] to (r, c)
        c = int(np.clip(round((lon - 77.0) / 0.01), 0, self.width - 1))
        r = int(np.clip(round((lat - 18.0) / 0.01), 0, self.height - 1))
        return r, c

    def pixel_to_coord(self, r: int, c: int):
        return 77.0 + c * 0.01, 18.0 + r * 0.01

    def get_elevation_at(self, lon: float, lat: float):
        r, c = self.coord_to_pixel(lon, lat)
        return float(self.elevation_grid[r, c])

    def sample_elevation_profile(self, coords, num_samples=50):
        # Simplified linear profile sampler for mock testing
        profile = []
        for idx, (lon, lat) in enumerate(coords):
            dist = idx * 20.0
            r, c = self.coord_to_pixel(lon, lat)
            elev = float(self.elevation_grid[r, c])
            slope = float(self.slope_grid_deg[r, c])
            profile.append({
                "distance_meters": dist,
                "longitude": lon,
                "latitude": lat,
                "elevation_m": elev,
                "slope_deg": slope,
                "hazard_level": "SLOPE_HIGH" if slope > 15.0 else "SLOPE_LOW",
                "terrain_classification": "SLOPE_HIGH" if slope > 15.0 else "SLOPE_LOW",
                "terrain_model_note": "Synthetic mock test raster."
            })
        return profile


def test_synthetic_grid_obstacle_avoidance():
    """Verify that SAFEST preference detours around steep obstacle while avoiding high costs."""
    print("Testing synthetic obstacle avoidance across route preferences...")
    mock_dem = MockSyntheticDEMService()
    pathfinder = TerrainPathfinder(dem_service=mock_dem)

    # Start at (5, 5), Goal at (5, 25).
    # Direct horizontal path on row 5 goes straight into the ridge at cols 12-16 (slope = 28 deg).
    start_coord = list(mock_dem.pixel_to_coord(5, 5))
    goal_coord = list(mock_dem.pixel_to_coord(5, 25))

    # 1. SAFEST preference (should detour around row 9-10 to avoid the 28 deg cliff)
    safe_result = pathfinder.plan_full_route(
        start_coord=start_coord,
        destination_coord=goal_coord,
        preference=RoutePreference.SAFEST,
        max_safe_slope=15.0,
        avoid_sand=True
    )
    assert safe_result["status"] in ["SUCCESS", "PARTIAL_SUCCESS"]
    assert safe_result["route_preference"] == "SAFEST"

    # Verify that the SAFEST route detoured around the obstacle (rows 2-8, cols 12-16)
    path_coords = safe_result["path_geojson"]["geometry"]["coordinates"]
    path_rc = [mock_dem.coord_to_pixel(lon, lat) for lon, lat in path_coords]
    min_row = min(r for r, c in path_rc)
    max_row = max(r for r, c in path_rc)

    # Must detour either north (row < 2) or south (row >= 9) around the obstacle
    assert min_row < 2 or max_row >= 9, f"SAFEST route should detour around rows 2-8, got min_row={min_row}, max_row={max_row}"

    # Verify that ZERO cells in the path touched the steep obstacle
    obstacle_hits = [pt for pt in path_rc if 2 <= pt[0] <= 8 and 12 <= pt[1] <= 16]
    assert len(obstacle_hits) == 0, f"SAFEST route should have avoided obstacle completely, hit: {obstacle_hits}"

    # Verify slope on the detour remains within safe limits
    assert safe_result["max_slope_deg"] <= 15.0

    # 2. SHORTEST preference (attempts direct or shorter distance traversal)
    shortest_result = pathfinder.plan_full_route(
        start_coord=start_coord,
        destination_coord=goal_coord,
        preference=RoutePreference.SHORTEST,
        max_safe_slope=30.0,
        avoid_sand=False
    )
    assert shortest_result["status"] == "SUCCESS"
    assert shortest_result["route_preference"] == "SHORTEST"

    # SHORTEST distance should be shorter or equal to SAFEST detour distance
    assert shortest_result["total_distance_km"] <= safe_result["total_distance_km"]

    print(
        f"Obstacle avoidance verified: SAFEST distance={safe_result['total_distance_km']:.3f} km (max row {max_row}), "
        f"SHORTEST distance={shortest_result['total_distance_km']:.3f} km."
    )


def test_checkpoint_sequencing():
    """Verify that multiple scientific checkpoints are visited in the exact requested order."""
    print("Testing multi-checkpoint sequential ordering...")
    mock_dem = MockSyntheticDEMService()
    pathfinder = TerrainPathfinder(dem_service=mock_dem)

    p_start = list(mock_dem.pixel_to_coord(2, 2))
    cp_1 = list(mock_dem.pixel_to_coord(10, 20))
    cp_2 = list(mock_dem.pixel_to_coord(25, 5))
    p_dest = list(mock_dem.pixel_to_coord(28, 28))

    result = pathfinder.plan_full_route(
        start_coord=p_start,
        destination_coord=p_dest,
        checkpoint_coords=[cp_1, cp_2],
        preference=RoutePreference.BALANCED
    )

    assert result["status"] == "SUCCESS"
    assert len(result["waypoints"]) == 4

    # Verify waypoints match coordinates and sequential naming
    assert result["waypoints"][0]["name"] == "Mission Origin"
    assert result["waypoints"][1]["name"] == "Checkpoint #1"
    assert result["waypoints"][2]["name"] == "Checkpoint #2"
    assert result["waypoints"][3]["name"] == "Objective Destination"

    # Verify progressive cumulative distances
    wps = result["waypoints"]
    assert wps[0]["distance_from_start_m"] == 0.0
    assert wps[1]["distance_from_start_m"] > 0.0
    assert wps[2]["distance_from_start_m"] > wps[1]["distance_from_start_m"]
    assert wps[3]["distance_from_start_m"] > wps[2]["distance_from_start_m"]

    print("Checkpoint sequencing verified: Origin -> CP1 -> CP2 -> Destination.")


def test_transparent_difficulty_and_warnings():
    """Verify difficulty metrics, safety warnings, and explicit astronaut disclaimer."""
    print("Testing transparent difficulty scoring, warnings, and disclaimer...")
    mock_dem = MockSyntheticDEMService()
    pathfinder = TerrainPathfinder(dem_service=mock_dem)

    p_start = list(mock_dem.pixel_to_coord(2, 2))
    p_dest = list(mock_dem.pixel_to_coord(20, 20))

    result = pathfinder.plan_full_route(
        start_coord=p_start,
        destination_coord=p_dest,
        preference=RoutePreference.BALANCED
    )

    # 1. Difficulty score & rating
    assert "terrain_difficulty_score" in result
    score = result["terrain_difficulty_score"]
    assert 0.0 <= score <= 100.0
    assert "terrain_difficulty_rating" in result

    # 2. Safety disclaimer (explicit rule: do not claim guaranteed safety for astronauts)
    assert "safety_disclaimer" in result
    assert "NOT guaranteed safe for human astronauts" in result["safety_disclaimer"]

    # 3. GeoJSON Feature format
    geojson = result["path_geojson"]
    assert geojson["type"] == "Feature"
    assert geojson["geometry"]["type"] == "LineString"
    assert len(geojson["geometry"]["coordinates"]) > 5
    assert "terrain_difficulty_score" in geojson["properties"]

    print(f"Difficulty score: {score}/100 ({result['terrain_difficulty_rating']}).")
    print("Safety disclaimer verified.")


def test_unreachable_destination_handling():
    """Verify that enclosed or unreachable destinations are handled gracefully without crashing."""
    print("Testing unreachable destination handling...")
    mock_dem = MockSyntheticDEMService()

    # Create an impassable wall around cell (20, 20)
    mock_dem.slope_grid_deg[18:23, 18:23] = 45.0  # 45 deg impassable barrier

    pathfinder = TerrainPathfinder(dem_service=mock_dem)
    p_start = list(mock_dem.pixel_to_coord(2, 2))
    p_enclosed = list(mock_dem.pixel_to_coord(20, 20))

    # Engine should not throw an unhandled crash; it should return PARTIAL_SUCCESS or handle gracefully
    result = pathfinder.plan_full_route(
        start_coord=p_start,
        destination_coord=p_enclosed,
        preference=RoutePreference.SAFEST,
        max_safe_slope=15.0
    )

    assert result["status"] in ["PARTIAL_SUCCESS", "SUCCESS"]
    assert len(result["safety_warnings"]) > 0 or len(result["legs"]) > 0
    print("Unreachable destination handled gracefully with diagnostic warnings.")


def test_authentic_jezero_dem_preferences():
    """Verify all three preferences on authentic Jezero Crater CTX DEM."""
    print("Testing authentic Jezero Crater DEM routing across all preferences...")
    pathfinder = TerrainPathfinder(dem_service=jezero_dem_service)

    # Route from Octavia Butler Landing to Wildcat Ridge
    p_start = [77.4508, 18.4447]
    p_dest = [77.4042, 18.4485]

    for pref in [RoutePreference.SHORTEST, RoutePreference.BALANCED, RoutePreference.SAFEST]:
        res = pathfinder.plan_full_route(
            start_coord=p_start,
            destination_coord=p_dest,
            preference=pref,
            max_safe_slope=15.0,
            avoid_sand=True
        )
        assert res["status"] == "SUCCESS"
        assert res["total_distance_km"] > 2.0
        assert res["route_preference"] == pref.value
        assert len(res["elevation_profile"]) > 10
        assert res["safety_disclaimer"] == ASTRONAUT_SAFETY_DISCLAIMER

    print("Authentic Jezero DEM verified under SHORTEST, BALANCED, and SAFEST.")


if __name__ == "__main__":
    test_synthetic_grid_obstacle_avoidance()
    test_checkpoint_sequencing()
    test_transparent_difficulty_and_warnings()
    test_unreachable_destination_handling()
    test_authentic_jezero_dem_preferences()
    print("\n>>> ALL ROUTE-PLANNING ENGINE TESTS PASSED SUCCESSFULLY! <<<")
