"""
Pydantic data models for Jezero Crater terrain and topographic data.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TerrainPointAssessment(BaseModel):
    longitude: float
    latitude: float
    elevation_meters: float
    ctx_elevation_meters: float
    hirise_elevation_meters: Optional[float] = None
    slope_degrees: float
    terrain_classification: str
    terrain_model_note: str
    primary_source: str
    in_jezero_dem_bounds: bool
    datum: str = "MOLA Areoid Datum (USGS/NASA)"
    attribution: Dict[str, Any]

class RasterMetadata(BaseModel):
    name: str
    resolution: str
    raster_shape: List[int]
    bounds: Dict[str, float]
    datum: str
    crs: str
    elevation_min_m: float
    elevation_max_m: float
    elevation_median_m: float

class TerrainSummaryResponse(BaseModel):
    region: str
    bounding_box: Dict[str, float]
    ctx_dem: RasterMetadata
    hirise_dtm_available: bool
    hirise_dtm_resolution: str
    hazards: List[Dict[str, Any]]
    slope_trafficability_thresholds: Dict[str, str]
    source_attribution: Dict[str, Any]
