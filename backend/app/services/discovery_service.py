"""
Scientific Discoveries Service for querying NASA Mars 2020 Perseverance Mission Records.
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from app.config import DB_PATH, NASA_ATTRIBUTIONS
from app.models.discovery import ScientificDiscovery, GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry
from app.models.objective import ScientificObjective

class DiscoveryService:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_objectives(self) -> List[ScientificObjective]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scientific_objectives ORDER BY id ASC")
            rows = cursor.fetchall()

            objectives = []
            for row in rows:
                objectives.append(ScientificObjective(
                    id=row["id"],
                    code=row["code"],
                    title=row["title"],
                    category=row["category"],
                    description=row["description"],
                    scientific_rationale=row["scientific_rationale"],
                    primary_instruments=json.loads(row["primary_instruments"]),
                    target_formations=json.loads(row["target_formations"]),
                    recommended_checkpoint_ids=json.loads(row["recommended_checkpoint_ids"]),
                    biosignature_relevance=row["biosignature_relevance"]
                ))
            return objectives

    def get_objective_by_id(self, obj_id: str) -> Optional[ScientificObjective]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scientific_objectives WHERE id = ?", (obj_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return ScientificObjective(
                id=row["id"],
                code=row["code"],
                title=row["title"],
                category=row["category"],
                description=row["description"],
                scientific_rationale=row["scientific_rationale"],
                primary_instruments=json.loads(row["primary_instruments"]),
                target_formations=json.loads(row["target_formations"]),
                recommended_checkpoint_ids=json.loads(row["recommended_checkpoint_ids"]),
                biosignature_relevance=row["biosignature_relevance"]
            )

    def get_discoveries(
        self,
        objective_id: Optional[str] = None,
        samples_only: bool = False,
        search_query: Optional[str] = None
    ) -> List[ScientificDiscovery]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM scientific_discoveries WHERE 1=1"
            params = []

            if objective_id:
                query += " AND primary_objective_id = ?"
                params.append(objective_id)

            if samples_only:
                query += " AND sample_acquired = 1"

            if search_query:
                query += " AND (target_name LIKE ? OR lithology LIKE ? OR scientific_summary LIKE ? OR mineralogy_detected LIKE ?)"
                like_term = f"%{search_query}%"
                params.extend([like_term, like_term, like_term, like_term])

            query += " ORDER BY sol ASC"
            cursor.execute(query, params)
            rows = cursor.fetchall()

            discoveries = []
            for row in rows:
                discoveries.append(ScientificDiscovery(
                    id=row["id"],
                    target_name=row["target_name"],
                    sol=row["sol"],
                    earth_date=row["earth_date"],
                    latitude=row["latitude"],
                    longitude=row["longitude"],
                    elevation_m=row["elevation_m"],
                    geological_formation=row["geological_formation"],
                    lithology=row["lithology"],
                    instruments=json.loads(row["instruments"]),
                    scientific_summary=row["scientific_summary"],
                    mineralogy_detected=json.loads(row["mineralogy_detected"]),
                    biosignature_potential=row["biosignature_potential"],
                    sample_acquired=bool(row["sample_acquired"]),
                    sample_name=row["sample_name"],
                    sample_tube_serial=row["sample_tube_serial"],
                    cache_status=row["cache_status"],
                    primary_objective_id=row["primary_objective_id"],
                    nasa_pds_citation=row["nasa_pds_citation"],
                    companion_insight=row["companion_insight"]
                ))
            return discoveries

    def get_discovery_by_id(self, disc_id: str) -> Optional[ScientificDiscovery]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scientific_discoveries WHERE id = ?", (disc_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return ScientificDiscovery(
                id=row["id"],
                target_name=row["target_name"],
                sol=row["sol"],
                earth_date=row["earth_date"],
                latitude=row["latitude"],
                longitude=row["longitude"],
                elevation_m=row["elevation_m"],
                geological_formation=row["geological_formation"],
                lithology=row["lithology"],
                instruments=json.loads(row["instruments"]),
                scientific_summary=row["scientific_summary"],
                mineralogy_detected=json.loads(row["mineralogy_detected"]),
                biosignature_potential=row["biosignature_potential"],
                sample_acquired=bool(row["sample_acquired"]),
                sample_name=row["sample_name"],
                sample_tube_serial=row["sample_tube_serial"],
                cache_status=row["cache_status"],
                primary_objective_id=row["primary_objective_id"],
                nasa_pds_citation=row["nasa_pds_citation"],
                companion_insight=row["companion_insight"]
            )

    def get_discoveries_geojson(self, objective_id: Optional[str] = None) -> Dict[str, Any]:
        discoveries = self.get_discoveries(objective_id=objective_id)
        features = []
        for d in discoveries:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [d.longitude, d.latitude]
                },
                "properties": {
                    "id": d.id,
                    "target_name": d.target_name,
                    "sol": d.sol,
                    "earth_date": d.earth_date,
                    "elevation_m": d.elevation_m,
                    "geological_formation": d.geological_formation,
                    "lithology": d.lithology,
                    "instruments": d.instruments,
                    "scientific_summary": d.scientific_summary,
                    "mineralogy_detected": d.mineralogy_detected,
                    "biosignature_potential": d.biosignature_potential,
                    "sample_acquired": d.sample_acquired,
                    "sample_name": d.sample_name,
                    "cache_status": d.cache_status,
                    "primary_objective_id": d.primary_objective_id,
                    "nasa_pds_citation": d.nasa_pds_citation,
                    "companion_insight": d.companion_insight
                }
            })

        return {
            "type": "FeatureCollection",
            "metadata": {
                "source": "NASA Mars 2020 Perseverance Mission Science Archive",
                "target": "Jezero Crater, Mars",
                "count": len(features)
            },
            "features": features
        }

discovery_service = DiscoveryService()
