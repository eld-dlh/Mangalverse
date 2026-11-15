"""
Pydantic data models for Terrain-Aware Martian Surface Routing.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CoordinatePoint(BaseModel):
    longitude: float
    latitude: float

class RouteCalculationRequest(BaseModel):
    start_point: Optional[List[float]] = None  # [lon, lat], defaults to Octavia E. Butler landing
    destination_point: Optional[List[float]] = None  # [lon, lat]
    checkpoint_ids: Optional[List[str]] = Field(default_factory=list)
    checkpoint_coords: Optional[List[List[float]]] = None  # Direct coordinates [[lon, lat], ...]
    objective_id: Optional[str] = None
    preference: str = "BALANCED"  # SHORTEST, SAFEST, or BALANCED
    max_safe_slope_deg: float = 15.0  # Rover engineering safety limit (degrees)
    avoid_sand_hazards: bool = True
    speed_kmh: float = 0.12  # Standard autonomous drive speed of Perseverance (km/h)

class ElevationProfilePoint(BaseModel):
    distance_meters: float
    longitude: float
    latitude: float
    elevation_m: float
    slope_deg: float
    hazard_level: str  # "SLOPE_LOW", "SLOPE_MODERATE", "SLOPE_HIGH"
    terrain_classification: Optional[str] = None
    terrain_model_note: Optional[str] = None

class RouteWaypoint(BaseModel):
    id: str
    name: str
    longitude: float
    latitude: float
    elevation_m: float
    distance_from_start_m: float
    notes: str

class RouteCalculationResponse(BaseModel):
    status: str
    route_preference: Optional[str] = "BALANCED"
    total_distance_km: float
    total_elevation_gain_m: float
    total_elevation_loss_m: float
    max_slope_deg: float
    avg_slope_deg: float
    estimated_drive_duration_hours: float
    estimated_energy_consumption_kwh: float
    terrain_difficulty_score: Optional[float] = None
    terrain_difficulty_rating: Optional[str] = None
    path_geojson: Dict[str, Any]
    elevation_profile: List[ElevationProfilePoint]
    waypoints: List[RouteWaypoint]
    safety_warnings: List[str]
    safety_disclaimer: Optional[str] = None
    algorithm_meta: Dict[str, Any]
