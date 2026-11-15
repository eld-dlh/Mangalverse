"""
Official NASA & USGS Data Acquisition Script for MARS EXPLORER.
Downloads authentic original planetary science data products directly from
authoritative USGS Astrogeology and NASA PDS archive endpoints.
"""
import os
import sys
import time
import hashlib
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ORIGINALS_DIR = BASE_DIR / "originals"

DOWNLOAD_TARGETS = [
    {
        "tier": "Dataset 1: CTX Jezero DEM Mosaic (20m)",
        "destination_dir": ORIGINALS_DIR / "ctx",
        "files": [
            {
                "filename": "M20_JezeroCrater_CTXDEM_20m.xml",
                "url": "https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.xml",
                "priority": "HIGH_METADATA"
            },
            {
                "filename": "M20_JezeroCrater_CTXDEM_20m.tif",
                "url": "https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXDEM_20m.tif",
                "priority": "CRITICAL_RASTER"
            }
        ]
    },
    {
        "tier": "Dataset 2: CTX Orthorectified Image Mosaic (5m)",
        "destination_dir": ORIGINALS_DIR / "ctx",
        "files": [
            {
                "filename": "M20_JezeroCrater_CTXortho_mosaic_5m.xml",
                "url": "https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXortho_mosaic_5m.xml",
                "priority": "HIGH_METADATA"
            },
            {
                "filename": "M20_JezeroCrater_CTXortho_mosaic_5m.tif",
                "url": "https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/CTX/ScienceInvestigationMaps_JPL/M20_JezeroCrater_CTXortho_mosaic_5m.tif",
                "priority": "CRITICAL_RASTER"
            }
        ]
    },
    {
        "tier": "Dataset 3: HiRISE DTM & Orthomosaic",
        "destination_dir": ORIGINALS_DIR / "hirise",
        "files": [
            {
                "filename": "DTM_MOLAtopography_DeltaGeoid_Jezero_C_Edited_affine_1m_Eqc_latTs0_lon0.xml",
                "url": "https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/HiRISE/DTM_MOLAtopography_DeltaGeoid_Jezero_C_Edited_affine_1m_Eqc_latTs0_lon0.xml",
                "priority": "HIGH_METADATA"
            },
            {
                "filename": "DTM_MOLAtopography_DeltaGeoid_Jezero_C_Edited_affine_1m_Eqc_latTs0_lon0.tif",
                "url": "https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/HiRISE/DTM_MOLAtopography_DeltaGeoid_Jezero_C_Edited_affine_1m_Eqc_latTs0_lon0.tif",
                "priority": "CRITICAL_RASTER"
            }
        ]
    },
    {
        "tier": "Dataset 4: MEDA Calibrated Observations",
        "destination_dir": ORIGINALS_DIR / "meda",
        "files": [
            {
                "filename": "meda_bundle_sis.pdf",
                "url": "https://pds-atmospheres.nmsu.edu/PDS/data/PDS4/Mars2020/mars2020_meda/document/meda_bundle_sis.pdf",
                "priority": "SPECIFICATION"
            }
        ]
    },
    {
        "tier": "Dataset 5: USGS SIM 3464 Geologic Map",
        "destination_dir": ORIGINALS_DIR / "geology",
        "files": [
            {
                "filename": "sim3464_metadata.txt",
                "url": "https://pubs.usgs.gov/sim/3464/sim3464_metadata.txt",
                "priority": "METADATA"
            },
            {
                "filename": "sim3464_database.zip",
                "url": "https://pubs.usgs.gov/sim/3464/sim3464_database.zip",
                "priority": "DATABASE_ZIP"
            }
        ]
    }
]

def attempt_download(url: str, dest_path: Path):
    print(f"Connecting to: {url}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) MarsExplorer/1.0'}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        total_size = response.getheader('Content-Length')
        print(f"  Content-Length: {total_size} bytes")
        with open(dest_path, 'wb') as out_f:
            chunk_size = 1024 * 1024 # 1 MB chunks
            downloaded = 0
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    pct = (downloaded / int(total_size)) * 100
                    print(f"  Downloaded: {downloaded / 1024 / 1024:.2f} MB ({pct:.1f}%)", end='\r')
                else:
                    print(f"  Downloaded: {downloaded / 1024 / 1024:.2f} MB", end='\r')
    print(f"\n  [SUCCESS] Saved to {dest_path}")

def run_download_pipeline():
    results = []
    for target in DOWNLOAD_TARGETS:
        print(f"\n=======================================================")
        print(f"PROCESSING: {target['tier']}")
        print(f"=======================================================")
        for file_info in target["files"]:
            filename = file_info["filename"]
            url = file_info["url"]
            dest = target["destination_dir"] / filename
            try:
                attempt_download(url, dest)
                sha256 = hashlib.sha256(dest.read_bytes()).hexdigest()
                size = dest.stat().st_size
                results.append({
                    "filename": filename,
                    "status": "DOWNLOADED",
                    "size_bytes": size,
                    "sha256": sha256,
                    "url": url,
                    "error": None
                })
            except Exception as e:
                print(f"  [FAILED] {filename}: {str(e)}")
                results.append({
                    "filename": filename,
                    "status": "FAILED",
                    "size_bytes": 0,
                    "sha256": None,
                    "url": url,
                    "error": str(e)
                })

    print("\n\n=== DOWNLOAD PIPELINE SUMMARY ===")
    for r in results:
        print(f"[{r['status']}] {r['filename']} - Error: {r['error']}")

if __name__ == "__main__":
    run_download_pipeline()
