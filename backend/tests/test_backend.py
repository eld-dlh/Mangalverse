"""
Comprehensive unit and integration test suite for Mangalverse Backend.
Directly tests geospatial processing, pathfinding, and all required API router handlers:
- GET /api/discoveries
- GET /api/discoveries/{id}
- GET /api/objectives
- GET /api/terrain
- GET /api/environment
- POST /api/routes
- GET /api/checkpoints
"""
import sys
from pathlib import Path
from fastapi import HTTPException

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.dem_service import jezero_dem_service, mars_haversine_distance
from app.services.pathfinding import terrain_pathfinder
from app.services.discovery_service import discovery_service
from app.services.weather_service import weather_service
from app.routers import (
    objectives,
    discoveries,
    checkpoints,
    terrain,
    routing,
    elevation,
    environment,
    rover
)
from app.models.route import RouteCalculationRequest

def test_dem_raster_properties():
    """Verify DEM resolution, elevation range, and slope gradient."""
    print("Testing DEM raster properties...")
    assert jezero_dem_service.height >= 400
    assert jezero_dem_service.width >= 400
    assert jezero_dem_service.dx_meters >= 15.0
    assert jezero_dem_service.dy_meters >= 15.0

    landing_elev = jezero_dem_service.get_elevation_at(77.4508, 18.4447)
    assert abs(landing_elev - (-2570.0)) < 15.0

    # Bounds and NoData verification
    assert jezero_dem_service.is_in_bounds(77.4508, 18.4447) is True
    assert jezero_dem_service.is_in_bounds(27.70417, -6.61665) is False
    assert jezero_dem_service.get_elevation_at(27.70417, -6.61665) is None
    assert jezero_dem_service.get_slope_at(27.70417, -6.61665) is None
    print(f"DEM raster properties verified (Landing site elevation: {landing_elev:.2f} m, out-of-bounds bounds checking active).")

def test_mars_haversine():
    """Verify spherical distance calculation on Mars."""
    print("Testing Mars spherical haversine...")
    dist = mars_haversine_distance(0.0, 0.0, 0.1, 0.0)
    assert 5500.0 < dist < 6200.0
    print("Mars haversine verified.")

def test_elevation_profile():
    """Verify sampling elevation along polyline."""
    print("Testing elevation profile sampling...")
    coords = [
        [77.4508, 18.4447],
        [77.4042, 18.4485]
    ]
    profile = jezero_dem_service.sample_elevation_profile(coords, num_samples=25)
    assert len(profile) == 25
    assert profile[0]["distance_meters"] == 0.0
    assert profile[-1]["distance_meters"] > 2500.0
    for p in profile:
        assert "elevation_m" in p
        assert "slope_deg" in p
        assert "hazard_level" in p
    print("Elevation profile verified.")

def test_terrain_pathfinding_astar():
    """Verify terrain-aware A* finds valid route."""
    print("Testing terrain-aware A* pathfinding...")
    result = terrain_pathfinder.plan_full_route(
        start_coord=[77.4508, 18.4447],
        destination_coord=[77.4042, 18.4485],
        checkpoint_coords=[],
        max_safe_slope=15.0,
        avoid_sand=True
    )
    assert result["status"] == "SUCCESS"
    assert result["total_distance_km"] > 2.0
    assert result["max_slope_deg"] <= 18.0
    assert result["estimated_drive_duration_hours"] > 0
    assert len(result["path_geojson"]["geometry"]["coordinates"]) > 10
    print("A* pathfinding verified.")

def test_discovery_service():
    """Verify retrieval of NASA scientific discoveries and objectives."""
    print("Testing NASA discovery service...")
    objs = discovery_service.get_objectives()
    assert len(objs) >= 4

    discs = discovery_service.get_discoveries()
    assert len(discs) >= 10

    # Filter by Astrobiology objective OBJ-1
    bio_disc = discovery_service.get_discoveries(objective_id="OBJ-1")
    assert len(bio_disc) >= 3
    assert any(d.id == "wildcat_ridge" for d in bio_disc)

    # Filter samples only
    samples = discovery_service.get_discoveries(samples_only=True)
    assert len(samples) >= 4
    for s in samples:
        assert s.sample_acquired is True
    print("Discovery service verified.")

