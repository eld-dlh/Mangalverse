"""
API router for Terrain-Aware A* Surface Route Planning across Jezero Crater.
Integrates terrain analysis with scientific objectives and mission itineraries.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Any
from app.models.route import RouteCalculationRequest, RouteCalculationResponse
from app.models.itinerary import MissionItineraryRequest, MissionItineraryResponse
from app.services.pathfinding import terrain_pathfinder, RoutePreference
from app.services.discovery_service import discovery_service
from app.services.mission_service import mission_service
from app.config import JEZERO_BBOX

router = APIRouter(tags=["Terrain-Aware Pathfinding"])

def _validate_and_plan_route(request: RouteCalculationRequest, format_type: str = "json") -> Any:
    """Internal validator and execution engine for route planning."""
    # 1. Validate route preference
    pref_str = (request.preference or "BALANCED").strip().upper()
    valid_prefs = [p.value for p in RoutePreference]
    if pref_str not in valid_prefs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid route preference: '{request.preference}'. Allowed options: {', '.join(valid_prefs)}."
        )

    # 2. Validate max slope
    if request.max_safe_slope_deg < 1.0 or request.max_safe_slope_deg > 45.0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid max_safe_slope_deg: {request.max_safe_slope_deg}. Must be between 1.0 and 45.0 degrees."
        )

    # 3. Validate speed
    if request.speed_kmh <= 0.0 or request.speed_kmh > 5.0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid speed_kmh: {request.speed_kmh}. Must be between 0.01 and 5.0 km/h."
        )

    # 4. Validate start_point
    start_point = request.start_point or [JEZERO_BBOX["center_lon"], JEZERO_BBOX["center_lat"]]
    if not isinstance(start_point, (list, tuple)) or len(start_point) != 2:
        raise HTTPException(
            status_code=400,
            detail="start_point must be a 2-element coordinate list [longitude, latitude]."
        )
    s_lon, s_lat = start_point[0], start_point[1]
    if s_lat < -90.0 or s_lat > 90.0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid start_point latitude: {s_lat}. Must be between -90.0 and 90.0 degrees."
        )
    if s_lon < -180.0 or s_lon > 360.0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid start_point longitude: {s_lon}. Must be between -180.0 and 360.0 degrees."
        )

    # 5. Checkpoints: resolve from request or objective recommendations
    checkpoint_coords = []
    checkpoint_ids = list(request.checkpoint_ids or [])

    # If objective_id supplied and no checkpoints specified, pull objective checkpoints
    if request.objective_id and not checkpoint_ids and not request.checkpoint_coords:
        cat = mission_service.get_category_by_id(request.objective_id)
        if cat:
            checkpoint_ids = cat.recommended_checkpoint_ids
        else:
            db_obj = discovery_service.get_objective_by_id(request.objective_id.upper())
            if db_obj:
                checkpoint_ids = db_obj.recommended_checkpoint_ids

    if checkpoint_ids:
        for cid in checkpoint_ids:
            disc = discovery_service.get_discovery_by_id(cid)
            if not disc:
                raise HTTPException(
                    status_code=400,
                    detail=f"Checkpoint '{cid}' not found in scientific discoveries database."
                )
            checkpoint_coords.append([disc.longitude, disc.latitude])

    if request.checkpoint_coords:
        for idx, cp in enumerate(request.checkpoint_coords):
            if not isinstance(cp, (list, tuple)) or len(cp) != 2:
                raise HTTPException(
                    status_code=400,
                    detail=f"checkpoint_coords[{idx}] must be a 2-element list [longitude, latitude]."
                )
            if cp[1] < -90.0 or cp[1] > 90.0 or cp[0] < -180.0 or cp[0] > 360.0:
                raise HTTPException(
                    status_code=400,
                    detail=f"checkpoint_coords[{idx}] coordinates [{cp[0]}, {cp[1]}] out of valid Martian bounds."
                )
            checkpoint_coords.append([cp[0], cp[1]])

    # 6. Validate destination_point
    destination = request.destination_point
    if destination is not None:
        if not isinstance(destination, (list, tuple)) or len(destination) != 2:
            raise HTTPException(
                status_code=400,
                detail="destination_point must be a 2-element coordinate list [longitude, latitude]."
            )
        d_lon, d_lat = destination[0], destination[1]
        if d_lat < -90.0 or d_lat > 90.0:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid destination_point latitude: {d_lat}. Must be between -90.0 and 90.0 degrees."
            )
        if d_lon < -180.0 or d_lon > 360.0:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid destination_point longitude: {d_lon}. Must be between -180.0 and 360.0 degrees."
            )
    elif checkpoint_coords:
        destination = checkpoint_coords.pop()
    else:
        # Default destination to Wildcat Ridge if nothing selected
        destination = [77.4042, 18.4485]

    try:
        route_result = terrain_pathfinder.plan_full_route(
            start_coord=start_point,
            destination_coord=destination,
            checkpoint_coords=checkpoint_coords,
            preference=pref_str,
            max_safe_slope=request.max_safe_slope_deg,
            avoid_sand=request.avoid_sand_hazards,
            speed_kmh=request.speed_kmh
        )

        if format_type.lower() == "geojson":
            return route_result["path_geojson"]

        return route_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route calculation engine error: {str(e)}")

# Standard endpoints: POST /api/routes and POST /api/route/calculate
@router.post("/api/routes", response_model=Any)
def plan_routes(
    request: RouteCalculationRequest,
    format: str = Query("json", description="Response format: 'json' or 'geojson'")
):
    """
    Plan terrain-aware surface traverse across Jezero Crater using Rasterio/NumPy A* pathfinding.
    Supports route preferences (SHORTEST, SAFEST, BALANCED), checkpoint sequencing, and GeoJSON export.
    """
    return _validate_and_plan_route(request, format_type=format)

@router.post("/api/routes/itinerary", response_model=MissionItineraryResponse)
def plan_route_itinerary(request: MissionItineraryRequest):
    """
    Generate a full scientific mission itinerary connecting an objective,
    its discovery checkpoints, A* terrain route, and NASA MEDA environmental observations.
    """
    try:
        return mission_service.plan_scientific_itinerary(request)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Itinerary error: {str(e)}")

@router.post("/api/route/calculate", response_model=RouteCalculationResponse)
def calculate_route_legacy(request: RouteCalculationRequest):
    """Legacy route calculation endpoint for existing frontend integration."""
    return _validate_and_plan_route(request, format_type="json")

@router.post("/api/routes/calculate", response_model=RouteCalculationResponse)
def calculate_routes_alias(request: RouteCalculationRequest):
    """Alias for route calculation."""
    return _validate_and_plan_route(request, format_type="json")
