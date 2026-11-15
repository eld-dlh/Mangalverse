"""
API router for NASA Mars 2020 scientific discoveries and geological targets in Jezero Crater.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.models.discovery import ScientificDiscovery
from app.services.discovery_service import discovery_service

router = APIRouter(prefix="/api/discoveries", tags=["Scientific Discoveries"])

@router.get("", response_model=Any)
def list_discoveries(
    objective_id: Optional[str] = Query(None, description="Filter by scientific objective ID (e.g. OBJ-1)"),
    samples_only: bool = Query(False, description="Filter to locations where rock/atmospheric samples were extracted"),
    search: Optional[str] = Query(None, description="Search query across targets, lithology, and minerals"),
    format: str = Query("json", description="Response format: 'json' or 'geojson'")
):
    """
    List verified NASA Perseverance scientific discoveries and geological targets.
    Supports filtering by objective, sample acquisition, and keyword search.
    Supports JSON list and GeoJSON FeatureCollection formats.
    """
    obj_id = objective_id if isinstance(objective_id, str) else None
    samples_flag = bool(samples_only) if isinstance(samples_only, bool) else False
    search_q = search if isinstance(search, str) else None

    if format.lower() == "geojson":
        return discovery_service.get_discoveries_geojson(objective_id=obj_id)

    return discovery_service.get_discoveries(
        objective_id=obj_id,
        samples_only=samples_flag,
        search_query=search_q
    )

@router.get("/geojson")
def get_discoveries_geojson(
    objective_id: Optional[str] = Query(None, description="Filter by scientific objective ID")
) -> Dict[str, Any]:
    """Export verified discoveries as a GeoJSON FeatureCollection for interactive maps."""
    obj_id = objective_id if isinstance(objective_id, str) else None
    return discovery_service.get_discoveries_geojson(objective_id=obj_id)

@router.get("/{disc_id}", response_model=ScientificDiscovery)
def get_discovery(disc_id: str):
    """Retrieve detailed scientific analysis, mineralogy, and instrument detections for a target."""
    disc = discovery_service.get_discovery_by_id(disc_id)
    if not disc:
        raise HTTPException(
            status_code=404,
            detail=f"Discovery '{disc_id}' not found in scientific database."
        )
    return disc
