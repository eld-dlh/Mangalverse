"""
Backend Configuration and NASA Dataset Attributions for Mars Explorer.
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
