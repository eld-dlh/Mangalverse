"""
Pydantic data models for Mars Exploration Mission Itineraries and Scientific Objectives.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ScientificCategorySummary(BaseModel):
    id: str
    code: str
    name: str
    description: str
    scientific_focus: str
    primary_instruments: List[str]
    discoveries_count: int
    discovery_ids: List[str]
    recommended_checkpoint_ids: List[str]
    citations: List[str]

class ItineraryDiscoveryLocation(BaseModel):
    id: str
    target_name: str
    sol: int
    earth_date: str
    latitude: float
    longitude: float
    elevation_m: float
    geological_formation: str
    lithology: str
    mineralogy_detected: List[str]
    sample_acquired: bool
    sample_name: Optional[str] = None
    scientific_significance: str
    companion_insight: str
    citation: str

class ItineraryEnvironmentalObservation(BaseModel):
    sol: int
    earth_date: str
    season_name: str
    solar_longitude_ls: float
    pressure_pa: float
    temp_air_avg_c: float
    temp_air_min_c: float
    temp_air_max_c: float
    temp_ground_avg_c: float
    dust_opacity_tau: float
    wind_speed_avg_ms: float
    survival_assessment: str
    eva_suit_warnings: List[str]
    instrument: str = "NASA Mars 2020 MEDA (Centro de Astrobiología / JPL)"

class MissionItineraryRequest(BaseModel):
    objective_id: str  # Can be objective ID ("OBJ-1") or category ("ancient_water")
    start_point: Optional[List[float]] = None  # [lon, lat], defaults to Octavia E. Butler Landing
    selected_checkpoint_ids: Optional[List[str]] = None  # Specific discoveries to visit in order
    preference: str = "BALANCED"  # SHORTEST, SAFEST, or BALANCED
    max_safe_slope_deg: float = 15.0
    avoid_sand_hazards: bool = True
    speed_kmh: float = 0.12

class MissionItineraryResponse(BaseModel):
    status: str
    mission_title: str
    selected_objective_id: str
    selected_objective_code: str
    selected_objective_title: str
    scientific_category: str
    scientific_rationale: str
    primary_instruments: List[str]
    discovery_locations: List[ItineraryDiscoveryLocation]
    checkpoint_order: List[Dict[str, Any]]
    route_summary: Dict[str, Any]
    terrain_difficulty: Dict[str, Any]
    environmental_observations: ItineraryEnvironmentalObservation
    source_references: Dict[str, Any]
    path_geojson: Dict[str, Any]
    safety_warnings: List[str]
    safety_disclaimer: str
