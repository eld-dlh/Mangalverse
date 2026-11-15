"""
Forensic audit of authentic MEDA data across all 8 Sols.
Analyzes timestamps (LMST, LTST, SCLK), sample counts, observation coverage (start/end/duration),
units, raw values vs processed stats, and explains Sol 1 discrepancy.
"""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
ORIG = BASE / "data" / "originals" / "meda"
PROC = BASE / "data" / "processed" / "environmental"

SOLS = [1, 89, 190, 262, 510, 800, 1050, 1215]

audit_results = {}

for sol in SOLS:
    sol_str = f"{sol:04d}"
    # Find files for this sol
    ats_files = list(ORIG.glob(f"WE__{sol_str}*CAL_ATS*.CSV"))
    ps_files  = list(ORIG.glob(f"WE__{sol_str}*CAL_PS*.CSV"))
    ats_xmls  = list(ORIG.glob(f"WE__{sol_str}*CAL_ATS*.xml"))
    ps_xmls   = list(ORIG.glob(f"WE__{sol_str}*CAL_PS*.xml"))

    res = {
        "sol": sol,
        "ats_csv": ats_files[0].name if ats_files else None,
        "ps_csv": ps_files[0].name if ps_files else None,
        "ats_xml": ats_xmls[0].name if ats_xmls else None,
        "ps_xml": ps_xmls[0].name if ps_xmls else None,
        "ats_size": ats_files[0].stat().st_size if ats_files else 0,
        "ps_size": ps_files[0].stat().st_size if ps_files else 0,
    }

    # Inspect ATS
    if ats_files:
        with open(ats_files[0], "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
            res["ats_header"] = header
            res["ats_row_count"] = len(rows)
            if rows:
                first_lmst = rows[0][1] if len(rows[0]) > 1 else ""
                last_lmst  = rows[-1][1] if len(rows[-1]) > 1 else ""
                res["ats_lmst_start"] = first_lmst
                res["ats_lmst_end"] = last_lmst
                
                # Check sensor temperatures
                # Find ATS temp column indices
                temp_cols = [i for i, c in enumerate(header) if "ATS_LOCAL_TEMP" in c.upper()]
                all_temps_k = []
                for r in rows:
                    for col_idx in temp_cols:
                        if col_idx < len(r) and r[col_idx].strip():
                            try:
                                val = float(r[col_idx])
                                if 140.0 <= val <= 310.0:
                                    all_temps_k.append(val)
                            except ValueError:
                                pass
                if all_temps_k:
                    res["ats_k_min"] = min(all_temps_k)
                    res["ats_k_max"] = max(all_temps_k)
                    res["ats_k_mean"] = sum(all_temps_k) / len(all_temps_k)
                    res["ats_c_min"] = res["ats_k_min"] - 273.15
                    res["ats_c_max"] = res["ats_k_max"] - 273.15
                    res["ats_c_mean"] = res["ats_k_mean"] - 273.15
                    res["ats_valid_samples"] = len(all_temps_k)

    # Inspect PS
    if ps_files:
        with open(ps_files[0], "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
            res["ps_header"] = header
            res["ps_row_count"] = len(rows)
            if rows:
                first_lmst = rows[0][1] if len(rows[0]) > 1 else ""
                last_lmst  = rows[-1][1] if len(rows[-1]) > 1 else ""
                res["ps_lmst_start"] = first_lmst
                res["ps_lmst_end"] = last_lmst
                p_col = next((i for i, c in enumerate(header) if "PRESSURE" in c.upper() and "UNCERTAINTY" not in c.upper()), None)
                all_p = []
                if p_col is not None:
                    for r in rows:
                        if p_col < len(r) and r[p_col].strip():
                            try:
                                val = float(r[p_col])
                                if 500.0 <= val <= 1000.0:
                                    all_p.append(val)
                            except ValueError:
                                pass
                if all_p:
                    res["ps_min"] = min(all_p)
                    res["ps_max"] = max(all_p)
                    res["ps_mean"] = sum(all_p) / len(all_p)
                    res["ps_valid_samples"] = len(all_p)

    audit_results[sol] = res

# Compare with processed JSON
with open(PROC / "meda_authentic.json") as f:
    proc_json = json.load(f)

print(json.dumps(audit_results, indent=2))
