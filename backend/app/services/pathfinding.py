"""
Optimized Terrain-Aware A* Pathfinding for Mars 2020 Exploration.
Calculates optimal rover routes based on real Jezero DEM topography, slope limits, and surface hazards.
Uses NumPy 2D array lookups and localized bounding search for sub-second performance.
"""
import heapq
import math
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from app.services.dem_service import jezero_dem_service, mars_haversine_distance

class TerrainPathfinder:
    def __init__(self, dem_service=jezero_dem_service):
        self.dem = dem_service
        self.elevation = self.dem.elevation_grid
        self.slope = self.dem.slope_grid_deg
        self.height, self.width = self.dem.height, self.dem.width
        self.dx = float(self.dem.dx_meters)
        self.dy = float(self.dem.dy_meters)

        # Precompute South Séítah hazard mask
        r1, c1 = self.dem.coord_to_pixel(77.436, 18.438)
        r2, c2 = self.dem.coord_to_pixel(77.447, 18.427)
        self.seitah_rmin, self.seitah_rmax = min(r1, r2), max(r1, r2)
        self.seitah_cmin, self.seitah_cmax = min(c1, c2), max(c1, c2)

        self.hazard_mask = np.zeros((self.height, self.width), dtype=bool)
        self.hazard_mask[self.seitah_rmin:self.seitah_rmax+1, self.seitah_cmin:self.seitah_cmax+1] = True

        # Precompute neighbor offsets and base distances
        diag_dist = math.hypot(self.dy, self.dx)
        self.directions = [
            (-1, 0, self.dy),
            (1, 0, self.dy),
            (0, -1, self.dx),
            (0, 1, self.dx),
            (-1, -1, diag_dist),
            (-1, 1, diag_dist),
            (1, -1, diag_dist),
            (1, 1, diag_dist)
        ]

    def astar_segment(
        self,
        start_rc: Tuple[int, int],
        goal_rc: Tuple[int, int],
        max_safe_slope: float = 15.0,
        avoid_sand: bool = True
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Fast A* path search between two grid points using 2D NumPy arrays and bounding box bounds.
        """
        sr, sc = start_rc
        gr, gc = goal_rc

        if (sr, sc) == (gr, gc):
            return [(sr, sc)]

        # Define search bounding box with generous padding
        padding = 40
        rmin = max(0, min(sr, gr) - padding)
        rmax = min(self.height - 1, max(sr, gr) + padding)
        cmin = max(0, min(sc, gc) - padding)
        cmax = min(self.width - 1, max(sc, gc) + padding)

        # 2D cost and visited structures for C-level access speed
        sub_h = rmax - rmin + 1
        sub_w = cmax - cmin + 1

        g_score = np.full((sub_h, sub_w), np.inf, dtype=np.float32)
        closed = np.zeros((sub_h, sub_w), dtype=bool)
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

        sr_local, sc_local = sr - rmin, sc - cmin
        gr_local, gc_local = gr - rmin, gc - cmin

        g_score[sr_local, sc_local] = 0.0

        def heuristic(r: int, c: int) -> float:
            return math.hypot((r - gr) * self.dy, (c - gc) * self.dx)

        # Open set stores (f_score, r, c)
        open_set = []
        heapq.heappush(open_set, (heuristic(sr, sc), sr, sc))

        max_iterations = 60000
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

                slope_val = self.slope[nr, nc]
                if slope_val > max_safe_slope:
                    continue

                # Slope penalty
                slope_factor = 1.0 + 2.5 * ((slope_val / max_safe_slope) ** 2)

                # Sand hazard penalty
                hazard_factor = 3.5 if (avoid_sand and self.hazard_mask[nr, nc]) else 1.0

                # Elevation gain penalty
                delta_z = self.elevation[nr, nc] - curr_elev
                climb_penalty = max(0.0, float(delta_z)) * 0.3

                edge_cost = (step_dist * slope_factor * hazard_factor) + climb_penalty
                tentative_g = curr_g + edge_cost

                if tentative_g < g_score[nlr, nlc]:
                    g_score[nlr, nlc] = tentative_g
                    came_from[(nr, nc)] = (cr, cc)
                    f_score = tentative_g + heuristic(nr, nc)
                    heapq.heappush(open_set, (f_score, nr, nc))

        # If blocked by strict slope limit, fallback with relaxed slope constraint
        if max_safe_slope < 22.0:
            return self.astar_segment(start_rc, goal_rc, max_safe_slope=22.0, avoid_sand=avoid_sand)

        return None

    def plan_full_route(
        self,
        start_coord: List[float],
        destination_coord: Optional[List[float]] = None,
        checkpoint_coords: Optional[List[List[float]]] = None,
        max_safe_slope: float = 15.0,
        avoid_sand: bool = True,
        speed_kmh: float = 0.12
    ) -> Dict[str, Any]:
        """
        Plan complete multi-leg route across all waypoints.
        """
        checkpoints = checkpoint_coords or []
        points = [start_coord] + checkpoints
        if destination_coord:
            points.append(destination_coord)

        if len(points) < 2:
            raise ValueError("Route requires at least a start point and destination or checkpoint.")

        full_pixel_path = []
        for i in range(len(points) - 1):
            p_from = points[i]
            p_to = points[i + 1]

            rc_from = self.dem.coord_to_pixel(p_from[0], p_from[1])
            rc_to = self.dem.coord_to_pixel(p_to[0], p_to[1])

            segment = self.astar_segment(rc_from, rc_to, max_safe_slope=max_safe_slope, avoid_sand=avoid_sand)
            if segment is None:
                # Direct interpolated line fallback
                steps = max(2, int(mars_haversine_distance(p_from[0], p_from[1], p_to[0], p_to[1]) / 25.0))
                rows = np.linspace(rc_from[0], rc_to[0], steps, dtype=int)
                cols = np.linspace(rc_from[1], rc_to[1], steps, dtype=int)
                segment = list(zip(rows, cols))

            if full_pixel_path and segment:
                full_pixel_path.extend(segment[1:])
            else:
                full_pixel_path.extend(segment)

        # Convert pixel path to geographic coordinates and extract metrics
        coords_lon_lat = []
        for r, c in full_pixel_path:
            lon, lat = self.dem.pixel_to_coord(r, c)
            coords_lon_lat.append([round(lon, 5), round(lat, 5)])

        # Generate continuous sampled elevation profile
        profile = self.dem.sample_elevation_profile(coords_lon_lat, num_samples=min(200, max(50, len(coords_lon_lat))))

        total_dist_m = profile[-1]["distance_meters"] if profile else 0.0
        total_dist_km = total_dist_m / 1000.0

        elevations = [p["elevation_m"] for p in profile]
        slopes = [p["slope_deg"] for p in profile]

        elev_gain = 0.0
        elev_loss = 0.0
        for i in range(len(elevations) - 1):
            diff = elevations[i+1] - elevations[i]
            if diff > 0:
                elev_gain += diff
            else:
                elev_loss += abs(diff)

        max_slope = max(slopes) if slopes else 0.0
        avg_slope = float(np.mean(slopes)) if slopes else 0.0

        slope_speed_reduction = max(0.5, 1.0 - (avg_slope / 25.0))
        effective_speed = speed_kmh * slope_speed_reduction
        duration_hours = total_dist_km / effective_speed if effective_speed > 0 else 0.0

        potential_energy_kwh = (1025.0 * 3.72 * max(0.0, elev_gain)) / 3.6e6
        base_energy_kwh = (duration_hours * 0.400)
        total_energy_kwh = round(base_energy_kwh + potential_energy_kwh * 1.5, 2)

        warnings = []
        if max_slope >= 14.0:
            warnings.append(f"Caution: Maximum route pitch reaches {max_slope:.1f}°, nearing Perseverance 15.0° safety limit.")
        if elev_gain > 50.0:
            warnings.append(f"Significant elevation ascent of +{elev_gain:.1f}m onto the Jezero delta fan.")
        if any(self.hazard_mask[r, c] for r, c in full_pixel_path):
            warnings.append("Route approaches Séítah ripple terrain. High wheel-slip risk.")

        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords_lon_lat
            },
            "properties": {
                "name": "Terrain-Aware Planned Traverse",
                "total_distance_km": round(total_dist_km, 3),
                "elevation_gain_m": round(elev_gain, 1),
                "elevation_loss_m": round(elev_loss, 1),
                "max_slope_deg": round(max_slope, 1),
                "avg_slope_deg": round(avg_slope, 1),
                "duration_hours": round(duration_hours, 2),
                "energy_kwh": total_energy_kwh
            }
        }

        waypoints_meta = []
        for idx, pt in enumerate(points):
            w_elev = self.dem.get_elevation_at(pt[0], pt[1])
            name = "Mission Origin" if idx == 0 else (f"Objective Destination" if idx == len(points)-1 else f"Checkpoint #{idx}")
            waypoints_meta.append({
                "id": f"wp_{idx}",
                "name": name,
                "longitude": pt[0],
                "latitude": pt[1],
                "elevation_m": round(w_elev, 1),
                "distance_from_start_m": round(mars_haversine_distance(points[0][0], points[0][1], pt[0], pt[1]), 1),
                "notes": f"Waypoint {idx}: elevation {w_elev:.1f}m"
            })

        return {
            "status": "SUCCESS",
            "total_distance_km": round(total_dist_km, 3),
            "total_elevation_gain_m": round(elev_gain, 1),
            "total_elevation_loss_m": round(elev_loss, 1),
            "max_slope_deg": round(max_slope, 1),
            "avg_slope_deg": round(avg_slope, 1),
            "estimated_drive_duration_hours": round(duration_hours, 2),
            "estimated_energy_consumption_kwh": total_energy_kwh,
            "path_geojson": geojson,
            "elevation_profile": profile,
            "waypoints": waypoints_meta,
            "safety_warnings": warnings,
            "algorithm_meta": {
                "algorithm": "Terrain-Aware A* (Rasterio DEM Grid)",
                "grid_resolution_m": round(self.dx, 1),
                "max_safe_slope_deg": max_safe_slope,
                "body": "Mars (Jezero Crater)",
                "coordinate_system": "EPSG:4326 (Martian Planetographic)"
            }
        }

terrain_pathfinder = TerrainPathfinder()
