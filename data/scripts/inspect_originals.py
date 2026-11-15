"""
Step 1: Forensic inspection of all downloaded original rasters.
Outputs SHA-256, dimensions, CRS, bounds, resolution, nodata, dtype.
"""
import rasterio
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

files = {
    "ctx_dem":    BASE / "originals/ctx/M20_JezeroCrater_CTXDEM_20m.tif",
    "ctx_ortho":  BASE / "originals/ctx/M20_JezeroCrater_CTXortho_mosaic_5m.tif",
    "hirise_dtm": BASE / "originals/hirise/DTM_MOLAtopography_DeltaGeoid_Jezero_C_Edited_affine_1m_Eqc_latTs0_lon0.tif",
}

results = {}
for key, p in files.items():
    if not p.exists():
        print(f"MISSING: {p}")
        continue
    sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
    with rasterio.open(p) as src:
        info = {
            "path": str(p.relative_to(BASE.parent)),
            "sha256": sha256,
            "width": src.width,
            "height": src.height,
            "crs_string": str(src.crs),
            "crs_wkt": src.crs.wkt if src.crs else None,
            "bounds": {"left": src.bounds.left, "bottom": src.bounds.bottom,
                       "right": src.bounds.right, "top": src.bounds.top},
            "transform": [src.transform.a, src.transform.b, src.transform.c,
                          src.transform.d, src.transform.e, src.transform.f],
            "dtypes": list(src.dtypes),
            "nodata": src.nodata,
            "count": src.count,
            "res": list(src.res),
        }
    results[key] = info
    print(f"\n=== {key} ===")
    print(f"  File:     {p.name}")
    print(f"  SHA-256:  {sha256}")
    print(f"  Size:     {p.stat().st_size:,} bytes")
    print(f"  Dims:     {info['width']} x {info['height']} px,  {info['count']} band(s)")
    print(f"  CRS:      {info['crs_string']}")
    print(f"  Bounds:   left={info['bounds']['left']:.6f}  bottom={info['bounds']['bottom']:.6f}")
    print(f"            right={info['bounds']['right']:.6f}  top={info['bounds']['top']:.6f}")
    print(f"  Res:      {info['res']} (native units)")
    print(f"  Dtype:    {info['dtypes']}  NoData={info['nodata']}")
    print(f"  WKT[:160]:{info['crs_wkt'][:160] if info['crs_wkt'] else 'None'}")

out = BASE / "originals" / "forensic_inspection.json"
out.write_text(json.dumps(results, indent=2))
print(f"\nFull results saved to: {out}")
