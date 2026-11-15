# MARS EXPLORER 🪐
### Objective-Driven Martian Exploration & Survival Platform
**NASA Space Apps Challenge Project**  
*Focus Region: Jezero Crater, Mars (18.38°N - 18.52°N, 77.30°E - 77.50°E)*

---

## 🌟 Executive Summary

**MARS EXPLORER** is an objective-driven Martian surface exploration and survival platform built for the NASA Space Apps Challenge. Using verified NASA mission data from the Mars 2020 *Perseverance* rover and USGS orbital datasets, the platform helps mission planners, scientists, and explorers identify scientific targets, understand groundbreaking discoveries, and compute terrain-aware surface routes across Jezero Crater.

The application features **two coherent, fully integrated interfaces**:
1. **Mission Control**: A tactical GIS command center featuring interactive Mars cartography, official NASA data layers, scientific objective selection, checkpoint sequencing, Rasterio/NumPy terrain-aware A* pathfinding, and a real-time MEDA environmental telemetry dashboard.
2. **Explorer Mode**: An accessible, narrative-driven exploration experience guided by **ARES** (Automated Reconnaissance & Exploration Specialist)—an original virtual companion featuring voice narration, contextual scientific explanations, and step-by-step waypoint navigation.

---

## 🚀 Core Exploration Workflow

The platform implements an integrated end-to-end scientific exploration pipeline:

$$\text{Select Scientific Objective} \longrightarrow \text{Retrieve Verified Discoveries} \longrightarrow \text{Select Checkpoints} \longrightarrow \text{Calculate Terrain-Aware Route (A*)} \longrightarrow \text{Explore Locations} \longrightarrow \text{Review Scientific \& Environmental Telemetry}$$

1. **Select Objective**: Choose from 4 primary NASA exploration goals:
   - **ASTROBIO-LACUSTRINE**: Ancient Lacustrine Biosignatures (*Wildcat Ridge, Bright Angel, Margin Unit*)
   - **PETROLOGY-IGNEOUS**: Igneous Petrology & Geochronology (*Octavia E. Butler, Montdenier, Salette*)
   - **PALEOHYDRO-DELTA**: Fluvial Geomorphology & Delta Paleohydrology (*Kodiak Butte, Skinner Ridge, Belva Crater, Otis Peak*)
   - **MSR-CACHING**: Mars Sample Return Depot Logistics (*Three Forks Surface Depot, Sealed Core Tubes*)
2. **Retrieve Relevant Discoveries**: The system dynamically filters authentic Mars 2020 targets, lithology, and mineral detections.
3. **Select Checkpoints**: Pick key exploration sites or load recommended sequence.
4. **Calculate Terrain-Aware Route**: A* pathfinding evaluates topography, slope limits, and sand drift hazards using real Jezero DEM data.
5. **Explore Locations**: Deep-dive into mineralogy (Vivianite, Magnesite, Smectite, Gypsum), instruments (SHERLOC, PIXL, SuperCam), and sample caching status.
6. **Review Environmental Telemetry**: Real-time NASA MEDA atmospheric pressure, diurnal air/ground temperature swings, dust optical depth ($\tau$), wind speeds, and survival assessments.

---

## 🔬 NASA Datasets & Source Provenance

Strict fidelity: **Zero invented coordinates, measurements, or findings.** All data points are strictly attributed to official NASA mission archives:

