"""
True HTTP Integration Test Suite for MANGALVERSE FastAPI Server.
Connects directly over HTTP (port 8000) to test:
- Real TCP connection and HTTP wire protocol
- FastAPI ASGI routing and path parameter extraction
- Query parameter deserialization
- JSON body payload deserialization
- Pydantic schema validation (verifying HTTP 422 on invalid/missing fields)
- Response serialization (JSON & GeoJSON)
- Error handling and HTTP status codes
"""
import sys
import httpx

BASE_URL = "http://127.0.0.1:8000"

def run_http_integration_suite():
    print("=" * 80)
    print(f"MANGALVERSE - TRUE HTTP INTEGRATION SUITE ({BASE_URL})")
    print("=" * 80)

    results = []

    with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
        # 1. Health & Root
        print("\n--- 1. Health & Core Infrastructure ---")
        r = client.get("/api/health")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        d = r.json()
        assert d["status"] == "HEALTHY"
        assert d["backend"] == "FastAPI"
        print(f"[PASSED] GET /api/health -> HTTP {r.status_code} ({d['status']})")
        results.append(("GET", "/api/health", 200, "PASS"))

        r = client.get("/api")
        assert r.status_code == 200
        d = r.json()
        assert "project" in d
        assert "endpoints" in d
        print(f"[PASSED] GET /api -> HTTP {r.status_code} (API index with {len(d['endpoints'])} endpoint groups)")
        results.append(("GET", "/api", 200, "PASS"))

        # 2. Discoveries
        print("\n--- 2. Scientific Discoveries ---")
        r = client.get("/api/discoveries")
        assert r.status_code == 200
        discs = r.json()
        assert len(discs) == 13, f"Expected 13 discoveries, got {len(discs)}"
        print(f"[PASSED] GET /api/discoveries -> HTTP {r.status_code} ({len(discs)} discoveries)")
        results.append(("GET", "/api/discoveries", 200, "PASS"))

        # GeoJSON
        r = client.get("/api/discoveries?format=geojson")
        assert r.status_code == 200
        geo = r.json()
        assert geo["type"] == "FeatureCollection"
        assert len(geo["features"]) == 13
        print(f"[PASSED] GET /api/discoveries?format=geojson -> HTTP {r.status_code} (FeatureCollection, 13 features)")
        results.append(("GET", "/api/discoveries?format=geojson", 200, "PASS"))

        # Filter by category
        r = client.get("/api/discoveries?category=ancient_water")
        assert r.status_code == 200
        water_discs = r.json()
        assert len(water_discs) >= 3
        print(f"[PASSED] GET /api/discoveries?category=ancient_water -> HTTP {r.status_code} ({len(water_discs)} items)")
        results.append(("GET", "/api/discoveries?category=ancient_water", 200, "PASS"))

        # Single item
        r = client.get("/api/discoveries/wildcat_ridge")
        assert r.status_code == 200
        d6 = r.json()
        assert d6["target_name"] == "Wildcat Ridge (Hazeltop)"
        print(f"[PASSED] GET /api/discoveries/wildcat_ridge -> HTTP {r.status_code} ({d6['target_name']})")
        results.append(("GET", "/api/discoveries/wildcat_ridge", 200, "PASS"))

        # 404
        r = client.get("/api/discoveries/nonexistent_target_xyz")
        assert r.status_code == 404
        print(f"[PASSED] GET /api/discoveries/nonexistent_target_xyz -> HTTP {r.status_code} (Correct 404 handling)")
        results.append(("GET", "/api/discoveries/nonexistent_target_xyz", 404, "PASS"))

        # 3. Objectives
        print("\n--- 3. Scientific Objectives ---")
        r = client.get("/api/objectives")
        assert r.status_code == 200
        objs = r.json()
        assert len(objs) == 4
        print(f"[PASSED] GET /api/objectives -> HTTP {r.status_code} ({len(objs)} objectives)")
        results.append(("GET", "/api/objectives", 200, "PASS"))

        r = client.get("/api/objectives/ancient_water")
        assert r.status_code == 200
        ow = r.json()
        assert ow["id"] == "ancient_water"
        print(f"[PASSED] GET /api/objectives/ancient_water -> HTTP {r.status_code} ({ow['name']})")
        results.append(("GET", "/api/objectives/ancient_water", 200, "PASS"))

        r = client.get("/api/objectives/ancient_water/discoveries")
        assert r.status_code == 200
        ow_discs = r.json()
        assert len(ow_discs) >= 3
        print(f"[PASSED] GET /api/objectives/ancient_water/discoveries -> HTTP {r.status_code} ({len(ow_discs)} discoveries)")
        results.append(("GET", "/api/objectives/ancient_water/discoveries", 200, "PASS"))

        # POST itinerary plan
        r = client.post("/api/objectives/plan", json={
            "objective_id": "ancient_water",
            "start_point": [77.4508, 18.4447],
            "selected_checkpoint_ids": ["enchanted_lake", "wildcat_ridge"],
            "preference": "BALANCED"
        })
        assert r.status_code == 200
        itin = r.json()
        assert itin["status"] == "SUCCESS"
        assert itin["route_summary"]["total_distance_km"] > 0
        print(f"[PASSED] POST /api/objectives/plan -> HTTP {r.status_code} (Distance: {itin['route_summary']['total_distance_km']} km, Status: {itin['status']})")
        results.append(("POST", "/api/objectives/plan", 200, "PASS"))

        # 4. MEDA Telemetry
        print("\n--- 4. MEDA Environmental Telemetry ---")
        r = client.get("/api/environment")
        assert r.status_code == 200
        env = r.json()
        assert "latest_sol" in env
        print(f"[PASSED] GET /api/environment -> HTTP {r.status_code} (Sol {env['latest_sol']['sol']}, Pressure: {env['latest_sol']['pressure_pa']} Pa)")
        results.append(("GET", "/api/environment", 200, "PASS"))

        r = client.get("/api/environment/meda/1215")
        assert r.status_code == 200
        m1215 = r.json()
        assert m1215["sol"] == 1215
        assert abs(m1215["temp_air_avg_c"] - (-50.18)) < 0.1
        print(f"[PASSED] GET /api/environment/meda/1215 -> HTTP {r.status_code} (Sol 1215 Air Temp: {m1215['temp_air_avg_c']}°C)")
        results.append(("GET", "/api/environment/meda/1215", 200, "PASS"))

        # 5. Terrain & Elevation
        print("\n--- 5. Terrain & Elevation Endpoints ---")
        r = client.get("/api/terrain?lon=77.4508&lat=18.4447")
        assert r.status_code == 200
        tp = r.json()
        assert abs(tp["elevation_meters"] - (-2569.0)) < 15.0
        print(f"[PASSED] GET /api/terrain?lon=77.4508&lat=18.4447 -> HTTP {r.status_code} (Elevation: {tp['elevation_meters']:.2f} m, Slope: {tp['slope_degrees']:.2f}°)")
        results.append(("GET", "/api/terrain (point)", 200, "PASS"))

        r = client.get("/api/terrain")
        assert r.status_code == 200
        t_summary = r.json()
        assert "ctx_dem" in t_summary
        assert t_summary["ctx_dem"]["elevation_median_m"] < 0
        print(f"[PASSED] GET /api/terrain -> HTTP {r.status_code} (Coverage median elev: {t_summary['ctx_dem']['elevation_median_m']:.1f} m)")
        results.append(("GET", "/api/terrain (summary)", 200, "PASS"))

        r = client.post("/api/elevation/profile?samples=25", json=[
            [77.4508, 18.4447],
            [77.4360, 18.4380]
        ])
        assert r.status_code == 200
        prof = r.json()
        assert prof["samples_count"] == 25
        print(f"[PASSED] POST /api/elevation/profile -> HTTP {r.status_code} ({prof['samples_count']} profile points)")
        results.append(("POST", "/api/elevation/profile", 200, "PASS"))

        # 6. Routes & Validation
        print("\n--- 6. Route Planning & Pydantic Validation ---")
        r = client.post("/api/routes", json={
            "start_coord": [77.4508, 18.4447],
            "destination_coord": [77.4360, 18.4380],
            "preference": "BALANCED",
            "max_safe_slope": 15.0,
            "avoid_sand": True
        })
        assert r.status_code == 200
        route = r.json()
        assert route["status"] == "SUCCESS"
        assert route["total_distance_km"] > 0
        print(f"[PASSED] POST /api/routes -> HTTP {r.status_code} (Distance: {route['total_distance_km']} km, Status: {route['status']})")
        results.append(("POST", "/api/routes", 200, "PASS"))

        # Default empty body generates nominal baseline route
        r_def = client.post("/api/routes", json={})
        assert r_def.status_code == 200
        print(f"[PASSED] POST /api/routes (default body) -> HTTP 200 (Nominal landing traverse)")

        # Pydantic 422 on schema violation (invalid data type)
        r = client.post("/api/routes", json={"start_point": "not_a_valid_coordinate_array"})
        assert r.status_code == 422, f"Expected 422, got {r.status_code}"
        d_err = r.json()
        assert "detail" in d_err
        print(f"[PASSED] POST /api/routes (type mismatch) -> HTTP {r.status_code} (Pydantic 422 Unprocessable Entity verified)")
        results.append(("POST", "/api/routes (invalid type)", 422, "PASS"))

        # 7. Checkpoints
        print("\n--- 7. Checkpoints ---")
        r = client.get("/api/checkpoints")
        assert r.status_code == 200
        cps = r.json()
        assert len(cps) >= 4
        print(f"[PASSED] GET /api/checkpoints -> HTTP {r.status_code} ({len(cps)} checkpoints)")
        results.append(("GET", "/api/checkpoints", 200, "PASS"))

    print("\n" + "=" * 80)
    print(f"ALL {len(results)} HTTP INTEGRATION TESTS PASSED (100% SUCCESS)!")
    print("=" * 80)
    return results

if __name__ == "__main__":
    run_http_integration_suite()