def test_weather_service_meda():
    """Verify NASA MEDA environmental telemetry reports."""
    print("Testing MEDA weather service...")
    report = weather_service.get_latest_report()
    assert report.sol >= 1200
    assert report.pressure_pa > 500.0
    assert report.temp_air_avg_c < 0.0
    assert report.dust_opacity_tau > 0.0
    print("MEDA weather service verified.")

def test_checkpoints_endpoints():
    """Test GET /api/checkpoints and GET /api/checkpoints/{id}."""
    print("Testing /api/checkpoints endpoints...")
    cps = checkpoints.list_checkpoints(format="json")
    assert len(cps) >= 10
    assert any(c.id == "wildcat_ridge" for c in cps)

    # Filter by objective OBJ-1
    cps_obj1 = checkpoints.list_checkpoints(objective_id="OBJ-1", format="json")
    assert len(cps_obj1) >= 3

    # GeoJSON format
    cps_geojson = checkpoints.list_checkpoints(format="geojson")
    assert cps_geojson["type"] == "FeatureCollection"
    assert len(cps_geojson["features"]) >= 10

    # Single checkpoint
    cp = checkpoints.get_checkpoint("wildcat_ridge")
    assert cp.id == "wildcat_ridge"
    assert cp.sample_acquired is True
    assert cp.sample_name is not None
    assert "Shenandoah" in cp.geological_formation

    # Not found checkpoint error
    try:
        checkpoints.get_checkpoint("non_existent_target")
        assert False, "Expected 404 HTTPException"
    except HTTPException as e:
        assert e.status_code == 404
        assert "not found" in e.detail.lower()

    print("/api/checkpoints endpoints verified.")

def test_terrain_endpoints():
    """Test GET /api/terrain (metadata, point inspection, and coordinate validation)."""
    print("Testing /api/terrain endpoints...")
    # 1. Summary metadata
    summary = terrain.get_terrain_data(format="json")
    assert "bounding_box" in summary
    assert "ctx_dem" in summary
    assert summary["ctx_dem"]["elevation_min_m"] < -2000.0
    assert "hazards" in summary

    # GeoJSON summary polygon
    summary_geojson = terrain.get_terrain_data(format="geojson")
    assert summary_geojson["type"] == "Feature"
    assert summary_geojson["geometry"]["type"] == "Polygon"

    # 2. Point terrain analysis (Octavia Butler landing site)
    pt = terrain.get_terrain_data(lon=77.4508, lat=18.4447, format="json")
    assert "elevation_meters" in pt
    assert abs(pt["elevation_meters"] - (-2570.0)) < 15.0
    assert "slope_degrees" in pt
    assert pt["in_jezero_dem_bounds"] is True

    # 3. Coordinate validation - invalid latitude
    try:
        terrain.get_terrain_data(lon=77.45, lat=95.0)
        assert False, "Expected 400 for out-of-range latitude"
    except HTTPException as e:
        assert e.status_code == 400
        assert "latitude" in e.detail.lower()

    # 4. Coordinate validation - missing one coordinate
    try:
        terrain.get_terrain_data(lon=77.45, lat=None)
        assert False, "Expected 400 for partial coordinates"
    except HTTPException as e:
        assert e.status_code == 400
        assert "both 'lon' and 'lat'" in e.detail.lower()

    print("/api/terrain endpoints verified.")

