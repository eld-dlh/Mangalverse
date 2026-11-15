"""
Terrain-Aware Martian Route-Planning Engine (MARS EXPLORER).
NASA Space Apps Challenge.

Uses A* pathfinding over authentic Martian digital elevation models,
slope gradients, traversal-cost grids, and surface hazard zones.

Supports three distinct mission route preferences:
1. SHORTEST: Prioritises minimum surface drive distance.
2. SAFEST: Heavily penalises steep slopes, high-angle climbs, and known surface hazards.
3. BALANCED: Optimal trade-off between drive distance and terrain traversal cost.

Includes multi-checkpoint sequencing, transparent terrain difficulty scoring,
safety warnings, elevation profiling, and safety disclaimers.
"""

from enum import Enum
import heapq
import math
from typing import List, Tuple, Dict, Any, Optional, Union
import numpy as np

from app.services.dem_service import jezero_dem_service, mars_haversine_distance
from app.services.terrain_analysis import TerrainAnalyzer, TerrainConfig, HazardZone

# Explicit Scientific Safety Disclaimer
ASTRONAUT_SAFETY_DISCLAIMER: str = (
    "DISCLAIMER: This computational surface route is a mission planning model based on "
    "USGS/NASA orbital CTX and HiRISE DEM elevation data. It is NOT guaranteed safe for "
    "human astronauts or robotic surface operations. Real Martian terrain features unmapped "
    "sub-meter boulders, active aeolian sand traps, loose dust mantles, and slope instabilities "
    "that require active in-situ rover computer vision verification."
)


class RoutePreference(str, Enum):
    """Route optimization objectives for surface traverse planning."""
    SHORTEST = "SHORTEST"
    SAFEST = "SAFEST"
    BALANCED = "BALANCED"


class RouteLegStatus(str, Enum):
    SUCCESS = "SUCCESS"
    UNREACHABLE = "UNREACHABLE"
    DEGRADED = "DEGRADED"


