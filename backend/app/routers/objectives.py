from fastapi import APIRouter, HTTPException
from typing import List
from app.models.objective import ScientificObjective
from app.services.discovery_service import discovery_service

router = APIRouter(prefix="/api/objectives", tags=["Scientific Objectives"])

@router.get("", response_model=List[ScientificObjective])
def list_objectives():
    """Retrieve all verified NASA scientific exploration objectives."""
    return discovery_service.get_objectives()

@router.get("/{obj_id}", response_model=ScientificObjective)
def get_objective(obj_id: str):
    """Retrieve specific scientific objective details by ID."""
    obj = discovery_service.get_objective_by_id(obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Objective '{obj_id}' not found.")
    return obj
