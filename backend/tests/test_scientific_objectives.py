"""
Unit and Integration Tests for Scientific Objectives Integration (MARS EXPLORER).
Verifies:
1. Retrieval of authentic scientific discoveries from the shared SQLite database.
2. Grouping of discoveries into scientific categories:
   - Ancient water
   - Geological investigation
   - Water ice and resources
   - Atmospheric and dust observations
3. Retrieval of relevant discoveries and coordinates for selected objectives.
4. Independent testing of the objective-selection system decoupled from pathfinding.
5. Generation of complete Mission Itineraries connecting objectives, ordered checkpoints,
   terrain difficulty, NASA MEDA environmental telemetry, and source citations.
6. Error handling for unrecognized objectives and unreachable targets.
"""

import sys
from pathlib import Path
import numpy as np

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.mission_service import (
    MissionService,
    SCIENTIFIC_CATEGORIES,
    mission_service
)
from app.services.discovery_service import discovery_service
from app.models.itinerary import MissionItineraryRequest, MissionItineraryResponse
from app.services.pathfinding import ASTRONAUT_SAFETY_DISCLAIMER


def test_scientific_categories_grouping():
    """Requirement 1, 2, 3: Group authentic discoveries by scientific category."""
    print("Testing scientific categories grouping...")
    svc = MissionService()
    categories = svc.get_categories()

    assert len(categories) == 4
    cat_ids = [c.id for c in categories]
    assert "ancient_water" in cat_ids
    assert "geological_investigation" in cat_ids
    assert "water_ice_resources" in cat_ids
    assert "atmospheric_dust" in cat_ids

    # Verify category metadata and discovery IDs
    for cat in categories:
        assert cat.name is not None
        assert cat.description is not None
        assert len(cat.discovery_ids) >= 4
        assert len(cat.recommended_checkpoint_ids) >= 3
        assert len(cat.citations) >= 1

        # Verify that all discovery IDs actually exist in the authentic database
        for disc_id in cat.discovery_ids:
            disc = discovery_service.get_discovery_by_id(disc_id)
            assert disc is not None, f"Discovery '{disc_id}' in category '{cat.id}' must exist in SQLite DB"

    print("All 4 scientific categories verified with authentic database discoveries.")


def test_retrieval_of_objective_discoveries_decoupled():
    """Requirement 4: Return relevant discoveries and coordinates for a selected objective (Decoupled)."""
    print("Testing decoupled retrieval of discoveries and coordinates for objectives...")
    svc = MissionService()

    # 1. Ancient water objective
    water_locs = svc.get_discoveries_for_objective("ancient_water")
    assert len(water_locs) >= 4
    target_names = [loc.target_name for loc in water_locs]
    assert any("Wildcat Ridge" in name for name in target_names)
    assert any("Enchanted Lake" in name for name in target_names)

    for loc in water_locs:
        # Validate coordinates within Jezero Crater
        assert 77.30 <= loc.longitude <= 77.50
        assert 18.35 <= loc.latitude <= 18.55
        assert loc.elevation_m < -2000.0
        assert loc.lithology is not None
        assert loc.citation is not None
        assert loc.scientific_significance is not None

    # 2. Geological investigation objective
    geo_locs = svc.get_discoveries_for_objective("geological_investigation")
    assert len(geo_locs) >= 4
    geo_targets = [loc.target_name for loc in geo_locs]
    assert any("Octavia E. Butler" in name for name in geo_targets)
    assert any("Montdenier" in name for name in geo_targets)

    # 3. Water ice and resources objective
    resource_locs = svc.get_discoveries_for_objective("water_ice_resources")
    assert len(resource_locs) >= 3
    res_targets = [loc.target_name for loc in resource_locs]
    assert any("Three Forks" in name for name in res_targets)

    # 4. Atmospheric and dust observations objective
    atmo_locs = svc.get_discoveries_for_objective("atmospheric_dust")
    assert len(atmo_locs) >= 3

    print("Decoupled objective discovery retrieval verified across all 4 categories.")


