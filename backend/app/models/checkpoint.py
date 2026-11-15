"""
Pydantic data models for Mars surface route checkpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Checkpoint(BaseModel):
    id: str
    name: str
    sol: int
    earth_date: str
    latitude: float
    longitude: float
    elevation_m: float
    geological_formation: str
    lithology: str
    instruments: List[str]
    scientific_summary: str
    sample_acquired: bool
    sample_name: Optional[str] = None
    sample_tube_serial: Optional[str] = None
    cache_status: str
    primary_objective_id: str
    recommended_for_objectives: List[str] = Field(default_factory=list)
    companion_insight: str
    nasa_pds_citation: str

class CheckpointListResponse(BaseModel):
    count: int
    checkpoints: List[Checkpoint]
    target_region: str = "Jezero Crater, Mars"
