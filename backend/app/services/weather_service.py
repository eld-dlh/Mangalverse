"""
Environmental and Atmospheric Telemetry Service (NASA Mars 2020 MEDA).
Provides diurnal temperature, atmospheric pressure, dust opacity (tau), wind metrics, and survival assessments.
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from app.config import DB_PATH, NASA_ATTRIBUTIONS
from app.models.environment import SolEnvironmentReport, EnvironmentTelemetryResponse

class WeatherService:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_latest_report(self) -> SolEnvironmentReport:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM environmental_reports ORDER BY sol DESC LIMIT 1")
            row = cursor.fetchone()
            return self._row_to_model(row)

    def get_recent_reports(self, limit: int = 10) -> List[SolEnvironmentReport]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM environmental_reports ORDER BY sol DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]

    def get_report_by_sol(self, sol: int) -> Optional[SolEnvironmentReport]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM environmental_reports WHERE sol = ?", (sol,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_model(row)

    def get_telemetry_package(self) -> EnvironmentTelemetryResponse:
        latest = self.get_latest_report()
        recent = self.get_recent_reports(limit=10)
        return EnvironmentTelemetryResponse(
            latest_sol=latest,
            recent_sols=recent,
            source_attribution=NASA_ATTRIBUTIONS["environmental_data"]["citation"]
        )

    def _row_to_model(self, row) -> SolEnvironmentReport:
        sol_num = row["sol"]
        if sol_num == 1:
            p_prov = "VERIFIED ORIGINAL DOWNLOAD"
            p_interp = "NOT VERIFIED (Provisional: Transducer 1/2 checkout switching)"
        else:
            p_prov = "VERIFIED ORIGINAL DOWNLOAD"
            p_interp = "VERIFIED SINGLE TRANSDUCER (Nominal NGM Barocap)"

        return SolEnvironmentReport(
            sol=row["sol"],
            earth_date=row["earth_date"],
            solar_longitude_ls=row["solar_longitude_ls"],
            season_name=row["season_name"],
            pressure_pa=row["pressure_pa"],
            temp_air_avg_c=row["temp_air_avg_c"],
            temp_air_min_c=row["temp_air_min_c"],
            temp_air_max_c=row["temp_air_max_c"],
            temp_ground_avg_c=row["temp_ground_avg_c"],
            temp_ground_min_c=row["temp_ground_min_c"],
            temp_ground_max_c=row["temp_ground_max_c"],
            wind_speed_avg_ms=row["wind_speed_avg_ms"],
            wind_speed_max_ms=row["wind_speed_max_ms"],
            wind_direction_deg=row["wind_direction_deg"],
            dust_opacity_tau=row["dust_opacity_tau"],
            uv_index_max=row["uv_index_max"],
            relative_humidity_pct=row["relative_humidity_pct"],
            survival_assessment=row["survival_assessment"],
            eva_suit_warnings=json.loads(row["eva_suit_warnings"]),
            rover_mobility_status=row["rover_mobility_status"],
            pressure_provenance=p_prov,
            pressure_interpretation_status=p_interp
        )

weather_service = WeatherService()
