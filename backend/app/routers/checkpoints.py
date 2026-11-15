"""
API router for Mars surface exploration checkpoints and scientific targets.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.models.checkpoint import Checkpoint, CheckpointListResponse
from app.services.discovery_service import discovery_service

router = APIRouter(prefix="/api/checkpoints", tags=["Exploration Checkpoints"])

@router.get("", response_model=Any)
def list_checkpoints(
    objective_id: Optional[str] = Query(default=None, description="Filter by scientific objective ID (e.g. OBJ-1, OBJ-2)"),
    samples_only: bool = Query(default=False, description="Filter to checkpoints where samples were acquired"),
    format: str = Query(default="json", description="Response format: 'json' or 'geojson'")
):
    """
    Retrieve scientifically verified exploration checkpoints in Jezero Crater.
    Supports JSON list and GeoJSON FeatureCollection formats.
    """
    obj_id = objective_id if isinstance(objective_id, str) else None
    samples_flag = bool(samples_only) if isinstance(samples_only, bool) else False
    fmt = (format if isinstance(format, str) else "json").lower()

    if fmt == "geojson":
        return discovery_service.get_checkpoints_geojson(
            objective_id=obj_id,
            samples_only=samples_flag
        )

    return discovery_service.get_checkpoints(
        objective_id=obj_id,
        samples_only=samples_flag
    )

@router.get("/{checkpoint_id}", response_model=Checkpoint)
def get_checkpoint(checkpoint_id: str):
    """
    Retrieve specific checkpoint details, coordinates, geological formation, and sample status.
    """
    cp = discovery_service.get_checkpoint_by_id(checkpoint_id)
    if not cp:
        raise HTTPException(
            status_code=404,
            detail=f"Checkpoint '{checkpoint_id}' not found in scientific database."
        )
    return cp