| Dataset / Layer | NASA Mission / Instrument | Provider & Citation |
|---|---|---|
| **Jezero Crater DEM / DTM Topography** | Mars Reconnaissance Orbiter (MRO) HiRISE / CTX | USGS Astrogeology Science Center / NASA PDS (*Fergason et al., Mars 2020 TRN HiRISE DTM Mosaic, USGS Astropedia*) |
| **Rover Historical Traverse** | Mars 2020 Perseverance Rover Localization | NASA JPL MMGIS / NASA Planetary Data System (PDS) Geosciences Node |
| **Atmospheric & Environmental Data** | Mars Environmental Dynamics Analyzer (MEDA) | Centro de Astrobiología (CSIC-INTA) / NASA JPL (*Rodriguez-Manfredi et al., Space Sci Rev, 2021*) |
| **Scientific Targets & Rock Cores** | SHERLOC, PIXL, SuperCam, Mastcam-Z | NASA JPL Mars 2020 Science Team (*Farley et al., Science 2022; Scheller et al., Science 2022; Sharma et al., Nature 2023*) |
| **Global Mars Basemaps** | Viking MDIM 2.1 & Mars Global Surveyor MOLA | OpenPlanetaryMap / USGS Astrogeology Science Center |

---

## 🛠️ Technical Architecture

### Backend (Python FastAPI)
- **FastAPI**: RESTful API endpoints for objectives, discoveries, routing, elevation, and MEDA telemetry.
- **Rasterio & NumPy**: High-performance geospatial processing of Jezero Crater DEM GeoTIFF. Computes gradient magnitude, pitch slopes in degrees, and surface roughness.
- **A\* Pathfinding Algorithm**: Constraint-driven routing engine:
  - Enforces rover physical pitch limits ($\le 15^\circ$).
  - Avoids high wheel-slip hazards (e.g. Séítah ripple dune fields).
  - Calculates Mars spherical distances (Haversine on Mars radius $R = 3,389.5\text{ km}$).
  - Computes mechanical energy expenditure (kWh) and travel duration at autonomous drive speeds ($0.12\text{ km/h}$).
- **SQLite Database**: Verified scientific targets, mineralogy, sample tube serial numbers, and MEDA sol logs.

### Frontend (Interactive React & Leaflet)
- **React 18 & Leaflet**: High-performance interactive Martian GIS map with multiple layer switchers (OPM Basemap, USGS MOLA Topography, Shaded Relief).
- **Interactive SVG Elevation Profile**: Real-time elevation curve, slope gradient coloring, and synchronized map hover probe.
- **Virtual Companion (ARES)**: Holographic UI with speech synthesis using browser `speechSynthesis` API.
- **Tailwind CSS**: NASA / JPL dark mission control aesthetics with responsive panels.

---

## ⚡ Quick Start & Execution

### 1. Requirements
- Python 3.9+ (Python 3.10 - 3.14 supported)
- Standard web browser (Chrome, Edge, Firefox, Safari)

### 2. Launch the Platform
From the repository root directory, run:
```bash
python backend/run.py
```

### 3. Open in Browser
Navigate to:
```
http://127.0.0.1:8000
```

### 4. Run Automated Test Suite
To verify DEM loading, Mars spherical mathematics, A* pathfinding, and all API endpoints:
```bash
python backend/tests/test_backend.py
```

---

## 🛰️ API Documentation

Interactive Swagger documentation is available at:
`http://127.0.0.1:8000/docs`

Key API Endpoints:
- `GET /api/objectives`: List verified NASA scientific objectives.
- `GET /api/discoveries`: Query Perseverance targets with filters (`objective_id`, `samples_only`, `search`).
- `GET /api/discoveries/geojson`: Export targets as GeoJSON FeatureCollection.
- `POST /api/route/calculate`: Compute terrain-aware A* route over DEM raster grid.
- `GET /api/elevation/point`: Inspect elevation and slope at any Martian coordinate.
- `POST /api/elevation/profile`: Extract continuous elevation profile along coordinates.
- `GET /api/environment/meda`: Retrieve current and historical NASA MEDA sol reports.
- `GET /api/rover/traverse`: Retrieve official NASA Sols 0-1230 traverse coordinates.

---

## 👥 Credits & Space Apps Team
Built with pride for the **NASA Space Apps Challenge**.  
Data courtesy of NASA, Jet Propulsion Laboratory (JPL-Caltech), USGS Astrogeology Science Center, and OpenPlanetary.
