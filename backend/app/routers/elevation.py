from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any
from app.services.dem_service import jezero_dem_service

router = APIRouter(prefix="/api/elevation", tags=["Geospatial Elevation"])

@router.get("/point")
def get_elevation_point(
    lon: float = Query(..., description="Martian East Longitude (degrees)"),
    lat: float = Query(..., description="Martian Planetographic Latitude (degrees)"),
    prefer_hirise: bool = Query(True, description="Prefer high-resolution 1m HiRISE DTM where available")
):
    """Retrieve elevation and slope at specific coordinates in Jezero Crater."""
    elev = jezero_dem_service.get_elevation_at(lon, lat)
    slope = jezero_dem_service.get_slope_at(lon, lat)
    terrain = jezero_dem_service.get_terrain_assessment(slope)
    hirise_elev = jezero_dem_service.get_hirise_elevation_at(lon, lat)

    res_elev = hirise_elev if (prefer_hirise and hirise_elev is not None) else round(elev, 2)
    source = "USGS Mars 2020 HiRISE DTM (1m/pixel)" if (prefer_hirise and hirise_elev is not None) else "USGS Mars 2020 CTX DEM (20m/pixel)"

    return {
        "longitude": lon,
        "latitude": lat,
        "elevation_meters": res_elev,
        "ctx_elevation_meters": round(elev, 2),
        "hirise_elevation_meters": hirise_elev,
        "primary_source": source,
        "slope_degrees": round(slope, 2),
        "terrain_classification": terrain["classification"],
        "terrain_model_note": terrain["model_note"],
        "datum": "MOLA Areoid Datum (USGS/NASA)"
    }

@router.post("/profile")
def get_elevation_profile(
    coordinates: List[List[float]] = Body(..., description="List of [lon, lat] coordinates defining route"),
    samples: int = Query(100, ge=10, le=500)
):
    """Extract continuous elevation and slope profile along a route."""
    if len(coordinates) < 2:
        raise HTTPException(status_code=400, detail="Profile requires at least 2 coordinate pairs.")

    profile = jezero_dem_service.sample_elevation_profile(coordinates, num_samples=samples)
    return {
        "samples_count": len(profile),
        "total_distance_m": profile[-1]["distance_meters"] if profile else 0.0,
        "profile": profile
    }
