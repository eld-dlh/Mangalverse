"""Quick test for POST /api/route/compare"""
import requests

payload = {
    "start_point": [77.3812, 18.4421],
    "destination_point": [77.4521, 18.4356],
    "max_safe_slope_deg": 15.0,
    "avoid_sand_hazards": True,
    "speed_kmh": 0.12
}

r = requests.post("http://127.0.0.1:8000/api/route/compare", json=payload, timeout=120)
print("Status:", r.status_code)
if r.status_code == 200:
    d = r.json()
    for k in ["shortest", "safest", "balanced"]:
        v = d.get(k, {})
        dist = v.get("total_distance_km", "N/A")
        slope = v.get("max_slope_deg", "N/A")
        diff = v.get("terrain_difficulty_rating", "N/A")
        warn = len(v.get("safety_warnings", []))
        pts = len(v.get("path_geojson", {}).get("geometry", {}).get("coordinates", []))
        print(f"  {k:9s}: {dist} km | slope={slope}deg | diff={diff} | warnings={warn} | pts={pts}")
else:
    print(r.text[:800])
