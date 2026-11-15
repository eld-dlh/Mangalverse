from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CoordinatePoint(BaseModel):
    longitude: float
    latitude: float

class RouteCalculationRequest(BaseModel):
    start_point: Optional[List[float]] = None  # [lon, lat], defaults to Octavia E. Butler landing or current position
    destination_point: Optional[List[float]] = None  # [lon, lat]
    checkpoint_ids: Optional[List[str]] = Field(default_factory=list)
    objective_id: Optional[str] = None
    max_safe_slope_deg: float = 15.0  # Rover engineering safety limit
    avoid_sand_hazards: bool = True
    speed_kmh: float = 0.12  # Standard autonomous drive speed of Perseverance

class ElevationProfilePoint(BaseModel):
    distance_meters: float
    longitude: float
    latitude: float
    elevation_m: float
    slope_deg: float
    hazard_level: str  # "SAFE", "CAUTION", "CRITICAL"

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
    total_distance_km: float
    total_elevation_gain_m: float
    total_elevation_loss_m: float
    max_slope_deg: float
    avg_slope_deg: float
    estimated_drive_duration_hours: float
    estimated_energy_consumption_kwh: float
    path_geojson: Dict[str, Any]
    elevation_profile: List[ElevationProfilePoint]
    waypoints: List[RouteWaypoint]
    safety_warnings: List[str]
    algorithm_meta: Dict[str, Any]
