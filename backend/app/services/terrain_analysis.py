"""
Terrain Analysis Module for MANGALVERSE (NASA Space Apps Challenge).
High-performance geospatial raster processing using Python, NumPy, and Rasterio.

Processes authentic Martian elevation rasters (USGS CTX / HiRISE DTMs):
1. Loads GeoTIFF elevation rasters and preserves spatial reference and coordinate metadata.
2. Identifies missing/NoData and physically invalid planetary elevation cells.
3. Calculates topographical slope in both degrees and percent rise.
4. Generates a terrain traversal difficulty cost grid assigning higher penalties to steeper terrain.
5. Supports configurable hazard penalties (e.g. active aeolian dunes, boulder fields).
6. Exports processed terrain information in formats directly consumable by A* pathfinding.
"""

from dataclasses import dataclass, field
import math
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional, Union
import numpy as np
import rasterio
from rasterio.transform import rowcol, xy, Affine
from rasterio.crs import CRS
import pyproj

# Physical Constants for Mars (IAU 2000 Mars reference sphere, matching USGS CTX DEM geodetic CRS)
MARS_RADIUS_METERS: float = 3396190.0  # IAU 2000 Mars spherical radius (m)


@dataclass
class TerrainConfig:
    """
    Configuration parameters for terrain slope calculation and traversal cost modeling.
    All thresholds and cost weights are explicitly documented and fully configurable.
    """
    # Slope Trafficability Thresholds (in degrees)
    # Based on published rover engineering envelopes (MSL/Mars 2020 mobility specs)
    nominal_slope_deg: float = 10.0      # <= 10 deg: Nominal rover surface mobility
    max_safe_slope_deg: float = 15.0     # 10 - 15 deg: Caution threshold (elevated wheel slip)
    impassable_slope_deg: float = 25.0   # >= 25 deg: Angle of repose / impassable barrier

    # Traversal Cost Multipliers
    base_cost_per_meter: float = 1.0     # Baseline traversability cost per meter on flat bedrock
    slope_weight: float = 2.5            # Quadratic penalty coefficient for slopes
    steep_slope_exponent: float = 3.0    # Exponential penalty exponent above nominal slope
    roughness_weight: float = 0.5        # Multiplier for terrain curvature / roughness
    sand_hazard_penalty: float = 3.5     # Wheel-slip hazard multiplier (e.g. South Séítah dunes)

    # Physical Elevation Bounds for Mars (meters relative to MOLA Areoid datum)
    min_physical_elevation_m: float = -10000.0  # Deepest Hellas basin depression ~ -7,152 m
    max_physical_elevation_m: float = 30000.0   # Highest Olympus Mons peak ~ +21,229 m


@dataclass
class HazardZone:
    """Represents a spatial surface hazard zone requiring traversal penalties."""
    name: str
    hazard_type: str
    min_lon: float
    max_lon: float
    min_lat: float
    max_lat: float
    penalty_multiplier: float = 3.5
    is_impassable: bool = False


