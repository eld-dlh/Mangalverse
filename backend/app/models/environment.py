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
    pressure_provenance: Optional[str] = "VERIFIED ORIGINAL DOWNLOAD"
    pressure_interpretation_status: Optional[str] = "VERIFIED SINGLE TRANSDUCER"

class EnvironmentTelemetryResponse(BaseModel):
    latest_sol: SolEnvironmentReport
    recent_sols: List[SolEnvironmentReport]
    source_attribution: str
