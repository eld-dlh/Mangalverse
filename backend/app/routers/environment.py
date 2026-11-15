from fastapi import APIRouter, HTTPException
from typing import List
from app.models.environment import SolEnvironmentReport, EnvironmentTelemetryResponse
from app.services.weather_service import weather_service

router = APIRouter(prefix="/api/environment", tags=["Environmental Telemetry"])

@router.get("/meda", response_model=EnvironmentTelemetryResponse)
def get_environmental_telemetry():
    """Retrieve the latest and historical NASA Mars 2020 MEDA atmospheric observations."""
    return weather_service.get_telemetry_package()

@router.get("/meda/{sol}", response_model=SolEnvironmentReport)
def get_sol_environment(sol: int):
    """Retrieve MEDA observations for a specific mission Sol."""
    report = weather_service.get_report_by_sol(sol)
    if not report:
        raise HTTPException(status_code=404, detail=f"No MEDA telemetry recorded for Sol {sol}.")
    return report
