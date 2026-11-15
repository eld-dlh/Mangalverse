"""
API router for NASA Mars 2020 scientific objectives in Jezero Crater.
Integrates scientific goals with the route-planning engine.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Any
from app.models.objective import ScientificObjective
from app.models.itinerary import (
    ScientificCategorySummary,
    ItineraryDiscoveryLocation,
    MissionItineraryRequest,
    MissionItineraryResponse
)
from app.services.discovery_service import discovery_service
from app.services.mission_service import mission_service

router = APIRouter(prefix="/api/objectives", tags=["Scientific Objectives"])

@router.get("", response_model=Any)
def list_objectives(
    format: str = Query(default="json", description="Response format: 'json' or 'geojson'")
):
    """
    Retrieve all verified NASA scientific exploration objectives.
    Supports JSON list and GeoJSON summary formats.
    """
    fmt = (format if isinstance(format, str) else "json").lower()
    objectives = discovery_service.get_objectives()
    if fmt == "geojson":
        features = []
        for obj in objectives:
            features.append({
                "type": "Feature",
                "geometry": None,
                "properties": {
                    "id": obj.id,
                    "code": obj.code,
                    "title": obj.title,
                    "category": obj.category,
                    "description": obj.description,
                    "scientific_rationale": obj.scientific_rationale,
                    "primary_instruments": obj.primary_instruments,
                    "target_formations": obj.target_formations,
                    "recommended_checkpoint_ids": obj.recommended_checkpoint_ids,
                    "biosignature_relevance": obj.biosignature_relevance
                }
            })
        return {
            "type": "FeatureCollection",
            "metadata": {
                "source": "NASA Mars 2020 Mission Science Objectives",
                "count": len(features)
            },
            "features": features
        }
    return objectives

@router.get("/categories", response_model=List[ScientificCategorySummary])
def list_scientific_categories():
    """
    Retrieve scientific exploration categories:
    - Ancient water
    - Geological investigation
    - Water ice and resources
    - Atmospheric and dust observations
    Includes descriptions, target formations, and associated discovery targets.
    """
    return mission_service.get_categories()

@router.get("/{obj_id}", response_model=Any)
def get_objective(obj_id: str):
    """Retrieve specific scientific objective or category details by ID."""
    # Check category first
    cat = mission_service.get_category_by_id(obj_id)
    if cat:
        return cat

    obj = discovery_service.get_objective_by_id(obj_id.upper())
    if not obj:
        raise HTTPException(
            status_code=404,
            detail=f"Objective '{obj_id}' not found in scientific database."
        )
    return obj

@router.get("/{obj_id}/discoveries", response_model=List[ItineraryDiscoveryLocation])
def get_objective_discoveries(obj_id: str):
    """
    Retrieve relevant scientific discoveries and their coordinates for a selected objective.
    """
    locations = mission_service.get_discoveries_for_objective(obj_id)
    if not locations:
        raise HTTPException(
            status_code=404,
            detail=f"No discoveries found for objective '{obj_id}'."
        )
    return locations

@router.post("/plan", response_model=MissionItineraryResponse)
def plan_objective_itinerary(request: MissionItineraryRequest):
    """
    Plan a complete scientific expedition route around a selected scientific objective.
    Routes through relevant discovery checkpoints in requested sequence and compiles
    route summary, transparent terrain difficulty, and NASA MEDA environmental telemetry.
    """
    try:
        return mission_service.plan_scientific_itinerary(request)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Itinerary planning error: {str(e)}")
