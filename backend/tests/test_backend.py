"""
Comprehensive unit and integration test suite for Mars Explorer Backend.
Directly tests geospatial processing, pathfinding, and API router handlers.
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.dem_service import jezero_dem_service, mars_haversine_distance
from app.services.pathfinding import terrain_pathfinder
from app.services.discovery_service import discovery_service
from app.services.weather_service import weather_service
from app.routers import objectives, discoveries, routing, elevation, environment, rover
from app.models.route import RouteCalculationRequest

def test_dem_raster_properties():
    """Verify DEM resolution, elevation range, and slope gradient."""
    print("Testing DEM raster properties...")
    # Supports authentic CTX DEM (5067x4456, 20m resolution)
    assert jezero_dem_service.height >= 400
    assert jezero_dem_service.width >= 400
    assert jezero_dem_service.dx_meters >= 15.0
    assert jezero_dem_service.dy_meters >= 15.0

    # Landing site elevation should be approx -2570m (authentic CTX DEM gives -2567.05m)
    landing_elev = jezero_dem_service.get_elevation_at(77.4508, 18.4447)
    assert abs(landing_elev - (-2570.0)) < 15.0
    print(f"DEM raster properties verified (Landing site elevation: {landing_elev:.2f} m).")

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

def test_router_handlers():
    """Directly test API router handler logic."""
    print("Testing API router handlers...")
    # Objectives
    objs = objectives.list_objectives()
    assert len(objs) >= 4
    obj1 = objectives.get_objective("OBJ-1")
    assert obj1.code == "ASTROBIO-LACUSTRINE"

    # Discoveries GeoJSON
    geojson = discoveries.get_discoveries_geojson()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) >= 10

    # Routing
    req = RouteCalculationRequest(
        start_point=[77.4508, 18.4447],
        destination_point=[77.4042, 18.4485],
        checkpoint_ids=["montdenier"],
        max_safe_slope_deg=15.0
    )
    res = routing.calculate_route(req)
    assert res["status"] == "SUCCESS"
    assert len(res["elevation_profile"]) > 0
    assert len(res["waypoints"]) >= 2

    # Elevation point
    pt = elevation.get_elevation_point(lon=77.4508, lat=18.4447)
    assert "elevation_meters" in pt
    assert "slope_degrees" in pt

    # Environment
    meda = environment.get_environmental_telemetry()
    assert meda.latest_sol.sol >= 1200

    # Rover
    trav = rover.get_rover_traverse()
    assert trav["type"] == "FeatureCollection"
    status = rover.get_rover_status()
    assert status["mission_sol"] >= 1200
    print("All router handlers verified.")

if __name__ == "__main__":
    test_dem_raster_properties()
    test_mars_haversine()
    test_elevation_profile()
    test_terrain_pathfinding_astar()
    test_discovery_service()
    test_weather_service_meda()
    test_router_handlers()
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! BACKEND READY. <<<")
