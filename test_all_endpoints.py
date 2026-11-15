import requests

BASE = "http://127.0.0.1:8000"
results = []

def test(label, url, method="GET", body=None):
    try:
        if method == "POST":
            r = requests.post(url, json=body, timeout=30)
        else:
            r = requests.get(url, timeout=15)
        ok = "OK" if r.status_code == 200 else "FAIL"
        results.append((ok, r.status_code, label))
        print(f"[{ok}] {r.status_code}  {label}")
        return r
    except Exception as e:
        results.append(("ERR", 0, label))
        print(f"[ERR]       {label}: {e}")
        return None

test("GET /api/objectives",        BASE + "/api/objectives")
test("GET /api/discoveries",       BASE + "/api/discoveries")
test("GET /api/terrain",           BASE + "/api/terrain")
test("GET /api/terrain/geology",   BASE + "/api/terrain/geology")
test("GET /api/terrain/contours",  BASE + "/api/terrain/contours?interval_m=50")
test("GET /api/elevation/point",   BASE + "/api/elevation/point?lon=77.42&lat=18.44")
test("GET /api/environment/meda",  BASE + "/api/environment/meda")
test("GET /api/rover/traverse",    BASE + "/api/rover/traverse")
test("GET /api/rover/status",      BASE + "/api/rover/status")
test("POST /api/route/calculate",  BASE + "/api/route/calculate", "POST", {
    "start_point": [77.38, 18.44],
    "destination_point": [77.45, 18.44],
    "max_safe_slope_deg": 15.0,
    "avoid_sand_hazards": True,
    "speed_kmh": 0.12,
})
test("POST /api/route/compare",    BASE + "/api/route/compare", "POST", {
    "start_point": [77.38, 18.44],
    "destination_point": [77.45, 18.44],
    "max_safe_slope_deg": 15.0,
    "avoid_sand_hazards": True,
    "speed_kmh": 0.12,
})

passed = sum(1 for s,_,_ in results if s == "OK")
print(f"\n{'='*50}")
print(f"RESULT: {passed}/{len(results)} endpoints passing")
