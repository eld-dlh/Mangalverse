"""
API router for NASA Mars 2020 MEDA environmental and atmospheric telemetry in Jezero Crater.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Any
from app.models.environment import SolEnvironmentReport, EnvironmentTelemetryResponse
from app.services.weather_service import weather_service
from app.config import NASA_ATTRIBUTIONS

router = APIRouter(prefix="/api/environment", tags=["Environmental Telemetry"])

@router.get("", response_model=Any)
def get_environment(
    sol: Optional[int] = Query(default=None, description="Optional Martian mission sol (e.g. 1200) to retrieve specific report"),
    format: str = Query(default="json", description="Response format: 'json' or 'geojson'")
):
    """
    Retrieve NASA Mars 2020 MEDA atmospheric and environmental telemetry.
    Returns latest and recent sols, or a specific sol when specified.
    Supports standard JSON and GeoJSON formats.
    """
    sol_val = sol if isinstance(sol, int) else None
    fmt = (format if isinstance(format, str) else "json").lower()

    if sol_val is not None:
        report = weather_service.get_report_by_sol(sol_val)
        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"No MEDA telemetry recorded for Sol {sol_val}."
            )
        if fmt == "geojson":
            return {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.4508, 18.4447]
                },
                "properties": {
                    "sol": report.sol,
                    "earth_date": report.earth_date,
                    "solar_longitude_ls": report.solar_longitude_ls,
                    "season_name": report.season_name,
                    "pressure_pa": report.pressure_pa,
                    "temp_air_avg_c": report.temp_air_avg_c,
                    "temp_air_min_c": report.temp_air_min_c,
                    "temp_air_max_c": report.temp_air_max_c,
                    "temp_ground_avg_c": report.temp_ground_avg_c,
                    "wind_speed_avg_ms": report.wind_speed_avg_ms,
                    "dust_opacity_tau": report.dust_opacity_tau,
                    "survival_assessment": report.survival_assessment,
                    "eva_suit_warnings": report.eva_suit_warnings,
                    "source_attribution": NASA_ATTRIBUTIONS["environmental_data"]["citation"]
                }
            }
        return report

    pkg = weather_service.get_telemetry_package()
    if fmt == "geojson":
        latest = pkg.latest_sol
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [77.4508, 18.4447]
            },
            "properties": {
                "latest_sol": latest.sol,
                "earth_date": latest.earth_date,
                "season_name": latest.season_name,
                "pressure_pa": latest.pressure_pa,
                "temp_air_avg_c": latest.temp_air_avg_c,
                "temp_ground_avg_c": latest.temp_ground_avg_c,
                "dust_opacity_tau": latest.dust_opacity_tau,
                "survival_assessment": latest.survival_assessment,
                "eva_suit_warnings": latest.eva_suit_warnings,
                "sols_reported_count": len(pkg.recent_sols),
                "source_attribution": pkg.source_attribution
            }
        }
    return pkg

@router.get("/meda", response_model=EnvironmentTelemetryResponse)
def get_environmental_telemetry():
    """Retrieve the latest and historical NASA Mars 2020 MEDA atmospheric observations."""
    return weather_service.get_telemetry_package()

@router.get("/meda/{sol}", response_model=SolEnvironmentReport)
def get_sol_environment_meda(sol: int):
    """Retrieve MEDA observations for a specific mission Sol."""
    report = weather_service.get_report_by_sol(sol)
    if not report:
        raise HTTPException(status_code=404, detail=f"No MEDA telemetry recorded for Sol {sol}.")
    return report

@router.get("/{sol}", response_model=SolEnvironmentReport)
def get_sol_environment(sol: int):
    """Retrieve MEDA observations for a specific mission Sol."""
    report = weather_service.get_report_by_sol(sol)
    if not report:
        raise HTTPException(status_code=404, detail=f"No MEDA telemetry recorded for Sol {sol}.")
    return report
