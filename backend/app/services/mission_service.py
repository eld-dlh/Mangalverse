"""
Scientific Objective and Mission Itinerary Service (MARS EXPLORER).
Decoupled mission planning layer connecting verified scientific objectives
and NASA discovery records with the terrain-aware route-planning engine.
"""

from typing import List, Dict, Any, Optional
from app.services.discovery_service import discovery_service
from app.services.weather_service import weather_service
from app.services.pathfinding import terrain_pathfinder, RoutePreference, ASTRONAUT_SAFETY_DISCLAIMER
from app.models.itinerary import (
    ScientificCategorySummary,
    ItineraryDiscoveryLocation,
    ItineraryEnvironmentalObservation,
    MissionItineraryResponse,
    MissionItineraryRequest
)
from app.config import NASA_ATTRIBUTIONS, JEZERO_BBOX

# Category definitions aligning with scientific themes
SCIENTIFIC_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "ancient_water": {
        "id": "ancient_water",
        "code": "OBJ-1",
        "name": "Ancient Water & Lacustrine Exploration",
        "description": "Investigate ancient lakebed sediments, deltaic foreset mudstones, and carbonate margin units for evidence of sustained lacustrine environments and biosignatures.",
        "scientific_focus": "Aqueous habitability, delta paleohydrology, clay/sulfate precipitation, organic carbon preservation.",
        "primary_instruments": ["SHERLOC", "PIXL", "SuperCam", "Mastcam-Z"],
        "discovery_ids": ["enchanted_lake", "wildcat_ridge", "bright_angel", "margin_unit", "kodiak_butte", "skinner_ridge"],
        "recommended_checkpoint_ids": ["enchanted_lake", "wildcat_ridge", "margin_unit", "bright_angel"],
        "citations": [
            "Farley et al., A lacustrine environment in Jezero crater, Mars, Science 377 (2022).",
            "Mangold et al., Perseverance reveals an ancient delta-lake system at Jezero, Science 374 (2021).",
            "Sharma et al., Diverse organic-mineral associations in Jezero crater, Nature 619 (2023)."
        ]
    },
    "geological_investigation": {
        "id": "geological_investigation",
        "code": "OBJ-2",
        "name": "Geological Investigation & Planetary Petrology",
        "description": "Examine crystalline volcanic basement rocks, igneous differentiation, impact shock excavation, and geochronological units across the Jezero crater floor.",
        "scientific_focus": "Magma evolution, crater floor petrogenesis, Máaz basaltic andesite, Séítah olivine cumulates, radiometric age baselines.",
        "primary_instruments": ["PIXL", "SuperCam", "Mastcam-Z"],
        "discovery_ids": ["octavia_butler", "roubion_bellegarde", "montdenier", "salette_issole", "belva_crater", "otis_peak"],
        "recommended_checkpoint_ids": ["octavia_butler", "roubion_bellegarde", "montdenier", "salette_issole"],
        "citations": [
            "Farley et al., Mars 2020 Mission Overview and Science Objectives, Space Sci Rev (2020).",
            "Scheller et al., Aqueous alteration in Séítah, Science 377 (2022).",
            "Wiens et al., The SuperCam Instrument Suite on the Mars 2020 Rover, Space Sci Rev (2021)."
        ]
    },
    "water_ice_resources": {
        "id": "water_ice_resources",
        "code": "OBJ-4",
        "name": "Hydrated Minerals & In-Situ Resources",
        "description": "Target hydrated sulfates, bound structural water in vivianite/magnesite, subsurface radar layers, and sample cache depots for in-situ resource utilization (ISRU) and Mars Sample Return.",
        "scientific_focus": "Hydrated minerals, structural H2O reserves, RIMFAX subsurface reflectors, sample tube preservation, surface cache logistics.",
        "primary_instruments": ["RIMFAX", "SHERLOC", "PIXL", "CacheCam"],
        "discovery_ids": ["bright_angel", "margin_unit", "wildcat_ridge", "three_forks"],
        "recommended_checkpoint_ids": ["montdenier", "wildcat_ridge", "three_forks", "bright_angel"],
        "citations": [
            "Hamran et al., Ground Penetrating Radar on Mars: RIMFAX Observations in Jezero, Science Advances (2022).",
            "Muirhead et al., Mars 2020 Sample and Caching Subsystem Design and Operations, IEEE Aerospace (2021)."
        ]
    },
    "atmospheric_dust": {
        "id": "atmospheric_dust",
        "code": "OBJ-MEDA",
        "name": "Atmospheric, Dust & Meteorological Observations",
        "description": "Survey meteorological boundary layer dynamics, diurnal pressure swings, atmospheric dust optical depth (tau), local wind vectors, and surface EVA suit survivability.",
        "scientific_focus": "Atmospheric dust storms, diurnal thermal extremes, atmospheric pressure cycles, wind stress, solar UV index.",
        "primary_instruments": ["MEDA (ATS, PS, TIRS, RDS, WS, HS)"],
        "discovery_ids": ["octavia_butler", "montdenier", "three_forks", "bright_angel"],
        "recommended_checkpoint_ids": ["octavia_butler", "montdenier", "three_forks"],
        "citations": [
            "Rodriguez-Manfredi et al., The Mars Environmental Dynamics Analyzer (MEDA) Instrument Suite, Space Sci Rev (2021).",
            "de la Torre Juarez et al., First Year of MEDA Meteorological Observations in Jezero, JGR Planets (2023)."
        ]
    }
}


