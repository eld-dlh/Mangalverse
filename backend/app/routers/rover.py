import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.config import TRAVERSE_PATH, NASA_ATTRIBUTIONS, ROVER_STATUS_CONFIG

router = APIRouter(prefix="/api/rover", tags=["Perseverance Telemetry & Traverse"])

@router.get("/traverse")
def get_rover_traverse() -> Dict[str, Any]:
    """Retrieve official NASA Mars 2020 Perseverance Rover historical traverse GeoJSON."""
    if not TRAVERSE_PATH.exists():
        raise HTTPException(status_code=404, detail="Traverse GeoJSON not found on server.")
    with open(TRAVERSE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/status")
def get_rover_status() -> Dict[str, Any]:
    """Retrieve mission reference data, total distance driven, and sample tally.
    
    Data is sourced from the NASA PDS archive snapshot documented in config.py.
    This is NOT real-time telemetry.
    """
    return {
        **ROVER_STATUS_CONFIG,
        "source_attributions": NASA_ATTRIBUTIONS,
    }
