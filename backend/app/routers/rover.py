import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.config import TRAVERSE_PATH, NASA_ATTRIBUTIONS

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
    """Retrieve current mission telemetry, total distance driven, and sample tally."""
    return {
        "mission_name": "Mars 2020 Perseverance Rover",
        "landing_site": "Octavia E. Butler Landing (Jezero Crater)",
        "coordinates": {
            "latitude": 18.4447,
            "longitude": 77.4508,
            "elevation_m": -2570.0
        },
        "mission_sol": 1230,
        "odometer_km": 28.5,
        "sealed_sample_tubes_count": 24,
        "surface_depot_tubes_deposited": 10,
        "status": "OPERATIONAL",
        "power_source": "Multi-Mission Radioisotope Thermoelectric Generator (MMRTG)",
        "source_attributions": NASA_ATTRIBUTIONS
    }
