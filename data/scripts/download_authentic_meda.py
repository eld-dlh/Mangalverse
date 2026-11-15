"""
Download and process authentic Perseverance MEDA environmental observations
from NASA PDS Atmospheres Node:
  https://pds-atmospheres.nmsu.edu/PDS/data/PDS4/Mars2020/mars2020_meda/

Target Sols: 1, 89, 190, 260, 510, 800, 1050, 1215
"""
import urllib.request
import urllib.error
import re
import csv
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
ORIG_MEDA = DATA / "originals" / "meda"
PROC_ENV = DATA / "processed" / "environmental"

ORIG_MEDA.mkdir(parents=True, exist_ok=True)
PROC_ENV.mkdir(parents=True, exist_ok=True)

USER_AGENT = "MarsExplorer/1.0 (NASA Space Apps Challenge; Authentic Data Collector)"

# Directory mapping for sols in PDS4 data_calibrated_env
SOL_DIRS = [
    (1,    "sol_0000_0089", "sol_0001"),
    (89,   "sol_0000_0089", "sol_0089"),
    (190,  "sol_0180_0299", "sol_0190"),
    (262,  "sol_0180_0299", "sol_0262"),
    (510,  "sol_0420_0539", "sol_0510"),
    (800,  "sol_0780_0899", "sol_0800"),
    (1050, "sol_1020_1139", "sol_1050"),
    (1215, "sol_1140_1259", "sol_1215"),
]

BASE_CAL = "https://pds-atmospheres.nmsu.edu/PDS/data/PDS4/Mars2020/mars2020_meda/data_calibrated_env"
BASE_DER = "https://pds-atmospheres.nmsu.edu/PDS/data/PDS4/Mars2020/mars2020_meda/data_derived_env"

