from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ScientificDiscovery(BaseModel):
    id: str
    target_name: str
    sol: int
    earth_date: str
    latitude: float
    longitude: float
    elevation_m: float
    geological_formation: str
    lithology: str
    instruments: List[str]
    scientific_summary: str
    mineralogy_detected: List[str]
    biosignature_potential: str
    sample_acquired: bool
    sample_name: Optional[str] = None
    sample_tube_serial: Optional[str] = None
    cache_status: str
    primary_objective_id: str
    nasa_pds_citation: str
    companion_insight: str  # Contextual narrative for Virtual Companion in Explorer Mode

class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [lon, lat]

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: Dict[str, Any]

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