class MissionService:
    """Coordinates scientific objectives with database records and routing."""

    def __init__(self, discoveries_svc=discovery_service, weather_svc=weather_service, pathfinder=terrain_pathfinder):
        self.discoveries_svc = discoveries_svc
        self.weather_svc = weather_svc
        self.pathfinder = pathfinder

    def get_categories(self) -> List[ScientificCategorySummary]:
        """List all supported scientific exploration categories with discovery counts."""
        categories = []
        for cat_id, cat_data in SCIENTIFIC_CATEGORIES.items():
            categories.append(ScientificCategorySummary(
                id=cat_id,
                code=cat_data["code"],
                name=cat_data["name"],
                description=cat_data["description"],
                scientific_focus=cat_data["scientific_focus"],
                primary_instruments=cat_data["primary_instruments"],
                discoveries_count=len(cat_data["discovery_ids"]),
                discovery_ids=cat_data["discovery_ids"],
                recommended_checkpoint_ids=cat_data["recommended_checkpoint_ids"],
                citations=cat_data["citations"]
            ))
        return categories

    def get_category_by_id(self, category_id: str) -> Optional[ScientificCategorySummary]:
        """Query scientific category by ID."""
        cat_key = category_id.lower().strip()
        if cat_key in SCIENTIFIC_CATEGORIES:
            d = SCIENTIFIC_CATEGORIES[cat_key]
            return ScientificCategorySummary(
                id=cat_key,
                code=d["code"],
                name=d["name"],
                description=d["description"],
                scientific_focus=d["scientific_focus"],
                primary_instruments=d["primary_instruments"],
                discoveries_count=len(d["discovery_ids"]),
                discovery_ids=d["discovery_ids"],
                recommended_checkpoint_ids=d["recommended_checkpoint_ids"],
                citations=d["citations"]
            )
        # Search by code
        for c_id, d in SCIENTIFIC_CATEGORIES.items():
            if d["code"].lower() == cat_key:
                return ScientificCategorySummary(
                    id=c_id,
                    code=d["code"],
                    name=d["name"],
                    description=d["description"],
                    scientific_focus=d["scientific_focus"],
                    primary_instruments=d["primary_instruments"],
                    discoveries_count=len(d["discovery_ids"]),
                    discovery_ids=d["discovery_ids"],
                    recommended_checkpoint_ids=d["recommended_checkpoint_ids"],
                    citations=d["citations"]
                )
        return None

    def get_discoveries_for_objective(self, objective_identifier: str) -> List[ItineraryDiscoveryLocation]:
        """
        Retrieve authentic discoveries and their Martian coordinates for a selected objective or category.
        """
        target_ids = []
        cat = self.get_category_by_id(objective_identifier)
        if cat:
            target_ids = cat.discovery_ids
        else:
            # Check official objective ID in database (e.g. "OBJ-1")
            obj = self.discoveries_svc.get_objective_by_id(objective_identifier.upper())
            if obj:
                # Get discoveries with primary_objective_id matching or recommended checkpoints
                discs = self.discoveries_svc.get_discoveries(objective_id=obj.id)
                target_ids = [d.id for d in discs] + obj.recommended_checkpoint_ids
                target_ids = list(dict.fromkeys(target_ids))

        # Retrieve authentic discovery objects from SQLite
        locations = []
        for disc_id in target_ids:
            d = self.discoveries_svc.get_discovery_by_id(disc_id)
            if d:
                locations.append(ItineraryDiscoveryLocation(
                    id=d.id,
                    target_name=d.target_name,
                    sol=d.sol,
                    earth_date=d.earth_date,
                    latitude=d.latitude,
                    longitude=d.longitude,
                    elevation_m=d.elevation_m,
                    geological_formation=d.geological_formation,
                    lithology=d.lithology,
                    mineralogy_detected=d.mineralogy_detected,
                    sample_acquired=d.sample_acquired,
                    sample_name=d.sample_name,
                    scientific_significance=d.scientific_summary,
                    companion_insight=d.companion_insight,
                    citation=d.nasa_pds_citation
                ))
        return locations

    def plan_scientific_itinerary(self, request: MissionItineraryRequest) -> MissionItineraryResponse:
        """
        Generate a complete mission itinerary centered on a scientific objective.
        Connects verified discovery targets into an ordered A* surface route,
        calculates terrain metrics, and pairs with authentic NASA MEDA environmental observations.
        """
        # 1. Resolve Objective and Category metadata
        cat = self.get_category_by_id(request.objective_id)
        db_obj = None
        if cat:
            obj_code = cat.code
            obj_title = cat.name
            obj_category = cat.name
            obj_rationale = cat.description
            instruments = cat.primary_instruments
            default_checkpoints = cat.recommended_checkpoint_ids
            citations = cat.citations
        else:
            db_obj = self.discoveries_svc.get_objective_by_id(request.objective_id.upper())
            if not db_obj:
                raise ValueError(
                    f"Objective '{request.objective_id}' not recognized. "
                    f"Supported categories: {', '.join(SCIENTIFIC_CATEGORIES.keys())} or DB IDs: OBJ-1, OBJ-2, OBJ-3, OBJ-4."
                )
            obj_code = db_obj.code
            obj_title = db_obj.title
            obj_category = db_obj.category
            obj_rationale = db_obj.scientific_rationale
            instruments = db_obj.primary_instruments
            default_checkpoints = db_obj.recommended_checkpoint_ids
            citations = [NASA_ATTRIBUTIONS["scientific_discoveries"]["citation"]]

        # 2. Determine ordered checkpoints from request or objective recommendations
        chosen_cids = request.selected_checkpoint_ids or default_checkpoints
        if not chosen_cids:
            chosen_cids = default_checkpoints

        # Retrieve discovery locations in exact requested sequence
        ordered_discovery_locations: List[ItineraryDiscoveryLocation] = []
        checkpoint_coords: List[List[float]] = []

        for cid in chosen_cids:
            d = self.discoveries_svc.get_discovery_by_id(cid)
            if d:
                loc = ItineraryDiscoveryLocation(
                    id=d.id,
                    target_name=d.target_name,
                    sol=d.sol,
                    earth_date=d.earth_date,
                    latitude=d.latitude,
                    longitude=d.longitude,
                    elevation_m=d.elevation_m,
                    geological_formation=d.geological_formation,
                    lithology=d.lithology,
                    mineralogy_detected=d.mineralogy_detected,
                    sample_acquired=d.sample_acquired,
                    sample_name=d.sample_name,
                    scientific_significance=d.scientific_summary,
                    companion_insight=d.companion_insight,
                    citation=d.nasa_pds_citation
                )
                ordered_discovery_locations.append(loc)
                checkpoint_coords.append([d.longitude, d.latitude])

        if len(checkpoint_coords) == 0:
            raise ValueError(f"No valid discovery checkpoints found for objective '{request.objective_id}'.")

        # 3. Define Route Origin and Destination
        # Default start is Octavia E. Butler Landing (77.4508, 18.4447)
        start_coord = request.start_point or [JEZERO_BBOX["center_lon"], JEZERO_BBOX["center_lat"]]

        # If more than 1 checkpoint, route starts at start_coord, traverses through checkpoints 0..n-2,
        # with the final checkpoint acting as destination target
        if len(checkpoint_coords) == 1:
            dest_coord = checkpoint_coords[0]
            intermediate_coords = []
        else:
            dest_coord = checkpoint_coords[-1]
            intermediate_coords = checkpoint_coords[:-1]

        # 4. Invoke Route-Planning Engine
        route_plan = self.pathfinder.plan_full_route(
            start_coord=start_coord,
            destination_coord=dest_coord,
            checkpoint_coords=intermediate_coords,
            preference=request.preference,
            max_safe_slope=request.max_safe_slope_deg,
            avoid_sand=request.avoid_sand_hazards,
            speed_kmh=request.speed_kmh
        )

        # 5. Retrieve Authentic Environmental Observations (MEDA)
        # Query latest Sol report from weather service
        meda_report = self.weather_svc.get_latest_report()
        env_obs = ItineraryEnvironmentalObservation(
            sol=meda_report.sol,
            earth_date=meda_report.earth_date,
            season_name=meda_report.season_name,
            solar_longitude_ls=meda_report.solar_longitude_ls,
            pressure_pa=meda_report.pressure_pa,
            temp_air_avg_c=meda_report.temp_air_avg_c,
            temp_air_min_c=meda_report.temp_air_min_c,
            temp_air_max_c=meda_report.temp_air_max_c,
            temp_ground_avg_c=meda_report.temp_ground_avg_c,
            dust_opacity_tau=meda_report.dust_opacity_tau,
            wind_speed_avg_ms=meda_report.wind_speed_avg_ms,
            survival_assessment=meda_report.survival_assessment,
            eva_suit_warnings=meda_report.eva_suit_warnings
        )

        # 6. Format Checkpoint Ordering Table
        checkpoint_order_list = []
        for idx, loc in enumerate(ordered_discovery_locations):
            checkpoint_order_list.append({
                "sequence_number": idx + 1,
                "discovery_id": loc.id,
                "name": loc.target_name,
                "sol_discovered": loc.sol,
                "coordinates": [loc.longitude, loc.latitude],
                "elevation_m": loc.elevation_m,
                "formation": loc.geological_formation,
                "sample_acquired": loc.sample_acquired,
                "sample_name": loc.sample_name
            })

        # 7. Compile Final Mission Itinerary
        itinerary = MissionItineraryResponse(
            status=route_plan["status"],
            mission_title=f"Scientific Expedition: {obj_title}",
            selected_objective_id=cat.id if cat else db_obj.id,
            selected_objective_code=obj_code,
            selected_objective_title=obj_title,
            scientific_category=obj_category,
            scientific_rationale=obj_rationale,
            primary_instruments=instruments,
            discovery_locations=ordered_discovery_locations,
            checkpoint_order=checkpoint_order_list,
            route_summary={
                "total_distance_km": route_plan["total_distance_km"],
                "total_elevation_gain_m": route_plan["total_elevation_gain_m"],
                "total_elevation_loss_m": route_plan["total_elevation_loss_m"],
                "estimated_duration_hours": route_plan["estimated_drive_duration_hours"],
                "estimated_energy_kwh": route_plan["estimated_energy_consumption_kwh"],
                "max_slope_deg": route_plan["max_slope_deg"],
                "avg_slope_deg": route_plan["avg_slope_deg"],
                "route_preference": route_plan["route_preference"]
            },
            terrain_difficulty={
                "score": route_plan["terrain_difficulty_score"],
                "rating": route_plan["terrain_difficulty_rating"],
                "model_note": "Calculated via CTX DEM slope magnitude, roughness, and Séítah aeolian hazard proximity."
            },
            environmental_observations=env_obs,
            source_references={
                "topography": NASA_ATTRIBUTIONS["topography"]["citation"],
                "scientific_records": citations,
                "atmospheric_data": NASA_ATTRIBUTIONS["environmental_data"]["citation"],
                "rover_traverse": NASA_ATTRIBUTIONS["rover_traverse"]["citation"]
            },
            path_geojson=route_plan["path_geojson"],
            safety_warnings=route_plan["safety_warnings"],
            safety_disclaimer=ASTRONAUT_SAFETY_DISCLAIMER
        )

        return itinerary


# Singleton instance
mission_service = MissionService()
