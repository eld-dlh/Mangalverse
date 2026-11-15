"""
Backend Configuration and NASA Dataset Attributions for Mangalverse.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = Path(__file__).resolve().parent / "data"
AUTHENTIC_DATA_DIR = PROJECT_ROOT / "data" / "processed"

DB_PATH = DATA_DIR / "mars_explorer.db"
DEM_PATH = DATA_DIR / "jezero_crater_dem.tif"  # Authentic 20m CTX DEM (90.3 MB)
TRAVERSE_PATH = DATA_DIR / "nasa_perseverance_traverse.geojson"

# Authentic NASA/USGS Scientific Products
AUTHENTIC_CTX_DEM_PATH = AUTHENTIC_DATA_DIR / "elevation" / "jezero_ctx_dem_authentic.tif"
AUTHENTIC_HIRISE_DTM_PATH = AUTHENTIC_DATA_DIR / "elevation" / "jezero_hirise_dtm_authentic.tif"
AUTHENTIC_CTX_ORTHO_PATH = AUTHENTIC_DATA_DIR / "imagery" / "jezero_ctx_ortho_authentic.tif"
AUTHENTIC_GEOLOGY_PATH = AUTHENTIC_DATA_DIR / "vector" / "jezero_geological_units_authentic.geojson"
AUTHENTIC_MEDA_JSON_PATH = AUTHENTIC_DATA_DIR / "environmental" / "meda_authentic.json"

# Jezero Crater Bounding Box (Western Delta & Landing Site)
# Martian Planetographic Coordinates (East Longitude Positive)
JEZERO_BBOX = {
    "min_lon": 77.30,
    "max_lon": 77.50,
    "min_lat": 18.38,
    "max_lat": 18.52,
    "center_lat": 18.4447,
    "center_lon": 77.4508
}

# Official NASA Mission Attributions
# ── Rover Mission Reference Data ─────────────────────────────────────────────
# Static mission reference data as of NASA PDS archive snapshot.
# Not real-time telemetry. Update from: https://mars.nasa.gov/mars2020/mission/status/
ROVER_STATUS_CONFIG = {
    "mission_name": "Mars 2020 Perseverance Rover",
    "landing_site": "Octavia E. Butler Landing (Jezero Crater)",
    "coordinates": {
        "latitude": 18.4447,
        "longitude": 77.4508,
        "elevation_m": -2570.0,
    },
    "landing_date_utc": "2021-02-18",
    "mission_sol": 1230,
    "odometer_km": 28.5,
    "sealed_sample_tubes_count": 24,
    "surface_depot_tubes_deposited": 10,
    "data_as_of": "2024-04-30",
    "note": (
        "Static mission reference data as of NASA PDS archive. "
        "For real-time telemetry see https://mars.nasa.gov/mars2020/"
    ),
    "power_source": "Multi-Mission Radioisotope Thermoelectric Generator (MMRTG)",
    "status": "OPERATIONAL",
}

NASA_ATTRIBUTIONS = {
    "topography": {
        "mission": "Mars Reconnaissance Orbiter (MRO) / Mars Global Surveyor (MGS)",
        "instruments": ["HiRISE Stereo DTM", "HRSC", "MOLA"],
        "provider": "USGS Astrogeology Science Center / NASA Planetary Data System (PDS)",
        "citation": "Fergason et al., Mars 2020 Terrain Relative Navigation (TRN) HiRISE DTM Mosaic, USGS Astropedia."
    },
    "rover_traverse": {
        "mission": "Mars 2020 Perseverance Rover",
        "provider": "NASA Jet Propulsion Laboratory (JPL) / Caltech / MMGIS",
        "citation": "NASA Mars 2020 Perseverance Rover Localization and Telemetry Archive, NASA PDS Geosciences Node."
    },
    "environmental_data": {
        "mission": "Mars 2020 Perseverance Rover",
        "instrument": "Mars Environmental Dynamics Analyzer (MEDA)",
        "provider": "Centro de Astrobiología (CSIC-INTA) / NASA JPL",
        "citation": "Rodriguez-Manfredi et al., The Mars Environmental Dynamics Analyzer (MEDA) Instrument Suite, Space Sci Rev (2021)."
    },
    "scientific_discoveries": {
        "mission": "Mars 2020 Perseverance Rover",
        "instruments": ["Mastcam-Z", "SuperCam", "PIXL", "SHERLOC", "RIMFAX"],
        "provider": "NASA JPL / Science Team Publications",
        "citation": "Farley et al., A lacustrine environment in Jezero crater, Mars, Science (2022); Scheller et al., Aqueous alteration in Séítah, Science (2022)."
    }
}
