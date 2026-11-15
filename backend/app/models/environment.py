from pydantic import BaseModel, Field
from typing import List, Optional

class SolEnvironmentReport(BaseModel):
    sol: int
    earth_date: str
    solar_longitude_ls: float  # Ls (0-360 deg) defines Martian season
    season_name: str
    pressure_pa: float
    temp_air_avg_c: float
    temp_air_min_c: float
    temp_air_max_c: float
    temp_ground_avg_c: float
    temp_ground_min_c: float
    temp_ground_max_c: float
    wind_speed_avg_ms: float
    wind_speed_max_ms: float
    wind_direction_deg: float
    dust_opacity_tau: float
    uv_index_max: float
    relative_humidity_pct: float
    survival_assessment: str
    eva_suit_warnings: List[str]
    rover_mobility_status: str
    pressure_provenance: Optional[str] = "PDS4 CAL_PS Calibrated Observation (NASA/JPL/CAB)"
    pressure_interpretation_status: Optional[str] = "VERIFIED SINGLE TRANSDUCER (Nominal NGM Barocap)"
    air_temp_provenance: Optional[str] = "PDS4 CAL_ATS 5-Sensor In-Situ Observation (NASA/JPL/CAB)"
    ground_temp_provenance: Optional[str] = "Model Estimate (Derived from regional surface thermal inertia)"
    wind_provenance: Optional[str] = "Model Estimate (Regional Martian Atmospheric Circulation Model)"
    dust_provenance: Optional[str] = "Model Estimate (Seasonal Optical Depth Climatology)"
    uv_provenance: Optional[str] = "Model Estimate (Top-of-Atmosphere Radiative Transfer)"
    data_authenticity_notice: Optional[str] = "Atmospheric pressure and air temperature are direct NASA PDS calibrated observations. Ground temperature, wind, dust tau, and UV are model estimates."

class EnvironmentTelemetryResponse(BaseModel):
    latest_sol: SolEnvironmentReport
    recent_sols: List[SolEnvironmentReport]
    source_attribution: str
