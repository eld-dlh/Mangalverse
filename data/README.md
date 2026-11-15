# MARS EXPLORER – Authentic NASA & USGS Mission Data Package
### Jezero Crater Scientific Exploration Platform (NASA Space Apps Challenge)

**Target Body**: Mars (`IAU2000:49900` / Mars 2000 Sphere / Planetocentric East-Positive)  
**Primary Study Region**: Jezero Crater & Western Fan Delta ($17.5^\circ\text{N} - 19.3^\circ\text{N}$, $76.9^\circ\text{E} - 78.6^\circ\text{E}$)  
**Mission Baseline**: NASA Mars 2020 *Perseverance* Rover Mission (Sols 0 – 1230+)  
**Authenticity Status**: 100% genuine scientific data products downloaded directly from official NASA Planetary Data System (PDS) and USGS Astrogeology Science Center archives. All synthetic files have been retired and isolated in `data/synthetic_demo/` for offline frontend testing only.

---

## 📁 1. Directory Structure

```
data/
├── originals/                               # Unmodified authentic downloads from NASA PDS & USGS
│   ├── ctx/
│   │   ├── M20_JezeroCrater_CTXDEM_20m.tif  # USGS Mars 2020 CTX DEM mosaic (90.3 MB, 20m/px)
│   │   ├── M20_JezeroCrater_CTXDEM_20m.xml  # Official PDS4 observational label
│   │   ├── M20_JezeroCrater_CTXortho_mosaic_5m.tif # USGS CTX 5m orthomosaic (359.6 MB, 5m/px)
│   │   └── M20_JezeroCrater_CTXortho_mosaic_5m.xml # Official PDS4 observational label
│   ├── hirise/
│   │   ├── DTM_MOLAtopography_DeltaGeoid_Jezero_C_Edited_affine_1m_Eqc_latTs0_lon0.tif # USGS 1m DTM (125 MB)
│   │   └── DTM_MOLAtopography_DeltaGeoid_Jezero_C_Edited_affine_1m_Eqc_latTs0_lon0.xml # HiRISE metadata
│   ├── geology/
│   │   ├── sim3464_database.zip             # USGS Scientific Investigations Map 3464 Database (349 MB)
│   │   └── sim3464_extracted/               # Extracted File Geodatabase (Nili.gdb)
│   ├── meda/
│   │   ├── meda_bundle_sis.pdf              # Official Software Interface Specification
│   │   └── WE__*.CSV / .xml                 # Calibrated tables for Sols 1, 89, 190, 262, 510, 800, 1050, 1215
│   ├── forensic_inspection.json             # SHA-256 hashes, exact CRS WKT, and raster bounds
│   └── metadata_verified.json               # Extracted PDS4 metadata
├── processed/                               # Aligned, clipped, and formatted for application runtime
│   ├── elevation/
│   │   ├── jezero_ctx_dem_authentic.tif     # Authentic CTX DEM clipped to Jezero Crater extent
│   │   └── jezero_hirise_dtm_authentic.tif  # Authentic HiRISE 1m DTM clipped to Jezero Delta Fan
│   ├── imagery/
│   │   └── jezero_ctx_ortho_authentic.tif   # Authentic CTX 5m orthomosaic imagery
│   ├── environmental/
│   │   ├── meda_authentic.json              # Processed diurnal temperature & pressure records (8 sols)
│   │   └── meda_authentic.csv               # Tabular representation of authentic MEDA records
│   └── vector/
│       └── jezero_geological_units_authentic.geojson # 1,304 USGS SIM 3464 geological units in Mars degrees
├── synthetic_demo/                          # PREVIOUS APPROXIMATIONS (Isolated; testing use only)
│   ├── elevation/                           # Synthetic MOLA, CTX, and HiRISE grids
│   ├── imagery/                             # Synthetic hillshades
│   ├── environmental/                       # Previous synthetic CSV summaries
│   └── vector/                              # Synthetic vector layers
├── scripts/
│   ├── download_authentic_nasa.py           # Authenticated retrieval of USGS & NASA rasters
│   ├── download_authentic_meda.py           # Authenticated retrieval of PDS4 MEDA observations
│   ├── inspect_originals.py                 # Forensic verification & SHA-256 computation
│   └── process_authentic_data.py            # Automated alignment, clipping, FileGDB conversion, & validation
├── source_inventory.csv                     # Exhaustive forensic provenance matrix
└── validation_report.md                     # File-by-file QA checklist (All PASS)
```

