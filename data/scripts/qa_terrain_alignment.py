"""
Multi-point terrain elevation and coordinate alignment QA script.
Tests CTX DEM and HiRISE DTM across 7 landmark locations in Jezero Crater.
"""
import rasterio
from rasterio.transform import rowcol
import pyproj

ctx_path = "data/processed/elevation/jezero_ctx_dem_authentic.tif"
hirise_path = "data/processed/elevation/jezero_hirise_dtm_authentic.tif"

LANDMARKS = [
    ("Octavia E. Butler Landing Site", 77.4508, 18.4447),
    ("South Seitah (Sand ripple field)", 77.4420, 18.4330),
    ("Kodiak Butte (Remnant mesa)",     77.4350, 18.4182),
    ("Wildcat Ridge (Delta scarp)",     77.4042, 18.4485),
    ("Belva Crater (Impact structure)", 77.3820, 18.4682),
    ("Neretva Vallis Inflow Gorge",     77.3200, 18.4800),
    ("Western Jezero Crater Rim Peak",  77.2500, 18.4500),
]

geo_crs = pyproj.CRS.from_proj4("+proj=longlat +a=3396190 +b=3396190 +no_defs")

with rasterio.open(ctx_path) as ctx_src, rasterio.open(hirise_path) as hi_src:
    ctx_to_proj = pyproj.Transformer.from_crs(geo_crs, ctx_src.crs, always_xy=True)
    hi_to_proj  = pyproj.Transformer.from_crs(geo_crs, hi_src.crs, always_xy=True)

    ctx_elev_arr = ctx_src.read(1)
    hi_elev_arr  = hi_src.read(1)

    print("=== JEZERO CRATER TERRAIN & ELEVATION AUDIT ===")
    print(f"{'Landmark':35s} | {'Lon':7s} | {'Lat':7s} | {'CTX (20m)':10s} | {'HiRISE (1m)':11s} | {'Delta (m)':9s}")
    print("-" * 92)

    for name, lon, lat in LANDMARKS:
        # CTX lookup
        cx, cy = ctx_to_proj.transform(lon, lat)
        cr, cc = rowcol(ctx_src.transform, cx, cy)
        if 0 <= cr < ctx_src.height and 0 <= cc < ctx_src.width:
            c_val = ctx_elev_arr[cr, cc]
            ctx_str = f"{c_val:8.2f}m" if c_val != ctx_src.nodata else "NoData"
        else:
            c_val = None
            ctx_str = "Out Bounds"

        # HiRISE lookup
        hx, hy = hi_to_proj.transform(lon, lat)
        hr, hc = rowcol(hi_src.transform, hx, hy)
        if 0 <= hr < hi_src.height and 0 <= hc < hi_src.width:
            h_val = hi_elev_arr[hr, hc]
            hi_str = f"{h_val:8.2f}m" if h_val != hi_src.nodata else "NoData"
        else:
            h_val = None
            hi_str = "Out Bounds"

        diff_str = f"{abs(c_val - h_val):7.2f}m" if (c_val is not None and h_val is not None and c_val != ctx_src.nodata and h_val != hi_src.nodata) else "N/A"
        print(f"{name:35s} | {lon:7.4f} | {lat:7.4f} | {ctx_str:10s} | {hi_str:11s} | {diff_str:9s}")
