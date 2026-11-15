# NASA Datasets — MARS EXPLORER
## Data Inventory, File Paths and PDS Identifiers

---

## 1. Topography & Elevation

### 1a. CTX Digital Elevation Model (Primary)
| Field | Value |
|-------|-------|
| **File** | `backend/app/data/jezero_crater_dem.tif` |
| **Alias** | `data/processed/elevation/jezero_ctx_dem_authentic.tif` |
| **Size** | 88.2 MB |
| **Resolution** | 20 m/pixel |
| **CRS** | Mars Equirectangular — `+proj=eqc +lat_ts=18.4663 +a=3396190 +b=3396190` |
| **Datum** | MOLA Areoid |
| **Bounds (projected)** | left=4328999, bottom=1042080, right=4418119, top=1143420 m |
| **Elevation range** | −3504.6 m to −475.8 m |
| **Shape** | 5067 × 4456 pixels |
| **PDS LID** | `urn:nasa:pds:mars2020_trn_dtm:data:jezero_ctx_dem` |
| **Provider** | USGS Astrogeology Science Center |
| **Citation** | Fergason et al., Mars 2020 TRN HiRISE DTM Mosaic, USGS Astropedia |
| **Used by** | A* pathfinder, elevation probe, slope analysis, contour generation |

### 1b. HiRISE DTM (High-resolution, 1 m/pixel)
| Field | Value |
|-------|-------|
| **File** | `data/processed/elevation/jezero_hirise_dtm_authentic.tif` |
| **Size** | 103.5 MB |
| **Resolution** | 1 m/pixel |
| **Coverage** | Jezero landing ellipse, partial |
| **Provider** | USGS Astrogeology (Mars 2020 TRN product) |
| **Used by** | Elevation probe (`prefer_hirise=true`), terrain assessment |

---

## 2. Imagery

### 2a. CTX Orthomosaic
| Field | Value |
|-------|-------|
| **File** | `data/processed/imagery/jezero_ctx_ortho_authentic.tif` |
| **Original** | `data/originals/ctx/M20_JezeroCrater_CTXortho_mosaic_5m.tif` |
| **Size** | 342.9 MB |
| **Resolution** | 5 m/pixel |
| **CRS** | Mars Equirectangular (same as CTX DEM) |
| **PDS LID** | `urn:nasa:pds:mars2020_ctx_basemap_2021:data:m20_ctxortho_mosaic` |
| **Instrument** | MRO Context Camera (CTX) |
| **Provider** | Malin Space Science Systems / NASA PDS |
| **Status** | ⚠️ NOT yet served as map tiles — GDAL gdalwarp + gdal2tiles required |

---

## 3. Geological Mapping

### 3a. USGS Nili Fossae / Jezero Geological Units
| Field | Value |
|-------|-------|
| **File** | `data/processed/vector/jezero_geological_units_authentic.geojson` |
| **Source** | Converted from `data/originals/geology/sim3464_extracted/sim3464_JezeroNili_FINAL/Geodatabase/Nili.gdb` |
| **Size** | 131.8 MB |
| **Features** | 1,304 polygon features |
| **Properties** | `unit`, `name`, `symbol_noSub`, `symbol`, `Color_ID`, `SHAPE_Area` |
| **CRS** | WGS84 geographic (lon/lat) — reprojected during conversion |
| **API** | `GET /api/terrain/geology` |
| **Citation** | Goudge et al. (2015), USGS Scientific Investigations Map 3464 |
| **DOI** | https://doi.org/10.3133/sim3464 |

---

## 4. Derived Data Products

### 4a. Elevation Contours (50 m interval)
| Field | Value |
|-------|-------|
| **File** | `data/processed/vector/jezero_contours_50m.geojson` |
| **Generated from** | `backend/app/data/jezero_crater_dem.tif` (authentic CTX DEM) |
| **Script** | `scripts/generate_contours.py` |
| **Size** | 34.2 MB |
| **Features** | 17,243 LineString segments |
| **Interval** | 50 m |
| **CRS** | Mars geographic (lon/lat, Mars sphere R=3396190 m) |
| **API** | `GET /api/terrain/contours?interval_m=50` |
| **To regenerate** | `python scripts/generate_contours.py` |

---

## 5. Environmental / Atmospheric

### 5a. MEDA Daily Summaries (NASA PDS)
| Field | Value |
|-------|-------|
| **Database** | `backend/app/data/mars_explorer.db` → `environmental_reports` |
| **Raw files** | `data/originals/meda/WE__{SOL}___________CAL_{TYPE}.CSV` |
| **Sols available** | 1, 89, 190, 262, 510, 800, 1050, 1215 (8 sols) |
| **Instrument** | Mars Environmental Dynamics Analyzer (MEDA) |
| **Parameters** | Air temp (min/max/avg), ground temp, pressure, wind speed/dir, dust opacity (tau), UV index, humidity |
| **Provenance** | Verified original NASA PDS download |
| **API** | `GET /api/environment/meda` |
| **PDS archive** | https://pds-atmospheres.nmsu.edu/PDS/data/PDS4/Mars2020/mars2020_meda/ |
| **Citation** | Rodriguez-Manfredi et al. (2021), The Mars Environmental Dynamics Analyzer (MEDA) Instrument Suite, Space Sci Rev 217:48 |

---

## 6. Rover Operations

### 6a. Perseverance Traverse Path (GeoJSON)
| Field | Value |
|-------|-------|
| **File** | `backend/app/data/nasa_perseverance_traverse.geojson` |
| **Source** | NASA JPL / MMGIS (Mars Multi-Mission Geographic Information System) |
| **Coverage** | Sols 0–1230 |
| **API** | `GET /api/rover/traverse` |
| **Citation** | NASA Mars 2020 Perseverance Rover Localization Archive, NASA PDS Geosciences Node |

### 6b. Scientific Discoveries Database
| Field | Value |
|-------|-------|
| **File** | `backend/app/data/mars_explorer.db` → `scientific_discoveries` |
| **Records** | 13 Perseverance science targets |
| **Instruments** | Mastcam-Z, SuperCam, PIXL, SHERLOC, RIMFAX |
| **Fields** | target_name, sol, lat/lon, geological_formation, lithology, minerals, biosignature_potential, nasa_pds_citation |
| **API** | `GET /api/discoveries` |

---

## Bounding Box — Jezero Crater Study Area
```
min_lon: 77.30°E    max_lon: 77.50°E
min_lat: 18.38°N    max_lat: 18.52°N
center:  18.4447°N, 77.4508°E  (Octavia E. Butler Landing)
```