---

## 🛰️ 2. Authentic Mission Data Provenance Matrix

| Dataset | Instrument / Mission | Official Archive URL | Product Identifier | Resolution | Native CRS | Authenticity Status |
|---|---|---|---|---|---|---|
| **CTX Regional DEM** | Mars Reconnaissance Orbiter (MRO) CTX | [USGS Astropedia](https://astrogeology.usgs.gov/search/map/mars_2020_science_investigation_ctx_dem_mosaic) | `urn:nasa:pds:mars2020_ctx_basemap_2021:data:m20_ctxdem_mosaic` | 20.0 m/px | Mars Equirectangular ($\phi_{ts}=18.4663^\circ$) | **VERIFIED ORIGINAL DOWNLOAD** |
| **CTX Surface Orthomosaic** | MRO Context Camera (CTX) | [USGS Astropedia](https://astrogeology.usgs.gov/search/map/mars-2020-jezero-crater-landing-site-products) | `urn:nasa:pds:mars2020_ctx_basemap_2021:data:m20_ctxortho_mosaic` | 5.0 m/px | Mars Equirectangular ($\phi_{ts}=18.4663^\circ$) | **VERIFIED ORIGINAL DOWNLOAD** |
| **HiRISE Delta DTM (Jezero_C Component)** | MRO HiRISE Camera | [USGS Astropedia TRN](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_hirise_dtm_mosaic) | `DTM_MOLAtopography_DeltaGeoid_Jezero_C_Edited_affine_1m` (Single stereopair DTM: ESP_045994_1985 & ESP_046060_1985aa; not full mosaic) | 1.0 m/px | ESRI:103885 (Equirectangular Mars 2000 Sphere) | **VERIFIED ORIGINAL DOWNLOAD** |
| **Geological Units** | USGS Astrogeology Science Center | [USGS SIM 3464](https://pubs.usgs.gov/sim/3464/) | `USGS SIM 3464 (Sun & Stack, 2020)` | Vector (1,304 polygons) | MTM clon $77.5^\circ\text{E}$ (Transformed to Mars $^\circ$) | **VERIFIED ORIGINAL DOWNLOAD** |
| **Environmental Telemetry** | Mars 2020 Perseverance MEDA | [NASA PDS Atmospheres Node](https://pds-atmospheres.nmsu.edu/PDS/data/PDS4/Mars2020/mars2020_meda/) | `urn:nasa:pds:mars2020_meda:data_calibrated_env` | In-situ time series | In-situ Rover Station ($18.44^\circ\text{N}, 77.45^\circ\text{E}$) | **VERIFIED ORIGINAL DOWNLOAD** |

---

## 🌐 3. Spatial Reference & Coordinate Systems

All geospatial coordinates in this package are defined using the international cartographic standard for Mars:
- **Reference Body**: Mars (`IAU 2000 Sphere`)
- **Equatorial Radius ($a$)**: $3,396,190.0\text{ m}$
- **Polar Radius ($c$)**: $3,396,190.0\text{ m}$
- **Coordinate Convention**: Planetocentric Latitude (North Positive, $0^\circ$ to $90^\circ\text{N}$), Positive East Longitude ($0^\circ$ to $360^\circ\text{E}$)
- **Vertical Datum**: MOLA Areoid Datum ($0.0\text{ m}$ level). Jezero Crater floor elevation is authentically $-2,567.05\text{ m}$ below the datum.
- **Projected CRS in Rasters**: Mars Equirectangular (`standard_parallel_1 = 18.4663`, `central_meridian = 0`, units: metres). The backend `dem_service` automatically transforms between planetocentric degrees `(lon, lat)` and projected coordinates `(x, y)` via `pyproj`.

---

## 🔬 4. Perseverance MEDA Environmental Observations

The authentic MEDA records were ingested from calibrated PDS4 data products (`CAL_ATS` for Air Temperature Sensor and `CAL_PS` for Pressure Sensor):

| Sol | Earth Date | Mission Phase / Campaign | Mean Air Temp ($^\circ\text{C}$) | Min Air Temp ($^\circ\text{C}$) | Max Air Temp ($^\circ\text{C}$) | Mean Pressure (Pa) | Sensor Samples | LMST Coverage |
|---|---|---|---|---|---|---|---|---|
| **1** | 2021-02-19 | Landing Sol (Octavia E. Butler) | -19.42 | -30.50 | -0.97 | 716.99 | 1,440 | Partial (16:04–16:34 LMST, checkout window) |
| **89** | 2021-05-20 | Crater Floor Campaign End | -53.60 | -81.57 | -4.80 | 768.04 | 86,400 | Complete (00:01–23:59 LMST, 24.0 h) |
| **190** | 2021-09-01 | South Séítah Entry | -49.27 | -80.60 | -1.82 | 716.29 | 43,200 | Sub-Complete (00:00–23:05 LMST, 23.1 h) |
| **262** | 2021-11-14 | Post-Conjunction Sampling | -38.42 | -66.70 | -11.71 | 649.18 | 12,000 | Partial (10:15–23:05 LMST, 12.8 h; morning absent) |
| **510** | 2022-07-27 | Delta Front Scarp Arrival | -55.69 | -85.78 | +3.86 | 793.75 | 28,800 | Sub-Complete (00:00–23:05 LMST, 23.1 h) |
| **800** | 2023-05-21 | Upper Fan & Belva Crater | -48.50 | -78.15 | -5.83 | 750.82 | 43,200 | Sub-Complete (00:00–23:05 LMST, 23.1 h) |
| **1050** | 2024-02-02 | Margin Unit Carbonate Survey | -46.43 | -74.30 | +1.91 | 674.23 | 41,000 | Sub-Complete (00:00–23:05 LMST, 23.1 h) |
| **1215** | 2024-07-20 | Neretva Vallis Rim Ascent | -50.18 | -81.50 | +6.16 | 754.09 | 17,280 | Sub-Complete (00:00–23:05 LMST, 23.1 h) |

> **Mission Note on Sols 260–261**: During Sols 260–261 (October 2021), Mars passed behind the Sun from Earth's perspective (Mars Solar Conjunction). NASA mission rules strictly mandate that no commands be sent and science operations be paused to avoid corrupted transmissions through ionized solar coronal plasma. Sol 262 represents the immediate resumption of calibrated MEDA telemetry.

---

## ⚠️ 5. Terrain Classification Model Disclaimer

All slope classifications (`SLOPE_LOW` for $\le 10^\circ$, `SLOPE_MODERATE` for $10^\circ - 15^\circ$, `SLOPE_HIGH` for $> 15^\circ$) are **project-generated mathematical models** computed directly from the authentic CTX DEM 20m gradient matrix. 
- These classifications are **NOT NASA-certified mission safety ratings**.
- Real Mars 2020 tactical rover traverse routing incorporates sub-meter hazard maps, rock abundance distributions, wheel slip models, and stereo navigation hazard cameras that cannot be derived from a 20 m/pixel orbital DEM alone.
- Classification outputs are provided solely for educational and research pathfinding simulations.

---

## 🛠️ 5. Integration Guide for Frontend and Route Planning

1. **Topography Queries**:
   - The primary operational DEM used by FastAPI is at `backend/app/data/jezero_crater_dem.tif` (90.3 MB, authentic USGS CTX DEM at 20m post spacing).
   - Calling `/api/v1/elevation/point?lon=77.4508&lat=18.4447` queries the authentic raster and returns `elevation_meters: -2567.05` and `slope_degrees: 2.71`.
2. **Terrain-Aware Pathfinding**:
   - The pathfinding engine (`backend/app/services/pathfinding.py`) executes 8-directional A* over the authentic 20m CTX gradient and slope matrix.
   - It enforces maximum slope thresholds (default $15.0^\circ$) and automatically steers routes away from severe sand trap hazards (such as the South Séítah ripple field).
3. **Geological Context**:
   - The vector layer `data/processed/vector/jezero_geological_units_authentic.geojson` contains all 1,304 stratigraphic polygons from USGS SIM 3464, complete with lithology, unit symbol, and stratigraphic age.
4. **Historical Demo Files**:
   - If frontend components require lightweight mock files for offline UI unit tests without loading 90MB rasters, use the isolated assets under `data/synthetic_demo/`. Do **not** use them for scientific path calculations or mission telemetry.