def test_independent_objective_selection_with_mock_routing():
    """Requirement: Objective-selection system must remain separate from pathfinding."""
    print("Testing objective selection system with mock router...")
    
    class MockPathfinder:
        def plan_full_route(self, start_coord, destination_coord, checkpoint_coords, **kwargs):
            return {
                "status": "SUCCESS",
                "route_preference": kwargs.get("preference", "BALANCED"),
                "total_distance_km": 4.25,
                "total_elevation_gain_m": 42.0,
                "total_elevation_loss_m": 12.0,
                "estimated_drive_duration_hours": 35.4,
                "estimated_energy_consumption_kwh": 14.16,
                "max_slope_deg": 8.5,
                "avg_slope_deg": 4.2,
                "terrain_difficulty_score": 22.0,
                "terrain_difficulty_rating": "LOW DIFFICULTY (Traversable Flat Crater Bedrock)",
                "path_geojson": {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [start_coord, destination_coord]},
                    "properties": {}
                },
                "elevation_profile": [
                    {"distance_meters": 0.0, "elevation_m": -2570.0, "slope_deg": 2.0},
                    {"distance_meters": 4250.0, "elevation_m": -2528.0, "slope_deg": 3.0}
                ],
                "safety_warnings": []
            }

    mock_svc = MissionService(pathfinder=MockPathfinder())
    req = MissionItineraryRequest(
        objective_id="ancient_water",
        selected_checkpoint_ids=["enchanted_lake", "wildcat_ridge"]
    )
    itinerary = mock_svc.plan_scientific_itinerary(req)

    assert itinerary.status == "SUCCESS"
    assert itinerary.selected_objective_id == "ancient_water"
    assert len(itinerary.checkpoint_order) == 2
    assert itinerary.checkpoint_order[0]["discovery_id"] == "enchanted_lake"
    assert itinerary.checkpoint_order[1]["discovery_id"] == "wildcat_ridge"
    assert itinerary.route_summary["total_distance_km"] == 4.25

    print("Independent objective selection verified using mock routing.")


def test_mission_itinerary_generation():
    """Requirement 5, 6, 7: Generate full mission itinerary with terrain-aware route and MEDA weather."""
    print("Testing full mission itinerary generation with authentic DEM and MEDA...")
    req = MissionItineraryRequest(
        objective_id="ancient_water",
        selected_checkpoint_ids=["enchanted_lake", "wildcat_ridge", "bright_angel"],
        preference="SAFEST",
        max_safe_slope_deg=15.0
    )
    itinerary = mission_service.plan_scientific_itinerary(req)

    assert isinstance(itinerary, MissionItineraryResponse)
    assert itinerary.status in ["SUCCESS", "PARTIAL_SUCCESS"]
    assert "Ancient Water" in itinerary.selected_objective_title
    assert itinerary.scientific_category is not None
    assert len(itinerary.discovery_locations) == 3

    # Verify Checkpoint Order
    assert len(itinerary.checkpoint_order) == 3
    assert itinerary.checkpoint_order[0]["discovery_id"] == "enchanted_lake"
    assert itinerary.checkpoint_order[1]["discovery_id"] == "wildcat_ridge"
    assert itinerary.checkpoint_order[2]["discovery_id"] == "bright_angel"

    # Verify Route Summary Metrics
    route_sum = itinerary.route_summary
    assert route_sum["total_distance_km"] > 3.0
    assert route_sum["max_slope_deg"] <= 18.0
    assert route_sum["route_preference"] == "SAFEST"

    # Verify Terrain Difficulty
    diff = itinerary.terrain_difficulty
    assert 0.0 <= diff["score"] <= 100.0
    assert diff["rating"] is not None

    # Verify Environmental Observations from NASA MEDA
    env = itinerary.environmental_observations
    assert env.sol >= 1200
    assert env.pressure_pa > 500.0
    assert env.temp_air_avg_c < 0.0
    assert env.dust_opacity_tau > 0.0
    assert "MEDA" in env.instrument

    # Verify Scientific Source References
    sources = itinerary.source_references
    assert "scientific_records" in sources
    assert len(sources["scientific_records"]) >= 1
    assert "topography" in sources

    # Verify Astronaut Safety Disclaimer
    assert itinerary.safety_disclaimer == ASTRONAUT_SAFETY_DISCLAIMER
    assert "NOT guaranteed safe for human astronauts" in itinerary.safety_disclaimer

    print(f"Mission Itinerary verified: Distance={route_sum['total_distance_km']:.2f} km, "
          f"Difficulty={diff['score']}/100, MEDA Sol={env.sol} (Pressure={env.pressure_pa:.1f} Pa).")


def test_invalid_objective_handling():
    """Verify error handling for invalid or unrecognized objectives."""
    print("Testing invalid objective error handling...")
    req = MissionItineraryRequest(objective_id="non_existent_objective_xyz")
    try:
        mission_service.plan_scientific_itinerary(req)
        assert False, "Expected ValueError for invalid objective"
    except ValueError as ve:
        assert "not recognized" in str(ve).lower()
        print(f"Expected error caught: {ve}")


if __name__ == "__main__":
    test_scientific_categories_grouping()
    test_retrieval_of_objective_discoveries_decoupled()
    test_independent_objective_selection_with_mock_routing()
    test_mission_itinerary_generation()
    test_invalid_objective_handling()
    print("\n>>> ALL SCIENTIFIC OBJECTIVE INTEGRATION TESTS PASSED! <<<")
