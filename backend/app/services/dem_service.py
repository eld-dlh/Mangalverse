"""
DEM Service using Rasterio and NumPy for geospatial elevation and terrain analysis in Jezero Crater.
"""
import math
import numpy as np
import rasterio
from rasterio.transform import rowcol, xy
import pyproj
from typing import Tuple, List, Dict, Any, Optional
from app.config import DEM_PATH, JEZERO_BBOX, AUTHENTIC_HIRISE_DTM_PATH

# Physical constants for Mars (IAU 2000 Mars reference sphere, matching USGS CTX DEM geodetic CRS)
MARS_RADIUS_METERS = 3396190.0  # IAU 2000 Mars spherical radius (m)

def mars_haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate the great circle distance between two points on Mars in meters.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return MARS_RADIUS_METERS * c

class JezeroDEMService:
    def __init__(self, dem_path=DEM_PATH):
        self.dem_path = dem_path
        self._load_raster()
        self._hirise_loaded = False
        self._hirise_grid = None

    def _load_hirise(self):
        """Lazy loader for high-resolution 1m HiRISE DTM."""
        self._hirise_loaded = True
        if not AUTHENTIC_HIRISE_DTM_PATH.exists():
            return
        try:
            with rasterio.open(AUTHENTIC_HIRISE_DTM_PATH) as src:
                self._hirise_grid = src.read(1).astype(np.float32)
                self._hirise_transform = src.transform
                self._hirise_bounds = src.bounds
                self._hirise_height, self._hirise_width = self._hirise_grid.shape
                self._hirise_crs = src.crs
                self._hirise_nodata = src.nodata

            geo_crs = pyproj.CRS.from_proj4("+proj=longlat +a=3396190 +b=3396190 +no_defs")
            self._hirise_to_proj = pyproj.Transformer.from_crs(geo_crs, self._hirise_crs, always_xy=True)
            self._hirise_to_geo  = pyproj.Transformer.from_crs(self._hirise_crs, geo_crs, always_xy=True)
        except Exception as e:
            print(f"Warning: could not load HiRISE DTM: {e}")
            self._hirise_grid = None

    def _load_raster(self):
        with rasterio.open(self.dem_path) as src:
            self.elevation_grid = src.read(1).astype(np.float32)
            self.transform = src.transform
            self.bounds = src.bounds
            self.height, self.width = self.elevation_grid.shape
            self.crs = src.crs
            self.nodata = src.nodata

        # Setup coordinate transformers for Mars sphere
        geo_crs = pyproj.CRS.from_proj4("+proj=longlat +a=3396190 +b=3396190 +no_defs")
        if self.crs and (self.crs.is_projected if hasattr(self.crs, "is_projected") else True):
            self.is_projected = True
            self.to_proj = pyproj.Transformer.from_crs(geo_crs, self.crs, always_xy=True)
            self.to_geo  = pyproj.Transformer.from_crs(self.crs, geo_crs, always_xy=True)
            self.dx_meters = float(abs(self.transform.a))
            self.dy_meters = float(abs(self.transform.e))
        else:
            self.is_projected = False
            self.to_proj = None
            self.to_geo = None
            center_lat = (self.bounds.bottom + self.bounds.top) / 2.0
            deg_lat_meters = (math.pi / 180.0) * MARS_RADIUS_METERS
            deg_lon_meters = deg_lat_meters * math.cos(math.radians(center_lat))
            self.dx_meters = float(abs(self.transform.a) * deg_lon_meters)
            self.dy_meters = float(abs(self.transform.e) * deg_lat_meters)

        # Mask NoData values for gradient computation
        valid_mask = np.ones_like(self.elevation_grid, dtype=bool)
        if self.nodata is not None:
            valid_mask = (self.elevation_grid > (self.nodata + 1.0)) & np.isfinite(self.elevation_grid)
        else:
            valid_mask = (self.elevation_grid > -10000.0) & (self.elevation_grid < 30000.0)

        # Fill NaNs/NoData with median for continuous gradient calculation
        median_elev = float(np.nanmedian(np.where(valid_mask, self.elevation_grid, np.nan))) if np.any(valid_mask) else -2500.0
        clean_elev_filled = np.where(valid_mask, self.elevation_grid, median_elev)

        grad_y, grad_x = np.gradient(clean_elev_filled, self.dy_meters, self.dx_meters)
        gradient_magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)
        self.slope_grid_deg = np.degrees(np.arctan(gradient_magnitude)).astype(np.float32)
        self.slope_grid_deg[~valid_mask] = 0.0

        # Terrain roughness / curvature
        self.roughness_grid = (np.abs(np.gradient(self.slope_grid_deg)[0]) +
                               np.abs(np.gradient(self.slope_grid_deg)[1])).astype(np.float32)

    def coord_to_pixel(self, lon: float, lat: float) -> Tuple[int, int]:
        """
        Convert Martian coordinates (lon, lat) to raster grid indices (row, col).
        Clamps to valid raster dimensions.
        """
        if self.is_projected and self.to_proj is not None:
            x, y = self.to_proj.transform(lon, lat)
        else:
            x, y = lon, lat
        r, c = rowcol(self.transform, x, y)
        r = int(np.clip(r, 0, self.height - 1))
        c = int(np.clip(c, 0, self.width - 1))
        return r, c

    def pixel_to_coord(self, row: int, col: int) -> Tuple[float, float]:
        """
        Convert raster indices (row, col) to Martian coordinates (lon, lat).
        """
        x, y = xy(self.transform, row, col)
        if self.is_projected and self.to_geo is not None:
            lon, lat = self.to_geo.transform(x, y)
        else:
            lon, lat = x, y
        return float(lon), float(lat)

    def get_hirise_elevation_at(self, lon: float, lat: float) -> Optional[float]:
        """
        Query high-resolution (1 m/pixel) elevation from authentic USGS HiRISE DTM.
        Returns elevation in meters or None if coordinate is outside coverage.
        """
        if not self._hirise_loaded:
            self._load_hirise()
        if self._hirise_grid is None:
            return None
        try:
            x, y = self._hirise_to_proj.transform(lon, lat)
            r, c = rowcol(self._hirise_transform, x, y)
            if 0 <= r < self._hirise_height and 0 <= c < self._hirise_width:
                val = float(self._hirise_grid[r, c])
                if val != self._hirise_nodata and np.isfinite(val):
                    return round(val, 2)
        except Exception:
            pass
        return None

    def is_in_bounds(self, lon: float, lat: float) -> bool:
        """
        Check if Martian coordinate (lon, lat) falls within the authentic USGS Jezero Crater DEM extent
        and contains valid elevation data (non-NoData, realistic Martian elevation).
        """
        try:
            if self.is_projected and self.to_proj is not None:
                x, y = self.to_proj.transform(lon, lat)
            else:
                x, y = lon, lat

            if x < self.bounds.left or x > self.bounds.right or y < self.bounds.bottom or y > self.bounds.top:
                return False

            r, c = rowcol(self.transform, x, y)
            if not (0 <= r < self.height and 0 <= c < self.width):
                return False

            val = float(self.elevation_grid[r, c])
            if self.nodata is not None and abs(val - self.nodata) < 1.0:
                return False
            if val < -10000.0 or val > 30000.0 or not np.isfinite(val):
                return False

            return True
        except Exception:
            return False

    def get_elevation_at(self, lon: float, lat: float, prefer_hirise: bool = False) -> Optional[float]:
        """
        Get elevation in meters at specific coordinate.
        If prefer_hirise=True and coordinate is within HiRISE delta coverage, returns 1m HiRISE elevation.
        Otherwise falls back to regional 20m CTX DEM.
        Returns None if coordinate is outside valid DEM coverage.
        """
        if prefer_hirise:
            hi_val = self.get_hirise_elevation_at(lon, lat)
            if hi_val is not None:
                return hi_val
        if not self.is_in_bounds(lon, lat):
            return None
        r, c = self.coord_to_pixel(lon, lat)
        val = float(self.elevation_grid[r, c])
        return round(val, 2)

    def get_slope_at(self, lon: float, lat: float) -> Optional[float]:
        """
        Get slope in degrees at specific coordinate.
        Returns None if coordinate is outside valid DEM coverage.
        """
        if not self.is_in_bounds(lon, lat):
            return None
        r, c = self.coord_to_pixel(lon, lat)
        return round(float(self.slope_grid_deg[r, c]), 2)

    def get_analyzer(self):
        """Lazy access to full TerrainAnalyzer engine."""
        if not hasattr(self, "_analyzer") or self._analyzer is None:
            from app.services.terrain_analysis import TerrainAnalyzer, HazardZone
            self._analyzer = TerrainAnalyzer(self.dem_path)
            self._analyzer.add_hazard_zone(HazardZone(
                name="South Séítah Aeolian Dunes",
                hazard_type="Sand Ripple Slip",
                min_lon=77.436,
                max_lon=77.447,
                min_lat=18.427,
                max_lat=18.438,
                penalty_multiplier=3.5
            ))
        return self._analyzer

    def get_traversal_cost_at(self, lon: float, lat: float) -> float:
        """Query computed traversal cost at specific coordinate."""
        return self.get_analyzer().get_traversal_cost_at(lon, lat)

    def get_terrain_assessment(self, slope_deg: Optional[float]) -> dict:
        """
        Project-defined slope classification model derived from CTX DEM gradient analysis.
        These classifications are NOT NASA-certified mission safety ratings.
        Slope thresholds are based on published rover trafficability literature
        (Golombek et al. 2012, Mars Science Laboratory landing site selection)
        and are project-generated estimates only.
          <= 10 deg -> SLOPE_LOW    (generally traversable)
          <= 15 deg -> SLOPE_MODERATE (approach with caution)
          >  15 deg -> SLOPE_HIGH   (outside nominal traversal envelope)
        """
        if slope_deg is None:
            return {
                "classification": "OUT_OF_BOUNDS",
                "slope_degrees": None,
                "model_note": "Coordinates fall outside the authentic USGS Jezero Crater DEM boundary."
            }
        if slope_deg <= 10.0:
            label = "SLOPE_LOW"
        elif slope_deg <= 15.0:
            label = "SLOPE_MODERATE"
        else:
            label = "SLOPE_HIGH"
        return {
            "classification": label,
            "slope_degrees": round(float(slope_deg), 2),
            "model_note": (
                "Project-defined slope classification model based on CTX DEM gradient analysis. "
                "Thresholds: <=10 deg SLOPE_LOW, <=15 deg SLOPE_MODERATE, >15 deg SLOPE_HIGH. "
                "NOT a NASA mission safety certification."
            )
        }

    def sample_elevation_profile(self, coords: List[List[float]], num_samples: int = 100) -> List[Dict[str, Any]]:
        """
        Sample continuous elevation profile along a polyline.
        Each item contains: distance_meters, longitude, latitude, elevation_m, slope_deg, hazard_level.
        """
        if not coords or len(coords) < 2:
            return []

        # Calculate cumulative distance along polyline segments
        seg_dists = [0.0]
        total_dist = 0.0
        for i in range(len(coords) - 1):
            d = mars_haversine_distance(coords[i][0], coords[i][1], coords[i+1][0], coords[i+1][1])
            total_dist += d
            seg_dists.append(total_dist)

        if total_dist == 0:
            elev = self.get_elevation_at(coords[0][0], coords[0][1])
            slope = self.get_slope_at(coords[0][0], coords[0][1])
            assessment = self.get_terrain_assessment(slope)
            return [{
                "distance_meters": 0.0,
                "longitude": coords[0][0],
                "latitude": coords[0][1],
                "elevation_m": round(float(elev), 2) if elev is not None else -2500.0,
                "slope_deg": round(float(slope), 2) if slope is not None else 0.0,
                "hazard_level": assessment["classification"],
                "terrain_classification": assessment["classification"],
                "terrain_model_note": assessment["model_note"]
            }]

        # Sample evenly along total distance
        target_dists = np.linspace(0.0, total_dist, num_samples)
        profile = []

        seg_idx = 0
        for target_d in target_dists:
            while seg_idx < len(seg_dists) - 2 and seg_dists[seg_idx + 1] < target_d:
                seg_idx += 1

            p1 = coords[seg_idx]
            p2 = coords[seg_idx + 1]
            d_start = seg_dists[seg_idx]
            d_end = seg_dists[seg_idx + 1]

            if d_end - d_start > 0:
                fraction = (target_d - d_start) / (d_end - d_start)
            else:
                fraction = 0.0

            lon = p1[0] + fraction * (p2[0] - p1[0])
            lat = p1[1] + fraction * (p2[1] - p1[1])

            elev = self.get_elevation_at(lon, lat)
            slope = self.get_slope_at(lon, lat)
            assessment = self.get_terrain_assessment(slope)

            profile.append({
                "distance_meters": round(float(target_d), 1),
                "longitude": round(float(lon), 5),
                "latitude": round(float(lat), 5),
                "elevation_m": round(float(elev), 2) if elev is not None else -2500.0,
                "slope_deg": round(float(slope), 2) if slope is not None else 0.0,
                "hazard_level": assessment["classification"],
                "terrain_classification": assessment["classification"],
                "terrain_model_note": assessment["model_note"]
            })

        return profile

# Singleton instance
jezero_dem_service = JezeroDEMService()