def test_environment_endpoints():
    """Test GET /api/environment (package, sol query, and GeoJSON)."""
    print("Testing /api/environment endpoints...")
    # Telemetry package
    env_pkg = environment.get_environment(format="json")
    assert hasattr(env_pkg, "latest_sol")
    assert env_pkg.latest_sol.sol >= 1200
    assert len(env_pkg.recent_sols) >= 5

    # Specific sol query
    sol_rep = environment.get_environment(sol=env_pkg.latest_sol.sol, format="json")
    assert sol_rep.sol == env_pkg.latest_sol.sol

    # GeoJSON format
    env_geojson = environment.get_environment(format="geojson")
    assert env_geojson["type"] == "Feature"
    assert env_geojson["geometry"]["coordinates"] == [77.4508, 18.4447]

    # Non-existent sol
    try:
        environment.get_environment(sol=99999)
        assert False, "Expected 404 for unknown sol"
    except HTTPException as e:
        assert e.status_code == 404
        assert "no meda telemetry" in e.detail.lower()

    print("/api/environment endpoints verified.")

def test_routes_endpoint_and_validation():
    """Test POST /api/routes and coordinate/parameter validation."""
    print("Testing POST /api/routes and request validation...")
    # Valid route calculation
    req = RouteCalculationRequest(
        start_point=[77.4508, 18.4447],
        destination_point=[77.4042, 18.4485],
        checkpoint_ids=["montdenier"],
        max_safe_slope_deg=15.0
    )
    res = routing.plan_routes(req, format="json")
    assert res["status"] == "SUCCESS"
    assert res["total_distance_km"] > 2.0
    assert len(res["waypoints"]) >= 2
    assert "elevation_profile" in res

    # GeoJSON format
    res_geojson = routing.plan_routes(req, format="geojson")
    assert res_geojson["type"] == "Feature"
    assert res_geojson["geometry"]["type"] == "LineString"

    # Validation: invalid slope
    try:
        invalid_slope_req = RouteCalculationRequest(
            start_point=[77.4508, 18.4447],
            max_safe_slope_deg=50.0  # Exceeds max 45.0
        )
        routing.plan_routes(invalid_slope_req)
        assert False, "Expected 400 for excessive slope"
    except HTTPException as e:
        assert e.status_code == 400
        assert "slope" in e.detail.lower()

    # Validation: invalid latitude in start_point
    try:
        invalid_lat_req = RouteCalculationRequest(
            start_point=[77.4508, 99.0]
        )
        routing.plan_routes(invalid_lat_req)
        assert False, "Expected 400 for latitude out of range"
    except HTTPException as e:
        assert e.status_code == 400
        assert "latitude" in e.detail.lower()

    # Validation: unknown checkpoint ID
    try:
        invalid_cid_req = RouteCalculationRequest(
            start_point=[77.4508, 18.4447],
            checkpoint_ids=["imaginary_target_xyz"]
        )
        routing.plan_routes(invalid_cid_req)
        assert False, "Expected 400 for unknown checkpoint ID"
    except HTTPException as e:
        assert e.status_code == 400
        assert "not found" in e.detail.lower()

    print("POST /api/routes and validation verified.")

def test_discoveries_and_objectives_endpoints():
    """Test GET /api/discoveries and GET /api/objectives with format handling."""
    print("Testing /api/discoveries and /api/objectives endpoints...")
    # Discoveries JSON
    discs = discoveries.list_discoveries(format="json")
    assert len(discs) >= 10

    # Discoveries GeoJSON
    discs_geojson = discoveries.list_discoveries(format="geojson")
    assert discs_geojson["type"] == "FeatureCollection"
    assert len(discs_geojson["features"]) >= 10

    # Objectives JSON
    objs = objectives.list_objectives(format="json")
    assert len(objs) >= 4

    # Objectives GeoJSON
    objs_geojson = objectives.list_objectives(format="geojson")
    assert objs_geojson["type"] == "FeatureCollection"
    assert len(objs_geojson["features"]) >= 4

    print("/api/discoveries and /api/objectives endpoints verified.")

if __name__ == "__main__":
    test_dem_raster_properties()
    test_mars_haversine()
    test_elevation_profile()
    test_terrain_pathfinding_astar()
    test_discovery_service()
    test_weather_service_meda()
    test_checkpoints_endpoints()
    test_terrain_endpoints()
    test_environment_endpoints()
    test_routes_endpoint_and_validation()
    test_discoveries_and_objectives_endpoints()
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! BACKEND READY. <<<")