class TerrainAnalyzer:
    """
    Geospatial terrain analysis engine for Martian digital elevation models.
    Preserves exact raster spatial reference, computes gradients, evaluates hazards,
    and produces traversal cost grids.
    """

    def __init__(
        self,
        raster_source: Union[str, Path, np.ndarray],
        transform: Optional[Affine] = None,
        crs: Optional[CRS] = None,
        nodata: Optional[float] = None,
        config: Optional[TerrainConfig] = None
    ):
        """
        Initialize analyzer from a GeoTIFF file path or an in-memory NumPy array with spatial transform.
        """
        self.config = config or TerrainConfig()
        self.hazards: List[HazardZone] = []

        if isinstance(raster_source, (str, Path)):
            self.raster_path = Path(raster_source)
            self._load_from_file(self.raster_path)
        elif isinstance(raster_source, np.ndarray):
            self.raster_path = None
            self._load_from_array(raster_source, transform, crs, nodata)
        else:
            raise TypeError("raster_source must be a file path (str/Path) or a 2D numpy array.")

        # Compute derived spatial grids
        self._compute_slope_and_roughness()
        self._compute_traversal_cost_grid()

    def _load_from_file(self, file_path: Path):
        """Load GeoTIFF while strictly preserving spatial reference and resolution."""
        if not file_path.exists():
            raise FileNotFoundError(f"Elevation raster not found at: {file_path}")

        with rasterio.open(file_path) as src:
            self.elevation_grid = src.read(1).astype(np.float32)
            self.transform: Affine = src.transform
            self.bounds = src.bounds
            self.height, self.width = self.elevation_grid.shape
            self.crs: CRS = src.crs
            self.nodata: Optional[float] = src.nodata

        self._setup_coordinate_system()

    def _load_from_array(
        self,
        array: np.ndarray,
        transform: Optional[Affine],
        crs: Optional[CRS],
        nodata: Optional[float]
    ):
        """Load in-memory raster array (useful for unit testing with known synthetic grids)."""
        if array.ndim != 2:
            raise ValueError(f"Array must be 2-dimensional (height, width), got shape {array.shape}")

        self.elevation_grid = array.astype(np.float32)
        self.height, self.width = self.elevation_grid.shape
        self.transform = transform or Affine(20.0, 0.0, 0.0, 0.0, -20.0, 0.0)
        self.crs = crs or CRS.from_proj4("+proj=longlat +a=3396190 +b=3396190 +no_defs")
        self.nodata = nodata

        # Compute raster bounds from transform and shape
        left = self.transform.c
        top = self.transform.f
        right = left + self.transform.a * self.width
        bottom = top + self.transform.e * self.height
        from rasterio.coords import BoundingBox
        self.bounds = BoundingBox(
            left=min(left, right),
            bottom=min(top, bottom),
            right=max(left, right),
            top=max(top, bottom)
        )

        self._setup_coordinate_system()

    def _setup_coordinate_system(self):
        """Setup physical pixel dimensions in meters and Mars coordinate transformers."""
        geo_crs = pyproj.CRS.from_proj4("+proj=longlat +a=3396190 +b=3396190 +no_defs")

        is_projected = False
        if self.crs:
            try:
                is_projected = bool(self.crs.is_projected)
            except Exception:
                is_projected = True

        if is_projected and self.crs is not None:
            self.is_projected = True
            self.to_proj = pyproj.Transformer.from_crs(geo_crs, self.crs, always_xy=True)
            self.to_geo = pyproj.Transformer.from_crs(self.crs, geo_crs, always_xy=True)
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

        # Enforce positive non-zero spatial resolution
        self.dx_meters = max(self.dx_meters, 0.1)
        self.dy_meters = max(self.dy_meters, 0.1)

    def identify_invalid_cells(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Identify missing, NoData, and physically invalid terrain cells.
        Returns a boolean valid_mask (True = valid, False = invalid) and statistical metrics.
        """
        valid = np.ones((self.height, self.width), dtype=bool)

        # 1. Check for NaNs and Infs
        valid &= np.isfinite(self.elevation_grid)

        # 2. Check for explicit raster NoData
        if self.nodata is not None:
            valid &= (np.abs(self.elevation_grid - self.nodata) > 1e-4)

        # 3. Check for physical elevation limits on Mars
        valid &= (self.elevation_grid >= self.config.min_physical_elevation_m)
        valid &= (self.elevation_grid <= self.config.max_physical_elevation_m)

        total_cells = self.height * self.width
        valid_count = int(np.count_nonzero(valid))
        invalid_count = total_cells - valid_count

        stats = {
            "total_cells": total_cells,
            "valid_cells": valid_count,
            "invalid_cells": invalid_count,
            "valid_ratio": round(valid_count / total_cells, 5),
            "invalid_ratio": round(invalid_count / total_cells, 5)
        }
        return valid, stats

    def _compute_slope_and_roughness(self):
        """
        Calculate topographical slope in degrees and percent rise, plus roughness.
        Slope units:
        - Degrees: arctan(gradient_magnitude) * (180 / pi)  [0 to 90 degrees]
        - Percent: gradient_magnitude * 100                 [0 to 100+% rise/run]
        """
        self.valid_mask, self.cell_stats = self.identify_invalid_cells()

        # Fill invalid cells with median of valid cells for smooth continuous gradient computation
        if np.any(self.valid_mask):
            median_val = float(np.median(self.elevation_grid[self.valid_mask]))
        else:
            median_val = -2500.0

        clean_elevation = np.where(self.valid_mask, self.elevation_grid, median_val)

        # Central difference spatial gradients: dz/dy and dz/dx
        grad_y, grad_x = np.gradient(clean_elevation, self.dy_meters, self.dx_meters)

        # Gradient magnitude: rise over run (dimensionless ratio)
        self.gradient_magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2).astype(np.float32)

        # Slope in degrees (0 to 90 deg)
        self.slope_grid_deg = np.degrees(np.arctan(self.gradient_magnitude)).astype(np.float32)

        # Slope in percent (rise / run * 100)
        self.slope_grid_percent = (self.gradient_magnitude * 100.0).astype(np.float32)

        # Mask invalid cells to 0 slope for safe numerical processing
        self.slope_grid_deg[~self.valid_mask] = 0.0
        self.slope_grid_percent[~self.valid_mask] = 0.0

        # Terrain roughness / curvature: sum of absolute slope gradients
        rough_y, rough_x = np.gradient(self.slope_grid_deg)
        self.roughness_grid = (np.abs(rough_y) + np.abs(rough_x)).astype(np.float32)
        self.roughness_grid[~self.valid_mask] = 0.0

    def add_hazard_zone(self, hazard: HazardZone):
        """Register a surface hazard zone with custom penalty multiplier."""
        self.hazards.append(hazard)
        self._compute_traversal_cost_grid()

    def _compute_traversal_cost_grid(self):
        """
        Generate a terrain traversal difficulty cost grid.
        Higher costs are assigned to steeper terrain and registered hazard zones.
        Invalid cells or slopes exceeding impassable thresholds receive infinity (np.inf).
        """
        # Base traversability cost
        cost = np.full((self.height, self.width), self.config.base_cost_per_meter, dtype=np.float32)

        # 1. Slope penalty calculation
        nom = self.config.nominal_slope_deg
        max_s = self.config.max_safe_slope_deg
        imp_s = self.config.impassable_slope_deg

        # Quadratic penalty for nominal slopes (0 to nominal_slope_deg)
        slope_penalty = 1.0 + self.config.slope_weight * ((self.slope_grid_deg / nom) ** 2)

        # Elevated cubic penalty for steep slopes between nominal and impassable
        steep_mask = (self.slope_grid_deg > nom) & (self.slope_grid_deg < imp_s)
        excess_ratio = (self.slope_grid_deg - nom) / max(max_s - nom, 1.0)
        slope_penalty[steep_mask] += 3.0 * (excess_ratio[steep_mask] ** self.config.steep_slope_exponent)

        # Apply slope penalty
        cost *= slope_penalty

        # 2. Roughness penalty
        roughness_factor = 1.0 + self.config.roughness_weight * np.clip(self.roughness_grid, 0.0, 5.0)
        cost *= roughness_factor

        # 3. Hazard zone penalties
        self.hazard_mask = np.zeros((self.height, self.width), dtype=bool)

        for hz in self.hazards:
            r_min, c_min = self.coord_to_pixel(hz.min_lon, hz.max_lat)
            r_max, c_max = self.coord_to_pixel(hz.max_lon, hz.min_lat)

            rmn, rmx = min(r_min, r_max), max(r_min, r_max)
            cmn, cmx = min(c_min, c_max), max(c_min, c_max)

            rmn = max(0, rmn)
            rmx = min(self.height - 1, rmx)
            cmn = max(0, cmn)
            cmx = min(self.width - 1, cmx)

            if rmx >= rmn and cmx >= cmn:
                self.hazard_mask[rmn:rmx+1, cmn:cmx+1] = True
                if hz.is_impassable:
                    cost[rmn:rmx+1, cmn:cmx+1] = np.inf
                else:
                    cost[rmn:rmx+1, cmn:cmx+1] *= hz.penalty_multiplier

        # 4. Impassable slopes: cliffs and vertical scarps
        cost[self.slope_grid_deg >= imp_s] = np.inf

        # 5. Invalid / NoData cells: marked strictly impassable
        cost[~self.valid_mask] = np.inf

        self.cost_grid = cost.astype(np.float32)

    def coord_to_pixel(self, lon: float, lat: float) -> Tuple[int, int]:
        """Convert Martian coordinate (lon, lat) to raster grid indices (row, col)."""
        if self.is_projected and self.to_proj is not None:
            x, y = self.to_proj.transform(lon, lat)
        else:
            x, y = lon, lat
        r, c = rowcol(self.transform, x, y)
        r = int(np.clip(r, 0, self.height - 1))
        c = int(np.clip(c, 0, self.width - 1))
        return r, c

    def pixel_to_coord(self, row: int, col: int) -> Tuple[float, float]:
        """Convert raster grid indices (row, col) to Martian coordinate (lon, lat)."""
        x, y = xy(self.transform, row, col)
        if self.is_projected and self.to_geo is not None:
            lon, lat = self.to_geo.transform(x, y)
        else:
            lon, lat = x, y
        return float(lon), float(lat)

    def get_traversal_cost_at(self, lon: float, lat: float) -> float:
        """Query computed traversal cost at specific coordinate."""
        r, c = self.coord_to_pixel(lon, lat)
        return float(self.cost_grid[r, c])

    def export_route_planner_data(self) -> Dict[str, Any]:
        """
        Export processed terrain grids and spatial metadata in a format directly
        consumable by the A* pathfinding route engine.
        """
        return {
            "cost_grid": self.cost_grid,
            "slope_degrees": self.slope_grid_deg,
            "slope_percent": self.slope_grid_percent,
            "elevation_grid": self.elevation_grid,
            "roughness_grid": self.roughness_grid,
            "valid_mask": self.valid_mask,
            "hazard_mask": self.hazard_mask,
            "shape": (self.height, self.width),
            "dx_meters": self.dx_meters,
            "dy_meters": self.dy_meters,
            "transform": self.transform,
            "crs": self.crs,
            "bounds": self.bounds,
            "nodata": self.nodata,
            "cell_stats": self.cell_stats,
            "config": {
                "nominal_slope_deg": self.config.nominal_slope_deg,
                "max_safe_slope_deg": self.config.max_safe_slope_deg,
                "impassable_slope_deg": self.config.impassable_slope_deg,
                "base_cost_per_meter": self.config.base_cost_per_meter,
                "slope_weight": self.config.slope_weight,
                "sand_hazard_penalty": self.config.sand_hazard_penalty
            }
        }

    def get_subgrid_for_routing(
        self,
        rmin: int,
        rmax: int,
        cmin: int,
        cmax: int
    ) -> Dict[str, Any]:
        """
        Extract a localized window/subgrid for fast bounded A* path search.
        """
        rmin = max(0, rmin)
        rmax = min(self.height - 1, rmax)
        cmin = max(0, cmin)
        cmax = min(self.width - 1, cmax)

        return {
            "sub_cost": self.cost_grid[rmin:rmax+1, cmin:cmax+1],
            "sub_elevation": self.elevation_grid[rmin:rmax+1, cmin:cmax+1],
            "sub_slope": self.slope_grid_deg[rmin:rmax+1, cmin:cmax+1],
            "sub_hazard": self.hazard_mask[rmin:rmax+1, cmin:cmax+1],
            "sub_valid": self.valid_mask[rmin:rmax+1, cmin:cmax+1],
            "bounds_rc": (rmin, rmax, cmin, cmax),
            "dx_meters": self.dx_meters,
            "dy_meters": self.dy_meters
        }

    def export_geotiff(
        self,
        output_path: Union[str, Path],
        layer: str = "cost"
    ) -> Path:
        """
        Export processed terrain layer as a standard GeoTIFF, preserving the exact
        spatial reference (CRS), affine transform, and resolution.
        layer: 'cost', 'slope_deg', 'slope_percent', or 'roughness'.
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        if layer == "cost":
            data = np.where(np.isinf(self.cost_grid), -9999.0, self.cost_grid).astype(np.float32)
            out_nodata = -9999.0
        elif layer == "slope_deg":
            data = self.slope_grid_deg.copy()
            out_nodata = -9999.0
        elif layer == "slope_percent":
            data = self.slope_grid_percent.copy()
            out_nodata = -9999.0
        elif layer == "roughness":
            data = self.roughness_grid.copy()
            out_nodata = -9999.0
        else:
            raise ValueError(f"Unknown layer: {layer}. Choose 'cost', 'slope_deg', 'slope_percent', or 'roughness'.")

        with rasterio.open(
            out_p,
            "w",
            driver="GTiff",
            height=self.height,
            width=self.width,
            count=1,
            dtype="float32",
            crs=self.crs,
            transform=self.transform,
            nodata=out_nodata
        ) as dst:
            dst.write(data, 1)

        return out_p