class TerrainPathfinder:
    """
    High-performance A* routing engine for planetary surface exploration.
    Supports in-memory cost grids, slope grids, and spatial hazard masks.
    """

    def __init__(self, dem_service=jezero_dem_service):
        self.dem = dem_service
        self.elevation = self.dem.elevation_grid
        self.slope = self.dem.slope_grid_deg
        self.height, self.width = self.dem.height, self.dem.width
        self.dx = float(self.dem.dx_meters)
        self.dy = float(self.dem.dy_meters)

        # Precompute South Séítah hazard boundary
        r1, c1 = self.dem.coord_to_pixel(77.436, 18.438)
        r2, c2 = self.dem.coord_to_pixel(77.447, 18.427)
        self.seitah_rmin, self.seitah_rmax = min(r1, r2), max(r1, r2)
        self.seitah_cmin, self.seitah_cmax = min(c1, c2), max(c1, c2)

        self.hazard_mask = np.zeros((self.height, self.width), dtype=bool)
        self.hazard_mask[self.seitah_rmin:self.seitah_rmax + 1, self.seitah_cmin:self.seitah_cmax + 1] = True

        # Precompute 8-connected neighbor offsets and step distances in meters
        diag_dist = math.hypot(self.dy, self.dx)
        self.directions = [
            (-1, 0, self.dy),     # North
            (1, 0, self.dy),      # South
            (0, -1, self.dx),     # West
            (0, 1, self.dx),      # East
            (-1, -1, diag_dist),  # North-West
            (-1, 1, diag_dist),   # North-East
            (1, -1, diag_dist),   # South-West
            (1, 1, diag_dist)     # South-East
        ]

    def _get_preference_weights(self, preference: RoutePreference) -> Dict[str, float]:
        """
        Cost function weight parameters based on selected route preference:
        - dist_weight: baseline travel distance penalty
        - slope_weight: steep terrain penalty multiplier
        - slope_exponent: exponential scaling on slope angle
        - hazard_weight: penalty factor for entering registered hazard zones
        - climb_weight: penalty factor for elevation gain (energy expenditure)
        """
        if preference == RoutePreference.SHORTEST:
            return {
                "dist_weight": 1.0,
                "slope_weight": 0.3,
                "slope_exponent": 1.5,
                "hazard_weight": 1.2,
                "climb_weight": 0.05,
                "max_allowed_slope": 22.0
            }
        elif preference == RoutePreference.SAFEST:
            return {
                "dist_weight": 0.4,
                "slope_weight": 4.5,
                "slope_exponent": 3.0,
                "hazard_weight": 8.0,
                "climb_weight": 0.8,
                "max_allowed_slope": 14.0
            }
        else:  # BALANCED
            return {
                "dist_weight": 1.0,
                "slope_weight": 2.0,
                "slope_exponent": 2.0,
                "hazard_weight": 3.0,
                "climb_weight": 0.3,
                "max_allowed_slope": 16.0
            }

    def astar_segment(
        self,
        start_rc: Tuple[int, int],
        goal_rc: Tuple[int, int],
        preference: RoutePreference = RoutePreference.BALANCED,
        max_safe_slope: float = 15.0,
        avoid_sand: bool = True,
        custom_cost_grid: Optional[np.ndarray] = None,
        custom_hazard_mask: Optional[np.ndarray] = None
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Compute optimal single-leg path between two grid cells using A* search.
        Uses 2D NumPy subgrids and localized bounding box for sub-second performance.
        """
        sr, sc = start_rc
        gr, gc = goal_rc

        if (sr, sc) == (gr, gc):
            return [(sr, sc)]

        # Check bounds
        if not (0 <= sr < self.height and 0 <= sc < self.width):
            return None
        if not (0 <= gr < self.height and 0 <= gc < self.width):
            return None

        # Check start and goal slope thresholds
        slope_grid = self.slope
        if slope_grid[sr, sc] > max_safe_slope or slope_grid[gr, gc] > max_safe_slope:
            # If endpoints are on steep terrain, allow relaxed threshold to avoid immediate dead ends
            effective_max_slope = max(max_safe_slope, float(max(slope_grid[sr, sc], slope_grid[gr, gc])) + 2.0)
        else:
            effective_max_slope = max_safe_slope

        weights = self._get_preference_weights(preference)
        hazards = custom_hazard_mask if custom_hazard_mask is not None else self.hazard_mask

        # Dynamic search window bounding box with adaptive padding
        padding = max(50, int(math.hypot(abs(sr - gr), abs(sc - gc)) * 0.4))
        rmin = max(0, min(sr, gr) - padding)
        rmax = min(self.height - 1, max(sr, gr) + padding)
        cmin = max(0, min(sc, gc) - padding)
        cmax = min(self.width - 1, max(sc, gc) + padding)

        sub_h = rmax - rmin + 1
        sub_w = cmax - cmin + 1

        g_score = np.full((sub_h, sub_w), np.inf, dtype=np.float32)
        closed = np.zeros((sub_h, sub_w), dtype=bool)
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

        sr_local, sc_local = sr - rmin, sc - cmin
        gr_local, gc_local = gr - rmin, gc - cmin

        g_score[sr_local, sc_local] = 0.0

        # Admissible Euclidean heuristic scaled by minimum distance weight
        def heuristic(r: int, c: int) -> float:
            return math.hypot((r - gr) * self.dy, (c - gc) * self.dx) * weights["dist_weight"]

        open_set = []
        heapq.heappush(open_set, (heuristic(sr, sc), sr, sc))

        max_iterations = 75000
        iterations = 0

        while open_set and iterations < max_iterations:
            iterations += 1
            f, cr, cc = heapq.heappop(open_set)
            lr, lc = cr - rmin, cc - cmin

            if closed[lr, lc]:
                continue
            closed[lr, lc] = True

            if (cr, cc) == (gr, gc):
                path = [(cr, cc)]
                curr = (cr, cc)
                while curr in came_from:
                    curr = came_from[curr]
                    path.append(curr)
                path.reverse()
                return path

            curr_g = g_score[lr, lc]
            curr_elev = self.elevation[cr, cc]

            for dr, dc, step_dist in self.directions:
                nr, nc = cr + dr, cc + dc

                if not (rmin <= nr <= rmax and cmin <= nc <= cmax):
                    continue

                nlr, nlc = nr - rmin, nc - cmin
                if closed[nlr, nlc]:
                    continue

                slope_val = slope_grid[nr, nc]
                if slope_val > effective_max_slope:
                    continue

                # 1. Slope penalty calculation
                slope_ratio = min(slope_val / max(effective_max_slope, 1.0), 1.0)
                slope_factor = 1.0 + weights["slope_weight"] * (slope_ratio ** weights["slope_exponent"])

                # 2. Hazard penalty calculation
                is_hazard = hazards[nr, nc] if avoid_sand else False
                hazard_factor = weights["hazard_weight"] if is_hazard else 1.0

                # 3. Elevation climb penalty
                delta_z = self.elevation[nr, nc] - curr_elev
                climb_penalty = max(0.0, float(delta_z)) * weights["climb_weight"]

                # Optional custom cost grid override
                if custom_cost_grid is not None:
                    cell_cost = custom_cost_grid[nr, nc]
                    if math.isinf(cell_cost) or cell_cost > 1e6:
                        continue
                    cost_multiplier = cell_cost
                else:
                    cost_multiplier = slope_factor * hazard_factor

                edge_cost = (step_dist * weights["dist_weight"] * cost_multiplier) + climb_penalty
                tentative_g = curr_g + edge_cost

                if tentative_g < g_score[nlr, nlc]:
                    g_score[nlr, nlc] = tentative_g
                    came_from[(nr, nc)] = (cr, cc)
                    f_score = tentative_g + heuristic(nr, nc)
                    heapq.heappush(open_set, (f_score, nr, nc))

        # Fallback with relaxed slope constraint if strict search was blocked
        if effective_max_slope < 24.0:
            return self.astar_segment(
                start_rc,
                goal_rc,
                preference=preference,
                max_safe_slope=24.0,
                avoid_sand=False,
                custom_cost_grid=custom_cost_grid,
                custom_hazard_mask=custom_hazard_mask
            )

        return None

    def plan_full_route(
        self,
        start_coord: List[float],
        destination_coord: Optional[List[float]] = None,
        checkpoint_coords: Optional[List[List[float]]] = None,
        preference: Union[str, RoutePreference] = RoutePreference.BALANCED,
        max_safe_slope: float = 15.0,
        avoid_sand: bool = True,
        speed_kmh: float = 0.12,
        custom_cost_grid: Optional[np.ndarray] = None,
        custom_hazard_mask: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Plan complete multi-leg route across all waypoints in sequential order.

        Parameters:
        - start_coord: [longitude, latitude] of mission start
        - destination_coord: [longitude, latitude] of final objective
        - checkpoint_coords: Ordered list of intermediate scientific checkpoints
        - preference: RoutePreference (SHORTEST, SAFEST, BALANCED)
        - max_safe_slope: Slope angle limit in degrees
        - avoid_sand: Whether to penalize aeolian sand hazards
        - speed_kmh: Nominal drive speed (default 0.12 km/h autonomous drive)
        """
        # Parse preference enum safely
        if isinstance(preference, str):
            pref_clean = preference.strip().upper()
            try:
                pref_enum = RoutePreference(pref_clean)
            except ValueError:
                pref_enum = RoutePreference.BALANCED
        else:
            pref_enum = preference or RoutePreference.BALANCED

        checkpoints = checkpoint_coords or []
        ordered_points = [start_coord] + checkpoints
        if destination_coord:
            ordered_points.append(destination_coord)

        if len(ordered_points) < 2:
            raise ValueError("Route planning requires at least a start coordinate and one destination or checkpoint.")

        full_pixel_path: List[Tuple[int, int]] = []
        leg_statuses: List[Dict[str, Any]] = []
        warnings: List[str] = []

        # Validate that all points fall within raster bounds
        grid_waypoints = []
        for idx, pt in enumerate(ordered_points):
            r, c = self.dem.coord_to_pixel(pt[0], pt[1])
            if not (0 <= r < self.height and 0 <= c < self.width):
                raise ValueError(
                    f"Waypoint #{idx} coordinates [{pt[0]}, {pt[1]}] are outside DEM coverage bounds."
                )
            grid_waypoints.append((r, c))

        # Sequentially solve each route leg
        total_accumulated_cost = 0.0

        for i in range(len(grid_waypoints) - 1):
            rc_from = grid_waypoints[i]
            rc_to = grid_waypoints[i + 1]
            p_from = ordered_points[i]
            p_to = ordered_points[i + 1]

            segment = self.astar_segment(
                start_rc=rc_from,
                goal_rc=rc_to,
                preference=pref_enum,
                max_safe_slope=max_safe_slope,
                avoid_sand=avoid_sand,
                custom_cost_grid=custom_cost_grid,
                custom_hazard_mask=custom_hazard_mask
            )

            if segment is None:
                # Path unreachable under slope constraints: use direct geodesic interpolation fallback
                warnings.append(
                    f"Warning: Leg #{i+1} from [{p_from[0]:.4f}, {p_from[1]:.4f}] to [{p_to[0]:.4f}, {p_to[1]:.4f}] "
                    f"encountered impassable terrain barriers. Direct interpolation applied."
                )
                leg_statuses.append({
                    "leg_index": i + 1,
                    "status": RouteLegStatus.UNREACHABLE.value,
                    "note": "Impassable terrain encountered; fallback interpolation used."
                })
                dist_m = mars_haversine_distance(p_from[0], p_from[1], p_to[0], p_to[1])
                steps = max(2, int(dist_m / max(self.dx, 15.0)))
                rows = np.linspace(rc_from[0], rc_to[0], steps, dtype=int)
                cols = np.linspace(rc_from[1], rc_to[1], steps, dtype=int)
                segment = list(zip(rows, cols))
            else:
                leg_statuses.append({
                    "leg_index": i + 1,
                    "status": RouteLegStatus.SUCCESS.value,
                    "waypoints_count": len(segment)
                })

            if full_pixel_path and segment:
                full_pixel_path.extend(segment[1:])
            else:
                full_pixel_path.extend(segment)

        # Convert pixel path to geographic coordinates [lon, lat]
        coords_lon_lat = []
        for r, c in full_pixel_path:
            lon, lat = self.dem.pixel_to_coord(r, c)
            coords_lon_lat.append([round(lon, 5), round(lat, 5)])

        # Sample continuous elevation profile along the path
        num_profile_samples = min(250, max(50, len(coords_lon_lat)))
        profile = self.dem.sample_elevation_profile(coords_lon_lat, num_samples=num_profile_samples)

        total_dist_m = profile[-1]["distance_meters"] if profile else 0.0
        total_dist_km = total_dist_m / 1000.0

        elevations = [p["elevation_m"] for p in profile]
        slopes = [p["slope_deg"] for p in profile]

        # Calculate elevation gain and loss
        elev_gain = 0.0
        elev_loss = 0.0
        for i in range(len(elevations) - 1):
            diff = elevations[i + 1] - elevations[i]
            if diff > 0:
                elev_gain += diff
            else:
                elev_loss += abs(diff)

        max_slope = max(slopes) if slopes else 0.0
        avg_slope = float(np.mean(slopes)) if slopes else 0.0

        # Calculate rover mobility speed and energy
        slope_speed_reduction = max(0.4, 1.0 - (avg_slope / 30.0))
        effective_speed = speed_kmh * slope_speed_reduction
        duration_hours = total_dist_km / effective_speed if effective_speed > 0 else 0.0

        # Potential energy: m * g * h (Perseverance mass = 1025 kg, Mars g = 3.72 m/s^2)
        potential_energy_kwh = (1025.0 * 3.72 * max(0.0, elev_gain)) / 3.6e6
        base_power_kwh = duration_hours * 0.400  # 400W nominal MMRTG power
        total_energy_kwh = round(base_power_kwh + potential_energy_kwh * 1.5, 2)

        # Calculate transparent terrain difficulty score (0 to 100 index)
        hazard_cells_count = sum(1 for r, c in full_pixel_path if self.hazard_mask[r, c])
        hazard_ratio = hazard_cells_count / max(len(full_pixel_path), 1)

        raw_difficulty = (
            (avg_slope / 15.0) * 35.0 +
            (max_slope / 25.0) * 30.0 +
            (hazard_ratio * 25.0) +
            (min(elev_gain / max(total_dist_m, 1.0) * 100.0, 10.0))
        )
        difficulty_score = round(float(np.clip(raw_difficulty, 0.0, 100.0)), 1)

        if difficulty_score <= 25.0:
            difficulty_rating = "LOW DIFFICULTY (Traversable Flat Crater Bedrock)"
        elif difficulty_score <= 50.0:
            difficulty_rating = "MODERATE DIFFICULTY (Undulating Delta Sediments)"
        elif difficulty_score <= 75.0:
            difficulty_rating = "HIGH DIFFICULTY (Steep Delta Scarps / Dune Proximity)"
        else:
            difficulty_rating = "EXTREME DIFFICULTY (Approaching Mechanical Mobility Limits)"

        # Generate contextual route safety warnings
        if max_slope >= 14.0:
            warnings.append(
                f"Terrain Pitch Warning: Route peaks at {max_slope:.1f}° slope, nearing rover 15.0° engineering limit."
            )
        if elev_gain > 50.0:
            warnings.append(
                f"Elevation Ascent: Steep climb of +{elev_gain:.1f} m requiring additional MMRTG battery reserve."
            )
        if hazard_cells_count > 0:
            warnings.append(
                f"Hazard Warning: Traverse crosses {hazard_cells_count} grid cells in the South Séítah aeolian dune zone. High wheel-slip risk."
            )

        # Route Waypoint metadata objects
        waypoints_meta = []
        cumulative_dist = 0.0
        for idx, pt in enumerate(ordered_points):
            if idx == 0:
                name = "Mission Origin"
                notes = "Initial departure location."
            elif idx == len(ordered_points) - 1 and destination_coord:
                name = "Objective Destination"
                notes = "Final scientific exploration target."
            else:
                name = f"Checkpoint #{idx}"
                notes = "Intermediate scientific sampling waypoint."

            elev = self.dem.get_elevation_at(pt[0], pt[1])
            if idx > 0:
                cumulative_dist += mars_haversine_distance(
                    ordered_points[idx - 1][0], ordered_points[idx - 1][1], pt[0], pt[1]
                )

            waypoints_meta.append({
                "id": f"wp_{idx}",
                "name": name,
                "longitude": round(pt[0], 5),
                "latitude": round(pt[1], 5),
                "elevation_m": round(elev, 2),
                "distance_from_start_m": round(cumulative_dist, 1),
                "notes": notes
            })

        # GeoJSON Feature with LineString geometry and comprehensive properties
        geojson_feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords_lon_lat
            },
            "properties": {
                "name": f"Terrain-Aware Martian Route ({pref_enum.value})",
                "route_preference": pref_enum.value,
                "total_distance_km": round(total_dist_km, 3),
                "elevation_gain_m": round(elev_gain, 1),
                "elevation_loss_m": round(elev_loss, 1),
                "max_slope_deg": round(max_slope, 1),
                "avg_slope_deg": round(avg_slope, 1),
                "estimated_duration_hours": round(duration_hours, 2),
                "estimated_energy_kwh": total_energy_kwh,
                "terrain_difficulty_score": difficulty_score,
                "terrain_difficulty_rating": difficulty_rating,
                "waypoints_count": len(waypoints_meta),
                "safety_warnings_count": len(warnings)
            }
        }

        # Determine overall execution status
        any_unreachable = any(leg["status"] == RouteLegStatus.UNREACHABLE.value for leg in leg_statuses)
        overall_status = "PARTIAL_SUCCESS" if any_unreachable else "SUCCESS"

        return {
            "status": overall_status,
            "route_preference": pref_enum.value,
            "total_distance_km": round(total_dist_km, 3),
            "total_elevation_gain_m": round(elev_gain, 1),
            "total_elevation_loss_m": round(elev_loss, 1),
            "max_slope_deg": round(max_slope, 1),
            "avg_slope_deg": round(avg_slope, 1),
            "estimated_drive_duration_hours": round(duration_hours, 2),
            "estimated_energy_consumption_kwh": total_energy_kwh,
            "terrain_difficulty_score": difficulty_score,
            "terrain_difficulty_rating": difficulty_rating,
            "path_geojson": geojson_feature,
            "elevation_profile": profile,
            "waypoints": waypoints_meta,
            "legs": leg_statuses,
            "safety_warnings": warnings,
            "safety_disclaimer": ASTRONAUT_SAFETY_DISCLAIMER,
            "algorithm_meta": {
                "algorithm": "Terrain-Aware A*",
                "preference": pref_enum.value,
                "heuristic": "Spherical Euclidean Distance on Mars (R=3389.5 km)",
                "elevation_datum": "USGS/NASA MOLA Areoid Datum",
                "max_safe_slope_threshold": max_safe_slope,
                "avoid_sand_hazards": avoid_sand,
                "samples_count": len(profile)
            }
        }


# Singleton instance
terrain_pathfinder = TerrainPathfinder()
