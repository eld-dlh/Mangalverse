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
    in_bounds = jezero_dem_service.is_in_bounds(lon, lat)
    if not in_bounds:
        return {
            "longitude": lon,
            "latitude": lat,
            "elevation_meters": None,
            "ctx_elevation_meters": None,
            "hirise_elevation_meters": None,
            "primary_source": "Outside Jezero Crater DEM Coverage",
            "slope_degrees": None,
            "terrain_classification": "OUT_OF_BOUNDS",
            "terrain_model_note": "Coordinates fall outside the authentic USGS Jezero Crater DEM coverage boundary (~77.0°E-78.6°E, ~17.6°N-19.3°N).",
            "in_jezero_dem_bounds": False,
            "datum": "MOLA Areoid Datum (USGS/NASA)"
        }

    elev = jezero_dem_service.get_elevation_at(lon, lat)
    slope = jezero_dem_service.get_slope_at(lon, lat)
    terrain = jezero_dem_service.get_terrain_assessment(slope)
    hirise_elev = jezero_dem_service.get_hirise_elevation_at(lon, lat)

    res_elev = hirise_elev if (prefer_hirise and hirise_elev is not None) else (round(elev, 2) if elev is not None else None)
    source = "USGS Mars 2020 HiRISE DTM (1m/pixel)" if (prefer_hirise and hirise_elev is not None) else "USGS Mars 2020 CTX DEM (20m/pixel)"

    return {
        "longitude": lon,
        "latitude": lat,
        "elevation_meters": res_elev,
        "ctx_elevation_meters": round(elev, 2) if elev is not None else None,
        "hirise_elevation_meters": hirise_elev,
        "primary_source": source,
        "slope_degrees": round(slope, 2) if slope is not None else None,
        "terrain_classification": terrain["classification"],
        "terrain_model_note": terrain["model_note"],
        "in_jezero_dem_bounds": True,
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
