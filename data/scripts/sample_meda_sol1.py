"""
Inspect authentic MEDA CSV records for Sol 1.
"""
import urllib.request

base = "https://pds-atmospheres.nmsu.edu/PDS/data/PDS4/Mars2020/mars2020_meda/data_derived_env/sol_0000_0089/sol_0001/"
req = urllib.request.Request(base + "WE__0001___________DER_PS__________________P02.CSV", headers={"User-Agent": "MarsExplorer/1.0"})

with urllib.request.urlopen(req, timeout=15) as resp:
    lines = [resp.readline().decode('utf-8', errors='ignore') for _ in range(10)]
    print("--- Pressure Sensor CSV Header / Sample ---")
    for l in lines:
        print(l.strip())

req_tirs = urllib.request.Request(base + "WE__0001___________DER_TIRS________________P04.CSV", headers={"User-Agent": "MarsExplorer/1.0"})
with urllib.request.urlopen(req_tirs, timeout=15) as resp:
    lines = [resp.readline().decode('utf-8', errors='ignore') for _ in range(10)]
    print("\n--- TIRS (Thermal IR) CSV Header / Sample ---")
    for l in lines:
        print(l.strip())
