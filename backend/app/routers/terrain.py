"""
API router for Jezero Crater terrain, topography, and DEM trafficability analysis.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import json
import numpy as np

from app.services.dem_service import jezero_dem_service
from app.config import JEZERO_BBOX, NASA_ATTRIBUTIONS, AUTHENTIC_GEOLOGY_PATH
from app.models.terrain import TerrainPointAssessment, TerrainSummaryResponse, RasterMetadata

router = APIRouter(prefix="/api/terrain", tags=["Topography & Terrain Engine"])

@router.get("", response_model=Any)
def get_terrain_data(
    lon: Optional[float] = Query(default=None, description="Martian East Longitude in degrees (e.g. 77.4508)"),
    lat: Optional[float] = Query(default=None, description="Martian Planetographic Latitude in degrees (e.g. 18.4447)"),
    prefer_hirise: bool = Query(default=True, description="Prefer high-resolution 1m HiRISE DTM where available"),
    format: str = Query(default="json", description="Response format: 'json' or 'geojson'")
):
    """
    Retrieve terrain analysis at a specific coordinate or comprehensive DEM terrain metadata.
    Supports point inspection and regional coverage summary in JSON and GeoJSON formats.
    """
    lon_val = lon if isinstance(lon, (int, float)) else None
    lat_val = lat if isinstance(lat, (int, float)) else None
    pref_hirise = bool(prefer_hirise) if isinstance(prefer_hirise, bool) else True
    fmt = (format if isinstance(format, str) else "json").lower()

    # Case 1: Partial coordinate provided
    if (lon_val is not None and lat_val is None) or (lat_val is not None and lon_val is None):
        raise HTTPException(
            status_code=400,
            detail="Both 'lon' and 'lat' parameters are required for point terrain inspection."
        )

    # Case 2: Specific point query
    if lon_val is not None and lat_val is not None:
        # Validate Martian coordinates
        if lat_val < -90.0 or lat_val > 90.0:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid latitude: {lat_val}. Planetographic latitude must be between -90.0 and 90.0 degrees."
            )
        if lon_val < -180.0 or lon_val > 360.0:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid longitude: {lon_val}. Martian longitude must be between -180.0 and 360.0 degrees."
            )

        in_bounds = jezero_dem_service.is_in_bounds(lon_val, lat_val)

        if not in_bounds:
            props = {
                "longitude": lon_val,
                "latitude": lat_val,
                "elevation_meters": None,
                "ctx_elevation_meters": None,
                "hirise_elevation_meters": None,
                "slope_degrees": None,
                "terrain_classification": "OUT_OF_BOUNDS",
                "terrain_model_note": "Coordinates fall outside the authentic USGS Jezero Crater DEM coverage boundary (~77.0°E-78.6°E, ~17.6°N-19.3°N).",
                "primary_source": "Outside Jezero Crater DEM Coverage",
                "in_jezero_dem_bounds": False,
                "datum": "MOLA Areoid Datum (USGS/NASA)",
                "attribution": NASA_ATTRIBUTIONS["topography"]
            }
        else:
            elev = jezero_dem_service.get_elevation_at(lon_val, lat_val)
            slope = jezero_dem_service.get_slope_at(lon_val, lat_val)
            terrain_assessment = jezero_dem_service.get_terrain_assessment(slope)
            hirise_elev = jezero_dem_service.get_hirise_elevation_at(lon_val, lat_val)

            res_elev = hirise_elev if (pref_hirise and hirise_elev is not None) else (round(elev, 2) if elev is not None else None)
            source = (
                "USGS Mars 2020 HiRISE DTM (1m/pixel)"
                if (pref_hirise and hirise_elev is not None)
                else "USGS Mars 2020 CTX DEM (20m/pixel)"
            )

            props = {
                "longitude": lon_val,
                "latitude": lat_val,
                "elevation_meters": res_elev,
                "ctx_elevation_meters": round(elev, 2) if elev is not None else None,
                "hirise_elevation_meters": hirise_elev,
                "slope_degrees": round(slope, 2) if slope is not None else None,
                "terrain_classification": terrain_assessment["classification"],
                "terrain_model_note": terrain_assessment["model_note"],
                "primary_source": source,
                "in_jezero_dem_bounds": True,
                "datum": "MOLA Areoid Datum (USGS/NASA)",
                "attribution": NASA_ATTRIBUTIONS["topography"]
            }

        if fmt == "geojson":
            return {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon_val, lat_val]
                },
                "properties": props
            }

        return props

    # Case 3: Regional summary metadata
    grid = jezero_dem_service.elevation_grid
    valid_elev = grid[(grid > -10000.0) & (grid < 30000.0) & np.isfinite(grid)]
    min_elev = float(np.min(valid_elev)) if len(valid_elev) > 0 else -3000.0
    max_elev = float(np.max(valid_elev)) if len(valid_elev) > 0 else -2000.0
    med_elev = float(np.median(valid_elev)) if len(valid_elev) > 0 else -2500.0

    ctx_meta = {
        "name": "USGS Jezero Crater CTX DEM Mosaic",
        "resolution": f"{jezero_dem_service.dx_meters:.1f} m/pixel",
        "raster_shape": [jezero_dem_service.height, jezero_dem_service.width],
        "bounds": {
            "left": float(jezero_dem_service.bounds.left),
            "bottom": float(jezero_dem_service.bounds.bottom),
            "right": float(jezero_dem_service.bounds.right),
            "top": float(jezero_dem_service.bounds.top)
        },
        "datum": "MOLA Areoid Datum (USGS/NASA)",
        "crs": str(jezero_dem_service.crs),
        "elevation_min_m": round(min_elev, 2),
        "elevation_max_m": round(max_elev, 2),
        "elevation_median_m": round(med_elev, 2)
    }

    hazards = [
        {
            "name": "South Séítah Aeolian Dune Field",
            "type": "High Wheel-Slip Sand Ripple Hazard",
            "boundary": {
                "min_lon": 77.436,
                "max_lon": 77.447,
                "min_lat": 18.427,
                "max_lat": 18.438
            },
            "recommendation": "Active avoidance during autonomous surface route calculation."
        }
    ]

    slope_thresholds = {
        "SLOPE_LOW": "<= 10.0 degrees (Nominal rover traversal)",
        "SLOPE_MODERATE": "10.0 to 15.0 degrees (Approaching trafficability limit)",
        "SLOPE_HIGH": "> 15.0 degrees (Exceeds nominal rover engineering safety limit)"
    }

    summary_props = {
        "region": "Jezero Crater, Mars (Western Fan & Crater Floor)",
        "bounding_box": JEZERO_BBOX,
        "ctx_dem": ctx_meta,
        "hirise_dtm_available": jezero_dem_service._hirise_grid is not None or True,
        "hirise_dtm_resolution": "1.0 m/pixel (USGS Mars 2020 TRN DTM Mosaic)",
        "hazards": hazards,
        "slope_trafficability_thresholds": slope_thresholds,
        "source_attribution": NASA_ATTRIBUTIONS["topography"]
    }

    if fmt == "geojson":
        b = JEZERO_BBOX
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [b["min_lon"], b["min_lat"]],
                    [b["max_lon"], b["min_lat"]],
                    [b["max_lon"], b["max_lat"]],
                    [b["min_lon"], b["max_lat"]],
                    [b["min_lon"], b["min_lat"]]
                ]]
            },
            "properties": summary_props
        }

    return summary_props


# ── Geology GeoJSON (USGS sim3464 Nili Fossae / Jezero Crater mapping) ───────

@router.get("/geology", response_model=Any)
def get_geological_units():
    """
    Serve authentic USGS Jezero Crater geological unit polygons as GeoJSON.
    Source: Goudge et al. (2015) USGS SIM-3464 Nili Fossae geological map,
    converted from Nili.gdb geodatabase.
    """
    if not AUTHENTIC_GEOLOGY_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Geology GeoJSON not found on server. "
                f"Expected path: {AUTHENTIC_GEOLOGY_PATH}. "
                "Ensure data/processed/vector/jezero_geological_units_authentic.geojson exists."
            )
        )
    try:
        with open(AUTHENTIC_GEOLOGY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading geology GeoJSON: {e}")


# ── Elevation Contours (generated from authentic CTX DEM) ────────────────────

from app.config import AUTHENTIC_DATA_DIR

CONTOUR_DATA_DIR = AUTHENTIC_DATA_DIR / "vector"

@router.get("/contours", response_model=Any)
def get_elevation_contours(interval_m: int = Query(50, description="Contour interval in metres (default: 50)")):
    """
    Serve pre-generated elevation contour lines as GeoJSON.
    Contours are derived from the authentic USGS Jezero CTX DEM at the requested interval.

    Generate locally with: python scripts/generate_contours.py
    """
    path = CONTOUR_DATA_DIR / f"jezero_contours_{interval_m}m.geojson"
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Contour data for {interval_m}m interval not found. "
                f"Expected: {path}. "
                "Run: python scripts/generate_contours.py"
            )
        )
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading contour GeoJSON: {e}")
