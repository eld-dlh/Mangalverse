"""
Mars Explorer Backend API (NASA Space Apps Challenge).
Objective-driven Martian exploration platform utilizing NASA mission data for Jezero Crater.
"""
import mimetypes
from pathlib import Path

# Register JavaScript and JSX MIME types
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".jsx")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import (
    objectives,
    discoveries,
    checkpoints,
    terrain,
    routing,
    elevation,
    environment,
    rover
)
from app.config import NASA_ATTRIBUTIONS

app = FastAPI(
    title="Mars Explorer API - Jezero Crater Exploration Platform",
    description="Objective-driven Martian exploration backend utilizing verified NASA Mars 2020 mission datasets.",
    version="1.0.0"
)

# Enable CORS for frontend web application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(objectives.router)
app.include_router(discoveries.router)
app.include_router(checkpoints.router)
app.include_router(terrain.router)
app.include_router(routing.router)
app.include_router(elevation.router)
app.include_router(environment.router)
app.include_router(rover.router)

# Mount Static Files
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=FileResponse)
def serve_ui():
    """Serve the Mars Explorer interactive web application."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Mars Explorer Frontend UI loading..."}

@app.get("/api")
def api_root():
    return {
        "project": "MARS EXPLORER",
        "challenge": "NASA Space Apps Challenge",
        "focus_region": "Jezero Crater, Mars (18.38°N - 18.52°N, 77.30°E - 77.50°E)",
        "mission_focus": "Mars 2020 Perseverance Rover",
        "docs_url": "/docs",
        "endpoints": {
            "discoveries": "/api/discoveries",
            "discovery_by_id": "/api/discoveries/{id}",
            "objectives": "/api/objectives",
            "terrain": "/api/terrain",
            "environment": "/api/environment",
            "routes": "/api/routes",
            "checkpoints": "/api/checkpoints"
        },
        "verified_attributions": NASA_ATTRIBUTIONS
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "backend": "FastAPI",
        "geospatial_engine": "Rasterio + NumPy A*",
        "region": "Jezero Crater Delta"
    }