def download_file(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  Already exists: {dest.name} ({dest.stat().st_size:,} bytes)")
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            dest.write_bytes(data)
            print(f"  Downloaded: {dest.name} ({len(data):,} bytes)")
            return True
    except Exception as e:
        print(f"  Failed {url}: {e}")
        return False

def list_folder_files(folder_url: str) -> list[str]:
    try:
        req = urllib.request.Request(folder_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            entries = [e for e in re.findall(r'href="([^"]+)"', html)
                       if not e.startswith("?") and not e.startswith("/") and e != "../"]
            return entries
    except Exception as e:
        print(f"  Cannot list {folder_url}: {e}")
        return []

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def process_sol(sol_num: int, subrange: str, sol_folder: str) -> dict:
    print(f"\nProcessing Sol {sol_num} ({sol_folder}) ...")
    sol_url = f"{BASE_CAL}/{subrange}/{sol_folder}/"
    files = list_folder_files(sol_url)
    
    # Identify ATS and PS files
    ats_csv = next((f for f in files if "CAL_ATS" in f and f.upper().endswith(".CSV")), None)
    ats_xml = next((f for f in files if "CAL_ATS" in f and f.upper().endswith(".XML")), None)
    ps_csv  = next((f for f in files if "CAL_PS"  in f and f.upper().endswith(".CSV")), None)
    ps_xml  = next((f for f in files if "CAL_PS"  in f and f.upper().endswith(".XML")), None)

    sol_data = {
        "sol": sol_num,
        "source": "NASA PDS Atmospheres Node",
        "archive_url": sol_url,
        "files_downloaded": []
    }

    # Download files
    for fname in [ats_csv, ats_xml, ps_csv, ps_xml]:
        if fname:
            target = ORIG_MEDA / fname
            if download_file(f"{sol_url}{fname}", target):
                sol_data["files_downloaded"].append({
                    "filename": fname,
                    "sha256": sha256(target),
                    "size_bytes": target.stat().st_size
                })

    # Parse ATS CSV (Air Temperature in Kelvin -> convert to Celsius)
    if ats_csv and (ORIG_MEDA / ats_csv).exists():
        temps = []
        with open(ORIG_MEDA / ats_csv, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            # Find column indices for ATS temperatures
            temp_indices = []
            if header:
                for idx, col in enumerate(header):
                    if "ATS_LOCAL_TEMP" in col.upper():
                        temp_indices.append(idx)
            
            for row in reader:
                for idx in temp_indices:
                    if idx < len(row) and row[idx].strip():
                        try:
                            val = float(row[idx])
                            # Realistic Mars surface temp filter: 140K (-133C) to 310K (+37C)
                            if 140.0 <= val <= 310.0:
                                temps.append(val)
                        except ValueError:
                            pass
        
        if temps:
            sol_data["air_temperature_kelvin"] = {
                "min": round(min(temps), 2),
                "max": round(max(temps), 2),
                "mean": round(sum(temps) / len(temps), 2),
                "samples": len(temps)
            }
            sol_data["air_temperature_celsius"] = {
                "min": round(min(temps) - 273.15, 2),
                "max": round(max(temps) - 273.15, 2),
                "mean": round((sum(temps) / len(temps)) - 273.15, 2)
            }
            print(f"  ATS Temp (C): min={sol_data['air_temperature_celsius']['min']}°, "
                  f"max={sol_data['air_temperature_celsius']['max']}°, "
                  f"mean={sol_data['air_temperature_celsius']['mean']}°")

    # Parse PS CSV (Pressure in Pa)
    if ps_csv and (ORIG_MEDA / ps_csv).exists():
        pressures = []
        with open(ORIG_MEDA / ps_csv, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            p_idx = -1
            if header:
                for idx, col in enumerate(header):
                    if "PRESSURE" in col.upper() and "UNCERTAINTY" not in col.upper():
                        p_idx = idx
                        break
            if p_idx >= 0:
                for row in reader:
                    if p_idx < len(row) and row[p_idx].strip():
                        try:
                            val = float(row[p_idx])
                            if 500.0 <= val <= 1000.0:  # Reasonable Jezero surface pressure (Pa)
                                pressures.append(val)
                        except ValueError:
                            pass
        
        if pressures:
            sol_data["atmospheric_pressure_pa"] = {
                "min": round(min(pressures), 2),
                "max": round(max(pressures), 2),
                "mean": round(sum(pressures) / len(pressures), 2),
                "samples": len(pressures)
            }
            print(f"  PS Pressure (Pa): min={sol_data['atmospheric_pressure_pa']['min']}, "
                  f"max={sol_data['atmospheric_pressure_pa']['max']}, "
                  f"mean={sol_data['atmospheric_pressure_pa']['mean']}")

    return sol_data

def main():
    print("=" * 60)
    print("Fetching Authentic NASA MEDA Records from PDS")
    print("=" * 60)

    all_sols = []
    for sol_num, subrange, sol_folder in SOL_DIRS:
        res = process_sol(sol_num, subrange, sol_folder)
        all_sols.append(res)

    # Save to JSON
    out_json = PROC_ENV / "meda_authentic.json"
    dataset = {
        "metadata": {
            "source": "NASA Planetary Data System (PDS) Atmospheres Node",
            "instrument": "Mars Environmental Dynamics Analyzer (MEDA)",
            "mission": "Mars 2020 Perseverance Rover",
            "pds_bundle": "urn:nasa:pds:mars2020_meda",
            "retrieval_date": datetime.now(timezone.utc).isoformat(),
            "note": "Authentic calibrated observations from CAL_ATS (Air Temperature) and CAL_PS (Pressure)."
        },
        "sols": all_sols
    }
    out_json.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
    print(f"\nSaved authentic MEDA JSON to {out_json.relative_to(ROOT)}")

    # Save to CSV
    out_csv = PROC_ENV / "meda_authentic.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "sol", "temp_min_c", "temp_max_c", "temp_mean_c",
            "pressure_min_pa", "pressure_max_pa", "pressure_mean_pa",
            "temp_samples", "pressure_samples", "archive_url"
        ])
        for s in all_sols:
            t_c = s.get("air_temperature_celsius", {})
            p_pa = s.get("atmospheric_pressure_pa", {})
            t_k = s.get("air_temperature_kelvin", {})
            writer.writerow([
                s["sol"],
                t_c.get("min", ""),
                t_c.get("max", ""),
                t_c.get("mean", ""),
                p_pa.get("min", ""),
                p_pa.get("max", ""),
                p_pa.get("mean", ""),
                t_k.get("samples", 0),
                p_pa.get("samples", 0),
                s.get("archive_url", "")
            ])
    print(f"Saved authentic MEDA CSV to {out_csv.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
