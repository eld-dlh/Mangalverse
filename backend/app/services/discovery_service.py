"""
Scientific Discoveries Service for querying NASA Mars 2020 Perseverance Mission Records.
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from app.config import DB_PATH, NASA_ATTRIBUTIONS
from app.models.discovery import ScientificDiscovery, GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry
from app.models.objective import ScientificObjective
from app.models.checkpoint import Checkpoint

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

    def _get_objective_checkpoint_mapping(self) -> Dict[str, List[str]]:
        """Maps each checkpoint ID to the list of objective IDs recommending it."""
        mapping: Dict[str, List[str]] = {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, recommended_checkpoint_ids FROM scientific_objectives")
            for row in cursor.fetchall():
                obj_id = row["id"]
                try:
                    cids = json.loads(row["recommended_checkpoint_ids"])
                    for cid in cids:
                        if cid not in mapping:
                            mapping[cid] = []
                        if obj_id not in mapping[cid]:
                            mapping[cid].append(obj_id)
                except Exception:
                    pass
        return mapping

    def get_checkpoints(
        self,
        objective_id: Optional[str] = None,
        samples_only: bool = False
    ) -> List[Checkpoint]:
        """Query scientific checkpoints for surface route planning."""
        obj_mapping = self._get_objective_checkpoint_mapping()
        discoveries = self.get_discoveries(samples_only=samples_only)
        checkpoints = []
        for d in discoveries:
            recom_objs = obj_mapping.get(d.id, [])
            if objective_id:
                if d.primary_objective_id != objective_id and objective_id not in recom_objs:
                    continue
            checkpoints.append(Checkpoint(
                id=d.id,
                name=d.target_name,
                sol=d.sol,
                earth_date=d.earth_date,
                latitude=d.latitude,
                longitude=d.longitude,
                elevation_m=d.elevation_m,
                geological_formation=d.geological_formation,
                lithology=d.lithology,
                instruments=d.instruments,
                scientific_summary=d.scientific_summary,
                sample_acquired=d.sample_acquired,
                sample_name=d.sample_name,
                sample_tube_serial=d.sample_tube_serial,
                cache_status=d.cache_status,
                primary_objective_id=d.primary_objective_id,
                recommended_for_objectives=recom_objs,
                companion_insight=d.companion_insight,
                nasa_pds_citation=d.nasa_pds_citation
            ))
        return checkpoints

    def get_checkpoint_by_id(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Query specific checkpoint by ID."""
        d = self.get_discovery_by_id(checkpoint_id)
        if not d:
            return None
        obj_mapping = self._get_objective_checkpoint_mapping()
        return Checkpoint(
            id=d.id,
            name=d.target_name,
            sol=d.sol,
            earth_date=d.earth_date,
            latitude=d.latitude,
            longitude=d.longitude,
            elevation_m=d.elevation_m,
            geological_formation=d.geological_formation,
            lithology=d.lithology,
            instruments=d.instruments,
            scientific_summary=d.scientific_summary,
            sample_acquired=d.sample_acquired,
            sample_name=d.sample_name,
            sample_tube_serial=d.sample_tube_serial,
            cache_status=d.cache_status,
            primary_objective_id=d.primary_objective_id,
            recommended_for_objectives=obj_mapping.get(d.id, []),
            companion_insight=d.companion_insight,
            nasa_pds_citation=d.nasa_pds_citation
        )

    def get_checkpoints_geojson(
        self,
        objective_id: Optional[str] = None,
        samples_only: bool = False
    ) -> Dict[str, Any]:
        """Export checkpoints as GeoJSON FeatureCollection."""
        cps = self.get_checkpoints(objective_id=objective_id, samples_only=samples_only)
        features = []
        for cp in cps:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [cp.longitude, cp.latitude]
                },
                "properties": {
                    "id": cp.id,
                    "name": cp.name,
                    "sol": cp.sol,
                    "earth_date": cp.earth_date,
                    "elevation_m": cp.elevation_m,
                    "geological_formation": cp.geological_formation,
                    "lithology": cp.lithology,
                    "instruments": cp.instruments,
                    "scientific_summary": cp.scientific_summary,
                    "sample_acquired": cp.sample_acquired,
                    "sample_name": cp.sample_name,
                    "primary_objective_id": cp.primary_objective_id,
                    "recommended_for_objectives": cp.recommended_for_objectives,
                    "companion_insight": cp.companion_insight,
                    "nasa_pds_citation": cp.nasa_pds_citation
                }
            })
        return {
            "type": "FeatureCollection",
            "metadata": {
                "source": "NASA Mars 2020 Perseverance Mission Science Archive",
                "target": "Jezero Crater Exploration Checkpoints",
                "count": len(features)
            },
            "features": features
        }

discovery_service = DiscoveryService()
