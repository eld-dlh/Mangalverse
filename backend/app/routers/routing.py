from fastapi import APIRouter, HTTPException
from typing import List
from app.models.route import RouteCalculationRequest, RouteCalculationResponse
from app.services.pathfinding import terrain_pathfinder
from app.services.discovery_service import discovery_service
from app.config import JEZERO_BBOX

router = APIRouter(prefix="/api/route", tags=["Terrain-Aware Pathfinding"])

@router.post("/calculate", response_model=RouteCalculationResponse)
def calculate_route(request: RouteCalculationRequest):
    """
    Calculate terrain-aware surface traverse across Jezero Crater using A* pathfinding
    over Rasterio/NumPy DEM slope model.
    """
    # Default start point is Octavia E. Butler Landing if omitted
    start_point = request.start_point or [JEZERO_BBOX["center_lon"], JEZERO_BBOX["center_lat"]]

    # Collect checkpoint coordinates
    checkpoint_coords = []
    if request.checkpoint_ids:
        for cid in request.checkpoint_ids:
            disc = discovery_service.get_discovery_by_id(cid)
            if disc:
                checkpoint_coords.append([disc.longitude, disc.latitude])

    # If destination omitted but checkpoints provided, final checkpoint is destination
    destination = request.destination_point
    if not destination and checkpoint_coords:
        destination = checkpoint_coords.pop()
    elif not destination:
        # Default destination to Wildcat Ridge if nothing selected
        destination = [77.4042, 18.4485]

    try:
        route_result = terrain_pathfinder.plan_full_route(
            start_coord=start_point,
            destination_coord=destination,
            checkpoint_coords=checkpoint_coords,
            max_safe_slope=request.max_safe_slope_deg,
            avoid_sand=request.avoid_sand_hazards,
            speed_kmh=request.speed_kmh
        )
        return route_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route calculation error: {str(e)}")
