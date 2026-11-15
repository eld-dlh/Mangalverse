// MANGALVERSE - Frontend Application (NASA Space Apps Challenge)
// Objective-Driven Jezero Crater Exploration and Survival Platform

const { useState, useEffect, useRef, useMemo, useCallback } = React;

// -------------------------------------------------------------
// SVG ICONS (Self-contained, fast, zero external icon dependencies)
// -------------------------------------------------------------
const IconRocket = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
    <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
    <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
    <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
  </svg>
);

const IconUser = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const IconCompass = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
  </svg>
);

const IconLayers = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 2 7 12 12 22 7 12 2" />
    <polyline points="2 17 12 22 22 17" />
    <polyline points="2 12 12 17 22 12" />
  </svg>
);

const IconThermometer = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" />
  </svg>
);

const IconWind = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2" />
    <path d="M9.6 4.6A2 2 0 1 1 11 8H2" />
    <path d="M12.6 19.4A2 2 0 1 0 14 16H2" />
  </svg>
);

const IconGauge = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m12 14 4-4" />
    <path d="M3.34 19a10 10 0 1 1 17.32 0" />
  </svg>
);

const IconShield = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);

const IconBot = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="18" height="12" x="3" y="6" rx="2" />
    <circle cx="9" cy="12" r="1" />
    <circle cx="15" cy="12" r="1" />
    <path d="M12 2v4" />
    <path d="M2 12h1" />
    <path d="M21 12h1" />
  </svg>
);

const IconVolume = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
    <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
  </svg>
);

const IconVolumeMute = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
    <line x1="23" y1="9" x2="17" y2="15" />
    <line x1="17" y1="9" x2="23" y2="15" />
  </svg>
);

const IconCheck = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const IconAlert = () => (
  <svg className="w-4 h-4 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

const IconInfo = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="16" x2="12" y2="12" />
    <line x1="12" y1="8" x2="12.01" y2="8" />
  </svg>
);

// -------------------------------------------------------------
// MAIN APP COMPONENT
// -------------------------------------------------------------
function MarsExplorerApp() {
  // Navigation & View Mode
  const [activeMode, setActiveMode] = useState("MISSION_CONTROL"); // "MISSION_CONTROL" | "EXPLORER_MODE"
  const [activeTab, setActiveTab] = useState("WORKFLOW"); // "WORKFLOW" | "ENVIRONMENT" | "LAYERS"

  // Data State
  const [objectives, setObjectives] = useState([]);
  const [discoveries, setDiscoveries] = useState([]);
  const [traverseGeoJSON, setTraverseGeoJSON] = useState(null);
  const [medaTelemetry, setMedaTelemetry] = useState(null);
  const [selectedSol, setSelectedSol] = useState(null);

  // Workflow State
  const [selectedObjectiveId, setSelectedObjectiveId] = useState("OBJ-1");
  const [selectedCheckpointIds, setSelectedCheckpointIds] = useState([]);
  const [maxSafeSlope, setMaxSafeSlope] = useState(15.0);
  const [avoidSand, setAvoidSand] = useState(true);

  // Route State
  const [routePreference, setRoutePreference] = useState("BALANCED");
  const [routeResult, setRouteResult] = useState(null);
  const [isCalculatingRoute, setIsCalculatingRoute] = useState(false);
  const [routeHoverPoint, setRouteHoverPoint] = useState(null);

  // Explorer Mode State
  const [currentWaypointIndex, setCurrentWaypointIndex] = useState(0);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // UI Modals & Popups
  const [selectedDiscoveryModal, setSelectedDiscoveryModal] = useState(null);
  const [showAttributionModal, setShowAttributionModal] = useState(false);
  const [probePoint, setProbePoint] = useState(null);

  // Map Layer Toggles
  const [layers, setLayers] = useState({
    basemap: "OPM", // "OPM" | "MOLA" | "SOIL"
    showTraverse: true,
    showDiscoveries: true,
    showRoute: true,
    showHazards: true
  });

  // Reference for Leaflet map instance
  const mapRef = useRef(null);
  const mapContainerRef = useRef(null);
  const layersRef = useRef({});

  // -----------------------------------------------------------
  // 1. Initial Data Fetch
  // -----------------------------------------------------------
  useEffect(() => {
    // Load Objectives
    fetch('/api/objectives')
      .then(res => res.json())
      .then(data => {
        setObjectives(data);
        if (data.length > 0) {
          const defaultObj = data[0];
          setSelectedObjectiveId(defaultObj.id);
          setSelectedCheckpointIds(defaultObj.recommended_checkpoint_ids || []);
        }
      })
      .catch(err => console.error("Error loading objectives:", err));

    // Load Discoveries
    fetch('/api/discoveries')
      .then(res => res.json())
      .then(data => setDiscoveries(data))
      .catch(err => console.error("Error loading discoveries:", err));

    // Load Rover Traverse
    fetch('/api/rover/traverse')
      .then(res => res.json())
      .then(data => setTraverseGeoJSON(data))
      .catch(err => console.error("Error loading traverse:", err));

    // Load MEDA Environmental Telemetry
    fetch('/api/environment/meda')
      .then(res => res.json())
      .then(data => {
        setMedaTelemetry(data);
        setSelectedSol(data.latest_sol.sol);
      })
      .catch(err => console.error("Error loading MEDA telemetry:", err));
  }, []);

  // Filtered discoveries based on selected objective
  const filteredDiscoveries = useMemo(() => {
    if (!selectedObjectiveId) return discoveries;
    return discoveries.filter(d => d.primary_objective_id === selectedObjectiveId);
  }, [discoveries, selectedObjectiveId]);

  // Current selected objective object
  const currentObjective = useMemo(() => {
    return objectives.find(o => o.id === selectedObjectiveId);
  }, [objectives, selectedObjectiveId]);

  // Current selected MEDA report
  const currentMedaReport = useMemo(() => {
    if (!medaTelemetry) return null;
    if (!selectedSol) return medaTelemetry.latest_sol;
    return medaTelemetry.recent_sols.find(s => s.sol === selectedSol) || medaTelemetry.latest_sol;
  }, [medaTelemetry, selectedSol]);

  // -----------------------------------------------------------
  // 2. Leaflet Map Initialization
  // -----------------------------------------------------------
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    // Initialize Leaflet Map centered on Jezero Crater
    // Center: 18.4447° N, 77.4508° E
    const map = L.map(mapContainerRef.current, {
      center: [18.4447, 77.4200],
      zoom: 12,
      minZoom: 4,
      maxZoom: 16,
      zoomControl: false,
      attributionControl: false
    });

    L.control.zoom({ position: 'topright' }).addTo(map);

    // Custom attribution control
    L.control.attribution({
      position: 'bottomright',
      prefix: 'USGS Astrogeology / NASA JPL / OpenPlanetaryMap'
    }).addTo(map);

    mapRef.current = map;

    // Tile Layers
    const opmLayer = L.tileLayer('https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-2/all/{z}/{x}/{y}.png', {
      maxZoom: 16,
      attribution: 'NASA/JPL/USGS/OPM'
    });

    const molaLayer = L.tileLayer('https://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/mola_color-noshade_global/{z}/{x}/{y}.png', {
      maxNativeZoom: 6,
      maxZoom: 16,
      attribution: 'NASA MOLA Topography'
    });

    const soilLayer = L.tileLayer('https://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/viking_mdim21_global/{z}/{x}/{y}.png', {
      maxNativeZoom: 6,
      maxZoom: 16,
      attribution: 'NASA/USGS Viking MDIM 2.1 Mosaic'
    });

    opmLayer.addTo(map);
    layersRef.current.basemaps = { OPM: opmLayer, MOLA: molaLayer, SOIL: soilLayer };
    layersRef.current.activeBasemap = "OPM";

    // Layer Groups
    layersRef.current.traverseGroup = L.layerGroup().addTo(map);
    layersRef.current.discoveriesGroup = L.layerGroup().addTo(map);
    layersRef.current.routeGroup = L.layerGroup().addTo(map);
    layersRef.current.hazardsGroup = L.layerGroup().addTo(map);
    layersRef.current.probeMarker = null;

    // Render Séítah Sand Hazard Boundary Polygon
    // Lon 77.436 to 77.447, Lat 18.427 to 18.438
    const seitahBounds = [
      [18.438, 77.436],
      [18.438, 77.447],
      [18.427, 77.447],
      [18.427, 77.436]
    ];
    L.polygon(seitahBounds, {
      color: '#e24e1b',
      weight: 1.5,
      dashArray: '4, 4',
      fillColor: '#c1440e',
      fillOpacity: 0.18
    }).bindTooltip("⚠️ Séítah Sand Dunes (High Wheel Slip Hazard)", { sticky: true }).addTo(layersRef.current.hazardsGroup);

    // Delta Front Scarp line annotation
    const deltaScarp = [
      [18.435, 77.412],
      [18.448, 77.408],
      [18.465, 77.395],
      [18.485, 77.375]
    ];
    L.polyline(deltaScarp, {
      color: '#00d2ff',
      weight: 1.5,
      dashArray: '2, 6',
      opacity: 0.7
    }).bindTooltip("Western Fan Delta Scarp (+70m ascent)", { sticky: true }).addTo(layersRef.current.hazardsGroup);

    // Click handler to inspect terrain elevation and slope
    map.on('click', (e) => {
      const { lat, lng } = e.latlng;
      fetch(`/api/elevation/point?lon=${lng.toFixed(5)}&lat=${lat.toFixed(5)}`)
        .then(res => res.json())
        .then(data => {
          setProbePoint(data);
          if (layersRef.current.probeMarker) {
            layersRef.current.probeMarker.setLatLng([lat, lng]);
          } else {
            layersRef.current.probeMarker = L.circleMarker([lat, lng], {
              radius: 6,
              color: '#00ffc8',
              fillColor: '#00ffc8',
              fillOpacity: 0.8
            }).addTo(map);
          }
        })
        .catch(err => console.error("Error inspecting elevation:", err));
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update Basemap Layer
  useEffect(() => {
    if (!mapRef.current || !layersRef.current.basemaps) return;
    const { basemaps, activeBasemap } = layersRef.current;
    if (layers.basemap !== activeBasemap) {
      if (basemaps[activeBasemap]) mapRef.current.removeLayer(basemaps[activeBasemap]);
      if (basemaps[layers.basemap]) basemaps[layers.basemap].addTo(mapRef.current);
      layersRef.current.activeBasemap = layers.basemap;
    }
  }, [layers.basemap]);

  // Toggle Overlay Layers
  useEffect(() => {
    if (!mapRef.current || !layersRef.current) return;
    const map = mapRef.current;
    const { traverseGroup, discoveriesGroup, routeGroup, hazardsGroup } = layersRef.current;

    if (traverseGroup) layers.showTraverse ? map.addLayer(traverseGroup) : map.removeLayer(traverseGroup);
    if (discoveriesGroup) layers.showDiscoveries ? map.addLayer(discoveriesGroup) : map.removeLayer(discoveriesGroup);
    if (routeGroup) layers.showRoute ? map.addLayer(routeGroup) : map.removeLayer(routeGroup);
    if (hazardsGroup) layers.showHazards ? map.addLayer(hazardsGroup) : map.removeLayer(hazardsGroup);
  }, [layers.showTraverse, layers.showDiscoveries, layers.showRoute, layers.showHazards]);

  // -----------------------------------------------------------
  // 3. Render NASA Perseverance Traverse
  // -----------------------------------------------------------
  useEffect(() => {
    if (!mapRef.current || !traverseGeoJSON || !layersRef.current.traverseGroup) return;
    const group = layersRef.current.traverseGroup;
    group.clearLayers();

    // Render historical LineString
    const lineFeature = traverseGeoJSON.features.find(f => f.geometry.type === "LineString");
    if (lineFeature) {
      const latlngs = lineFeature.geometry.coordinates.map(c => [c[1], c[0]]);
      L.polyline(latlngs, {
        color: '#ff6b35',
        weight: 2.5,
        opacity: 0.85
      }).addTo(group);
    }

    // Render Landing Marker (Octavia E. Butler Landing)
    const landingSite = traverseGeoJSON.features.find(f => {
      if (!f || !f.geometry || f.geometry.type !== "Point") return false;
      const name = String(f.properties?.name || f.properties?.waypoint_name || "");
      return name.includes("Sol 0") || f.properties?.sol === 0;
    });
    if (landingSite) {
      const [lon, lat] = landingSite.geometry.coordinates;
      const landingIcon = L.divIcon({
        className: 'custom-landing-marker',
        html: `
          <div style="background:#ff6b35; color:#07090e; font-weight:700; font-size:10px; padding:3px 6px; border-radius:4px; border:1px solid #fff; box-shadow:0 0 10px rgba(255,107,53,0.8); white-space:nowrap; display:flex; align-items:center; gap:4px;">
            <svg style="width:12px;height:12px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v20M2 12h20"/></svg>
            TOUCHDOWN (Sol 0)
          </div>
        `,
        iconSize: [110, 24],
        iconAnchor: [55, 12]
      });

      L.marker([lat, lon], { icon: landingIcon })
        .bindPopup(`
          <div style="font-size:12px; line-height:1.4;">
            <div style="font-weight:bold; color:#ff6b35; margin-bottom:4px;">OCTAVIA E. BUTLER LANDING</div>
            <div>Mars 2020 Perseverance Touchdown: Feb 18, 2021</div>
            <div>Coordinates: 18.4447°N, 77.4508°E</div>
            <div>Elevation: -2570m (MOLA Datum)</div>
          </div>
        `)
        .addTo(group);
    }
  }, [traverseGeoJSON]);

  // -----------------------------------------------------------
  // 4. Render Scientific Discoveries & Checkpoint Markers
  // -----------------------------------------------------------
  useEffect(() => {
    if (!mapRef.current || !discoveries || !layersRef.current.discoveriesGroup) return;
    const group = layersRef.current.discoveriesGroup;
    group.clearLayers();

    discoveries.forEach(disc => {
      const isSelected = (selectedCheckpointIds || []).includes(disc.id);
      const isCurrentObjective = disc.primary_objective_id === selectedObjectiveId;

      // Pin styling based on sample status and selection
      let pinColor = '#94a3b8'; // default
      if (disc.sample_acquired) pinColor = '#00ffc8'; // sample acquired
      const bio = String(disc.biosignature_potential || "");
      if (bio.includes("CRITICAL") || bio.includes("POTENTIAL")) pinColor = '#f59e0b';
      if (isSelected) pinColor = '#ff6b35';

      const customIcon = L.divIcon({
        className: 'discovery-marker-icon',
        html: `
          <div style="
            width: ${isSelected ? '24px' : '16px'};
            height: ${isSelected ? '24px' : '16px'};
            background: ${pinColor};
            border-radius: 50%;
            border: 2px solid ${isSelected ? '#ffffff' : '#0f172a'};
            box-shadow: 0 0 ${isSelected ? '14px' : '6px'} ${pinColor};
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
          ">
            ${isSelected ? '<div style="width:6px;height:6px;background:#ffffff;border-radius:50%;"></div>' : ''}
          </div>
        `,
        iconSize: [isSelected ? 24 : 16, isSelected ? 24 : 16],
        iconAnchor: [isSelected ? 12 : 8, isSelected ? 12 : 8]
      });

      const marker = L.marker([disc.latitude, disc.longitude], { icon: customIcon });

      // Popup Content
      marker.bindPopup(`
        <div style="min-width: 220px; font-size: 12px; font-family: 'Inter', sans-serif;">
          <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:4px; margin-bottom:6px;">
            <span style="font-weight:700; color:#ff6b35;">${disc.target_name}</span>
            <span style="color:#00d2ff; font-family:'JetBrains Mono'; font-size:11px;">Sol ${disc.sol}</span>
          </div>
          <div style="color:#cbd5e1; margin-bottom:6px; font-size:11px;">${disc.geological_formation}</div>
          <div style="color:#94a3b8; font-size:11px; margin-bottom:6px;"><strong>Lithology:</strong> ${disc.lithology}</div>
          ${disc.sample_acquired ? `<div style="color:#00ffc8; font-weight:600; font-size:11px; margin-bottom:6px;">🧪 Core Sample: ${disc.sample_name} (${disc.sample_tube_serial})</div>` : ''}
          <div style="color:#f59e0b; font-size:11px; margin-bottom:8px;"><strong>Biosignature:</strong> ${disc.biosignature_potential}</div>
          <button id="modal-btn-${disc.id}" style="
            background: #1e293b; 
            color: #f1f5f9; 
            border: 1px solid #475569; 
            border-radius: 4px; 
            padding: 4px 8px; 
            font-size: 11px; 
            cursor: pointer; 
            width: 100%;
          ">View Full Scientific Dossier</button>
        </div>
      `);

      marker.on('popupopen', () => {
        const btn = document.getElementById(`modal-btn-${disc.id}`);
        if (btn) {
          btn.onclick = () => setSelectedDiscoveryModal(disc);
        }
      });

      marker.addTo(group);
    });
  }, [discoveries, selectedCheckpointIds, selectedObjectiveId]);

  // -----------------------------------------------------------
  // 5. Render Planned Terrain-Aware Route
  // -----------------------------------------------------------
  useEffect(() => {
    if (!mapRef.current || !layersRef.current.routeGroup) return;
    const group = layersRef.current.routeGroup;
    group.clearLayers();

    if (!routeResult || !routeResult.path_geojson) return;

    const coords = routeResult.path_geojson.geometry.coordinates.map(c => [c[1], c[0]]);

    // Render continuous path line
    L.polyline(coords, {
      color: '#00ffc8',
      weight: 3.5,
      opacity: 0.9,
      dashArray: '6, 6'
    }).addTo(group);

    // Waypoint markers along planned route
    if (routeResult.waypoints) {
      routeResult.waypoints.forEach((wp, idx) => {
        const wpIcon = L.divIcon({
          className: 'route-wp-marker',
          html: `
            <div style="
              background: #00d2ff;
              color: #07090e;
              font-family: 'JetBrains Mono';
              font-weight: 700;
              font-size: 10px;
              width: 18px;
              height: 18px;
              border-radius: 50%;
              display: flex;
              align-items: center;
              justify-content: center;
              border: 2px solid #ffffff;
              box-shadow: 0 0 8px rgba(0,210,255,0.9);
            ">${idx + 1}</div>
          `,
          iconSize: [18, 18],
          iconAnchor: [9, 9]
        });

        L.marker([wp.latitude, wp.longitude], { icon: wpIcon })
          .bindTooltip(`Leg #${idx + 1}: ${wp.name} (${wp.elevation_m}m)`, { direction: 'top' })
          .addTo(group);
      });
    }

    // Zoom/fit route bounds if newly calculated
    if (coords.length > 0 && isCalculatingRoute) {
      mapRef.current.fitBounds(L.polyline(coords).getBounds(), { padding: [50, 50] });
    }
  }, [routeResult, isCalculatingRoute]);

  // Render cursor highlight on map when hovering elevation profile
  useEffect(() => {
    if (!mapRef.current || !layersRef.current) return;
    const map = mapRef.current;

    if (routeHoverPoint) {
      if (!layersRef.current.hoverMarker) {
        layersRef.current.hoverMarker = L.circleMarker([routeHoverPoint.latitude, routeHoverPoint.longitude], {
          radius: 7,
          color: '#f59e0b',
          fillColor: '#f59e0b',
          fillOpacity: 0.9,
          weight: 2
        }).addTo(map);
      } else {
        layersRef.current.hoverMarker.setLatLng([routeHoverPoint.latitude, routeHoverPoint.longitude]);
      }
    } else if (layersRef.current.hoverMarker) {
      map.removeLayer(layersRef.current.hoverMarker);
      layersRef.current.hoverMarker = null;
    }
  }, [routeHoverPoint]);

  // -----------------------------------------------------------
  // 6. Route Calculation Handler (A* on Rasterio DEM)
  // -----------------------------------------------------------
  const handleCalculateRoute = useCallback(() => {
    setIsCalculatingRoute(true);

    // Landing site as default start
    const payload = {
      start_point: [77.4508, 18.4447],
      checkpoint_ids: selectedCheckpointIds,
      preference: routePreference,
      max_safe_slope_deg: parseFloat(maxSafeSlope),
      avoid_sand_hazards: avoidSand,
      speed_kmh: 0.12
    };

    fetch('/api/route/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => {
        if (!res.ok) throw new Error("Pathfinding request failed");
        return res.json();
      })
      .then(data => {
        setRouteResult(data);
        setIsCalculatingRoute(false);
      })
      .catch(err => {
        console.error("Route calculation error:", err);
        setIsCalculatingRoute(false);
      });
  }, [selectedCheckpointIds, maxSafeSlope, avoidSand]);

  // Trigger route calculation when checkpoints change
  useEffect(() => {
    if ((selectedCheckpointIds || []).length > 0) {
      handleCalculateRoute();
    }
  }, [selectedCheckpointIds]);

  // Toggle Checkpoint Selection
  const toggleCheckpoint = (id) => {
    setSelectedCheckpointIds(prev => {
      const arr = prev || [];
      if (arr.includes(id)) {
        return arr.filter(item => item !== id);
      } else {
        return [...arr, id];
      }
    });
  };

  // Change Active Objective
  const handleSelectObjective = (objId) => {
    setSelectedObjectiveId(objId);
    const obj = objectives.find(o => o.id === objId);
    if (obj && obj.recommended_checkpoint_ids) {
      setSelectedCheckpointIds(obj.recommended_checkpoint_ids);
    }
  };

  // -----------------------------------------------------------
  // 7. Virtual Companion "ASTRA" Speech & Narration
  // -----------------------------------------------------------
  const currentWaypointDiscovery = useMemo(() => {
    if (!selectedCheckpointIds || selectedCheckpointIds.length === 0) return null;
    const safeIndex = Math.min(currentWaypointIndex, selectedCheckpointIds.length - 1);
    const discId = selectedCheckpointIds[safeIndex];
    return discoveries.find(d => d.id === discId);
  }, [selectedCheckpointIds, currentWaypointIndex, discoveries]);

  const speakText = useCallback((text) => {
    if (!isVoiceEnabled || !('speechSynthesis' in window) || !text) return;
    try {
      window.speechSynthesis.cancel(); // cancel previous
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 0.95;

      // Choose pleasant synthetic voice if available
      const voices = window.speechSynthesis.getVoices() || [];
      const englishVoice = voices.find(v => {
        if (!v || !v.name || !v.lang) return false;
        const name = String(v.name);
        const lang = String(v.lang);
        return lang.startsWith("en") && (name.includes("Google") || name.includes("Natural") || name.includes("Samantha"));
      });
      if (englishVoice) utterance.voice = englishVoice;

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.warn("Speech synthesis error:", err);
      setIsSpeaking(false);
    }
  }, [isVoiceEnabled]);

  // Speak companion insight when moving to new waypoint in Explorer Mode
  useEffect(() => {
    if (activeMode === "EXPLORER_MODE" && currentWaypointDiscovery) {
      const narrative = currentWaypointDiscovery.companion_insight;
      speakText(narrative);

      // Pan map smoothly to waypoint
      if (mapRef.current) {
        mapRef.current.flyTo([currentWaypointDiscovery.latitude, currentWaypointDiscovery.longitude], 14, {
          duration: 1.5
        });
      }
    }
  }, [activeMode, currentWaypointIndex, currentWaypointDiscovery, speakText]);

  // -----------------------------------------------------------
  // 8. RENDER INTERFACES
  // -----------------------------------------------------------
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-mars-darkest">

      {/* =======================================================
          TOP MISSION BANNER & CONTROL BAR
          ======================================================= */}
      <header className="h-14 border-b border-mars-border bg-mars-darker flex items-center justify-between px-4 z-20 shrink-0">
        {/* Brand & Mission Status */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-mars-rust to-mars-red flex items-center justify-center shadow-lg shadow-mars-red/20 border border-mars-orange/50">
            <span className="text-white font-mission font-bold text-sm">MV</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mission font-bold text-sm tracking-wider text-slate-100">MANGALVERSE</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-mars-rust/30 text-mars-orange border border-mars-rust/50 font-semibold">
                JEZERO CRATER
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/50 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                NASA VERIFIED
              </span>
            </div>
            <div className="text-[10px] font-mono text-slate-400 flex items-center space-x-3">
              <span>LAT: 18.4447°N</span>
              <span>LON: 77.4508°E</span>
              <span>DATUM: MOLA AREOID</span>
              <span className="text-mars-cyan">SOL {currentMedaReport ? currentMedaReport.sol : 1230}</span>
            </div>
          </div>
        </div>

        {/* Coherent Interface Switcher */}
        <div className="flex items-center bg-mars-panel p-1 rounded-lg border border-mars-border">
          <button
            onClick={() => setActiveMode("MISSION_CONTROL")}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-mono transition-all ${activeMode === "MISSION_CONTROL"
              ? "bg-mars-rust text-white shadow-md shadow-mars-rust/30 font-semibold"
              : "text-slate-400 hover:text-slate-200"
              }`}
          >
            <IconRocket />
            <span>MISSION CONTROL</span>
          </button>

          <button
            onClick={() => setActiveMode("EXPLORER_MODE")}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-mono transition-all ${activeMode === "EXPLORER_MODE"
              ? "bg-mars-cyan text-mars-darkest font-bold shadow-md shadow-mars-cyan/30"
              : "text-slate-400 hover:text-slate-200"
              }`}
          >
            <IconBot />
            <span>EXPLORER MODE</span>
          </button>
        </div>

        {/* Actions & Attribution */}
        <div className="flex items-center space-x-2">
          {activeMode === "EXPLORER_MODE" && (
            <button
              onClick={() => {
                const nextState = !isVoiceEnabled;
                setIsVoiceEnabled(nextState);
                if (!nextState && 'speechSynthesis' in window) window.speechSynthesis.cancel();
              }}
              className={`p-2 rounded border text-xs font-mono flex items-center gap-1 transition ${isVoiceEnabled
                ? "bg-mars-cyan/20 border-mars-cyan/50 text-mars-cyan"
                : "bg-mars-panel border-mars-border text-slate-400"
                }`}
              title={isVoiceEnabled ? "Mute Companion Voice" : "Enable Companion Voice"}
            >
              {isVoiceEnabled ? <IconVolume /> : <IconVolumeMute />}
              <span>ASTRA AUDIO</span>
            </button>
          )}

          <button
            onClick={() => setShowAttributionModal(true)}
            className="px-2.5 py-1.5 rounded bg-mars-panel hover:bg-mars-border border border-mars-border text-xs font-mono text-slate-300 flex items-center space-x-1.5 transition"
          >
            <IconInfo />
            <span>NASA SOURCES</span>
          </button>
        </div>
      </header>

      {/* =======================================================
          MAIN CONTENT AREA (Split Layout)
          ======================================================= */}
      <div className="flex-1 flex overflow-hidden relative">

        {/* -----------------------------------------------------
            INTERFACE 1: MISSION CONTROL VIEW
            ----------------------------------------------------- */}
        {activeMode === "MISSION_CONTROL" && (
          <aside className="w-96 border-r border-mars-border bg-mars-darker flex flex-col z-10 shrink-0">
            {/* Sidebar Tabs */}
            <div className="flex border-b border-mars-border bg-mars-panel text-xs font-mono">
              <button
                onClick={() => setActiveTab("WORKFLOW")}
                className={`flex-1 py-2.5 px-3 flex items-center justify-center space-x-1.5 border-b-2 transition ${activeTab === "WORKFLOW"
                  ? "border-mars-orange text-mars-orange bg-mars-darker font-semibold"
                  : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
              >
                <IconCompass />
                <span>PLANNER</span>
              </button>

              <button
                onClick={() => setActiveTab("ENVIRONMENT")}
                className={`flex-1 py-2.5 px-3 flex items-center justify-center space-x-1.5 border-b-2 transition ${activeTab === "ENVIRONMENT"
                  ? "border-mars-cyan text-mars-cyan bg-mars-darker font-semibold"
                  : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
              >
                <IconThermometer />
                <span>MEDA CLIMATE</span>
              </button>

              <button
                onClick={() => setActiveTab("LAYERS")}
                className={`flex-1 py-2.5 px-3 flex items-center justify-center space-x-1.5 border-b-2 transition ${activeTab === "LAYERS"
                  ? "border-emerald-400 text-emerald-400 bg-mars-darker font-semibold"
                  : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
              >
                <IconLayers />
                <span>LAYERS</span>
              </button>
            </div>

            {/* TAB 1: WORKFLOW & ROUTE PLANNING */}
            {activeTab === "WORKFLOW" && (
              <div className="flex-1 overflow-y-auto p-4 space-y-4">

                {/* Step 1: Scientific Objective */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
                      <span className="w-4 h-4 rounded-full bg-mars-rust text-white flex items-center justify-center text-[9px] font-bold">1</span>
                      Scientific Objective
                    </span>
                    <span className="text-[10px] font-mono text-mars-orange">{objectives.length} Missions</span>
                  </div>

                  <select
                    value={selectedObjectiveId}
                    onChange={(e) => handleSelectObjective(e.target.value)}
                    className="w-full bg-mars-panel border border-mars-border rounded px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-mars-orange"
                  >
                    {objectives.map(obj => (
                      <option key={obj.id} value={obj.id}>
                        {obj.code} - {obj.title}
                      </option>
                    ))}
                  </select>

                  {currentObjective && (
                    <div className="mt-2 p-2.5 rounded bg-mars-panel/60 border border-mars-border text-[11px] text-slate-300 space-y-1.5">
                      <p className="leading-relaxed">{currentObjective.description}</p>
                      <div className="pt-1.5 border-t border-mars-border flex flex-wrap gap-1">
                        {currentObjective.primary_instruments.map((inst, i) => (
                          <span key={i} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-mono border border-slate-700">
                            {inst}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Step 2: Target Discoveries & Checkpoints */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
                      <span className="w-4 h-4 rounded-full bg-mars-rust text-white flex items-center justify-center text-[9px] font-bold">2</span>
                      Target Checkpoints
                    </span>
                    <span className="text-[10px] font-mono text-mars-cyan">
                      {(selectedCheckpointIds || []).length} Selected
                    </span>
                  </div>

                  <div className="space-y-1.5 max-h-52 overflow-y-auto pr-1">
                    {filteredDiscoveries.map(disc => {
                      const isChecked = (selectedCheckpointIds || []).includes(disc.id);
                      return (
                        <div
                          key={disc.id}
                          onClick={() => toggleCheckpoint(disc.id)}
                          className={`p-2 rounded border cursor-pointer transition flex items-start space-x-2 ${isChecked
                            ? "bg-mars-panel border-mars-orange/60 shadow-sm"
                            : "bg-mars-darker hover:bg-mars-panel/50 border-mars-border"
                            }`}
                        >
                          <div className={`mt-0.5 w-3.5 h-3.5 rounded border flex items-center justify-center shrink-0 ${isChecked ? "bg-mars-orange border-mars-orange text-white" : "border-slate-600"
                            }`}>
                            {isChecked && <IconCheck />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-semibold text-slate-200 truncate">{disc.target_name}</span>
                              <span className="text-[10px] font-mono text-slate-400 shrink-0">Sol {disc.sol}</span>
                            </div>
                            <div className="text-[10px] text-slate-400 truncate">{disc.geological_formation}</div>
                            {disc.sample_acquired && (
                              <div className="text-[10px] text-emerald-400 font-mono flex items-center gap-1 mt-0.5">
                                <span>🧪 {disc.sample_name}</span>
                                <span className="text-slate-500">({disc.sample_tube_serial})</span>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Step 3: Rover Mobility Engineering Constraints */}
                <div className="p-3 rounded-lg bg-mars-panel/60 border border-mars-border space-y-3">
                  <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
                    <span className="w-4 h-4 rounded-full bg-mars-rust text-white flex items-center justify-center text-[9px] font-bold">3</span>
                    Rover Safety Constraints
                  </div>

                  {/* Slope Threshold Slider */}
                  <div>
                    <div className="flex justify-between text-xs font-mono mb-1">
                      <span className="text-slate-300">Max Safe Slope:</span>
                      <span className="text-mars-orange font-bold">{maxSafeSlope}° pitch</span>
                    </div>
                    <input
                      type="range"
                      min="8"
                      max="22"
                      step="1"
                      value={maxSafeSlope}
                      onChange={(e) => setMaxSafeSlope(parseFloat(e.target.value))}
                      className="w-full accent-mars-orange cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-0.5">
                      <span>Strict (8°)</span>
                      <span>Percy Limit (15°)</span>
                      <span>Extreme (22°)</span>
                    </div>
                  </div>

                  {/* Sand Avoidance Toggle */}
                  <label className="flex items-center justify-between text-xs font-mono cursor-pointer pt-1 border-t border-mars-border/60">
                    <span className="text-slate-300">Avoid Séítah Dune Fields:</span>
                    <input
                      type="checkbox"
                      checked={avoidSand}
                      onChange={(e) => setAvoidSand(e.target.checked)}
                      className="accent-mars-orange w-4 h-4 cursor-pointer"
                    />
                  </label>

                  {/* Route Optimization Preference */}
                  <div className="pt-2 border-t border-mars-border/60">
                    <div className="text-[10px] font-mono text-slate-400 mb-1 font-semibold uppercase">
                      Route Preference (Optimization Goal):
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      {[
                        { id: "SHORTEST", label: "SHORTEST", desc: "Min Dist" },
                        { id: "BALANCED", label: "BALANCED", desc: "Nominal" },
                        { id: "SAFEST", label: "SAFEST", desc: "Low Slope" }
                      ].map(p => (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => setRoutePreference(p.id)}
                          className={`py-1 px-1 rounded text-[10px] font-mono font-bold transition border flex flex-col items-center ${routePreference === p.id
                            ? "bg-mars-orange text-white border-mars-orange shadow"
                            : "bg-mars-darker text-slate-400 border-mars-border hover:text-slate-200"
                            }`}
                        >
                          <span>{p.label}</span>
                          <span className="text-[8px] opacity-80">{p.desc}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Step 4: Calculate Route Button */}
                <button
                  onClick={handleCalculateRoute}
                  disabled={isCalculatingRoute || (selectedCheckpointIds || []).length === 0}
                  className="w-full py-2.5 px-4 rounded bg-gradient-to-r from-mars-rust to-mars-orange hover:from-mars-red hover:to-mars-rust text-white font-mono text-xs font-bold uppercase tracking-wider shadow-lg shadow-mars-rust/20 border border-mars-orange/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition"
                >
                  {isCalculatingRoute ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Computing A* Terrain Path...</span>
                    </>
                  ) : (
                    <>
                      <IconCompass />
                      <span>Calculate Terrain-Aware Route</span>
                    </>
                  )}
                </button>

                {/* Route Metrics Summary */}
                {routeResult && (
                  <div className="space-y-2 pt-2 border-t border-mars-border">
                    <div className="text-[11px] font-mono text-slate-400 font-semibold uppercase tracking-wider">
                      Planned Route Metrics
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                      <div className="p-2 rounded bg-mars-panel border border-mars-border">
                        <div className="text-[10px] text-slate-400">Total Distance</div>
                        <div className="text-mars-orange font-bold text-sm">{routeResult.total_distance_km} km</div>
                      </div>

                      <div className="p-2 rounded bg-mars-panel border border-mars-border">
                        <div className="text-[10px] text-slate-400">Drive Duration</div>
                        <div className="text-mars-cyan font-bold text-sm">{routeResult.estimated_drive_duration_hours} hrs</div>
                      </div>

                      <div className="p-2 rounded bg-mars-panel border border-mars-border">
                        <div className="text-[10px] text-slate-400">Max / Avg Slope</div>
                        <div className="text-slate-200 font-bold text-sm">{routeResult.max_slope_deg}° / {routeResult.avg_slope_deg}°</div>
                      </div>

                      <div className="p-2 rounded bg-mars-panel border border-mars-border">
                        <div className="text-[10px] text-slate-400">Elevation Ascent</div>
                        <div className="text-emerald-400 font-bold text-sm">+{routeResult.total_elevation_gain_m} m</div>
                      </div>
                    </div>

                    {/* Safety Warnings */}
                    {routeResult.safety_warnings && routeResult.safety_warnings.length > 0 && (
                      <div className="p-2.5 rounded bg-amber-950/40 border border-amber-800/60 text-[11px] text-amber-300 space-y-1">
                        {routeResult.safety_warnings.map((warn, i) => (
                          <div key={i} className="flex items-start gap-1.5">
                            <span className="shrink-0 mt-0.5"><IconAlert /></span>
                            <span className="leading-tight">{warn}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

              </div>
            )}

            {/* TAB 2: MEDA ENVIRONMENTAL TELEMETRY */}
            {activeTab === "ENVIRONMENT" && (
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-xs font-mono font-bold text-slate-200 uppercase block">HISTORICAL MEDA OBSERVATIONS</span>
                    <span className="text-[10px] text-slate-400 font-mono">NASA PDS4 Mars 2020 Archive (Sols 1–1215)</span>
                  </div>
                  {medaTelemetry && (
                    <select
                      value={selectedSol || ''}
                      onChange={(e) => setSelectedSol(parseInt(e.target.value))}
                      className="bg-mars-panel border border-mars-border rounded px-2 py-1 text-xs font-mono text-mars-cyan"
                    >
                      {medaTelemetry.recent_sols.map(s => (
                        <option key={s.sol} value={s.sol}>
                          Sol {s.sol} ({s.season_name.split(' ')[0]})
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                {/* Provenance Disclosure Banner */}
                <div className="p-2.5 rounded bg-slate-900/90 border border-slate-700 text-[10px] font-mono text-slate-300 space-y-1">
                  <div className="flex items-center justify-between text-slate-400 font-bold">
                    <span>SCIENTIFIC PROVENANCE STATUS</span>
                    <span className="text-emerald-400">NASA PDS4 CERTIFIED</span>
                  </div>
                  <p className="text-[9px] text-slate-400 leading-tight">
                    Pressure and air temperature are calibrated in-situ observations from NASA PDS4 CAL_PS and CAL_ATS bundles. Ground temperature, wind, and dust opacity are regional scientific model estimates.
                  </p>
                </div>

                {currentMedaReport && (
                  <div className="space-y-3 font-mono">
                    {/* Observation Sol Banner */}
                    <div className="flex items-center justify-between px-2 py-1 rounded bg-mars-darker border border-slate-800 text-[11px] text-slate-400">
                      <span>Observation Sol: <b className="text-mars-cyan">{currentMedaReport.sol}</b></span>
                      <span>Earth: <b className="text-slate-200">{currentMedaReport.earth_date}</b></span>
                      <span>Ls: <b className="text-amber-400">{currentMedaReport.solar_longitude_ls}°</b></span>
                    </div>

                    {/* Atmospheric Pressure (Direct PDS Sensor) */}
                    <div className="p-3 rounded bg-mars-panel border border-emerald-900/50">
                      <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                        <span className="flex items-center gap-1.5"><IconGauge /> Atmospheric Pressure</span>
                        <div className="flex items-center gap-1.5">
                          <span className="px-1.5 py-0.5 rounded text-[8px] bg-emerald-950 text-emerald-400 border border-emerald-700/60 font-bold">AUTHENTIC PDS</span>
                          <span className="text-mars-cyan font-bold">{currentMedaReport.pressure_pa} Pa</span>
                        </div>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-emerald-400 h-full rounded-full"
                          style={{ width: `${Math.min(100, Math.max(0, ((currentMedaReport.pressure_pa - 550) / 300) * 100))}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                        <span>550 Pa (Vacuum)</span>
                        <span>{(currentMedaReport.pressure_pa / 100).toFixed(2)} hPa</span>
                        <span>850 Pa (Peak)</span>
                      </div>
                      <div className="text-[9px] text-emerald-500/80 mt-1">
                        Source: PDS4 Bundle urn:nasa:pds:mars2020_meda (CAL_PS Barocap)
                      </div>
                    </div>

                    {/* Temperatures (Air = Authentic PDS, Ground = Model) */}
                    <div className="p-3 rounded bg-mars-panel border border-mars-border space-y-2">
                      <div className="text-xs text-slate-400 flex items-center justify-between">
                        <span className="flex items-center gap-1.5"><IconThermometer /> Diurnal Temperature Range</span>
                        <span className="text-[9px] text-slate-500">In-situ vs Regional Model</span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="p-2 rounded bg-mars-darker border border-emerald-900/40">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-slate-400">Air Temp (1.5m)</span>
                            <span className="px-1 py-0.2 rounded text-[7px] bg-emerald-950 text-emerald-400 border border-emerald-700 font-bold">AUTHENTIC PDS</span>
                          </div>
                          <div className="text-mars-orange font-bold text-sm mt-0.5">{currentMedaReport.temp_air_avg_c}°C</div>
                          <div className="text-[9px] text-slate-400">{currentMedaReport.temp_air_min_c}°C to {currentMedaReport.temp_air_max_c}°C</div>
                          <div className="text-[8px] text-slate-500 mt-0.5">CAL_ATS 5-Sensor Array</div>
                        </div>

                        <div className="p-2 rounded bg-mars-darker border border-amber-900/40">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-slate-400">Ground Surface</span>
                            <span className="px-1 py-0.2 rounded text-[7px] bg-amber-950 text-amber-400 border border-amber-700 font-bold">MODEL ESTIMATE</span>
                          </div>
                          <div className="text-amber-400 font-bold text-sm mt-0.5">{currentMedaReport.temp_ground_avg_c}°C</div>
                          <div className="text-[9px] text-slate-400">{currentMedaReport.temp_ground_min_c}°C to {currentMedaReport.temp_ground_max_c}°C</div>
                          <div className="text-[8px] text-slate-500 mt-0.5">Regional Thermal Inertia</div>
                        </div>
                      </div>
                    </div>

                    {/* Wind & Dust Opacity (Model Estimates) */}
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="p-2.5 rounded bg-mars-panel border border-amber-900/40">
                        <div className="flex items-center justify-between text-[10px] text-slate-400 mb-0.5">
                          <span className="flex items-center gap-1"><IconWind /> Wind Speed</span>
                          <span className="px-1 py-0.2 rounded text-[7px] bg-amber-950 text-amber-400 border border-amber-700 font-bold">MODEL</span>
                        </div>
                        <div className="text-slate-100 font-bold text-sm">{currentMedaReport.wind_speed_avg_ms} m/s</div>
                        <div className="text-[9px] text-slate-500">Gusts to {currentMedaReport.wind_speed_max_ms} m/s • Regional GCM</div>
                      </div>

                      <div className="p-2.5 rounded bg-mars-panel border border-amber-900/40">
                        <div className="flex items-center justify-between text-[10px] text-slate-400 mb-0.5">
                          <span className="flex items-center gap-1"><IconShield /> Dust Tau (τ)</span>
                          <span className="px-1 py-0.2 rounded text-[7px] bg-amber-950 text-amber-400 border border-amber-700 font-bold">MODEL</span>
                        </div>
                        <div className="text-amber-400 font-bold text-sm">{currentMedaReport.dust_opacity_tau}</div>
                        <div className="text-[9px] text-slate-500">{currentMedaReport.dust_opacity_tau > 0.8 ? "Dust Storm Alert" : "Clear Sky"} • Climatology</div>
                      </div>
                    </div>

                    {/* Human & Rover Survival Assessment */}
                    <div className="p-3 rounded bg-slate-900 border border-slate-700 text-xs space-y-1.5">
                      <div className="text-emerald-400 font-bold flex items-center gap-1">
                        <IconShield /> Survival Assessment:
                      </div>
                      <p className="text-[11px] text-slate-300 leading-relaxed font-sans">{currentMedaReport.survival_assessment}</p>

                      <div className="pt-2 border-t border-slate-800 space-y-1">
                        <div className="text-[10px] text-slate-400 font-semibold uppercase">EVA Suit Parameters:</div>
                        {currentMedaReport.eva_suit_warnings.map((warn, i) => (
                          <div key={i} className="text-[10px] text-amber-300 font-sans flex items-start gap-1">
                            <span>•</span>
                            <span>{warn}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: MAP LAYERS & GIS SETTINGS */}
            {activeTab === "LAYERS" && (
              <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
                <div>
                  <div className="text-slate-400 font-semibold uppercase mb-2">Mars Surface Basemap</div>
                  <div className="space-y-1.5">
                    {[
                      { id: "OPM", name: "OpenPlanetaryMap Mars Surface", desc: "MDIM 2.1 Imagery + Nomenclature" },
                      { id: "MOLA", name: "USGS MOLA Color Topography", desc: "Color-coded elevation benchmarks" },
                      { id: "SOIL", name: "USGS Viking MDIM 2.1 Mosaic", desc: "Monochrome shaded relief morphology" }
                    ].map(b => (
                      <label
                        key={b.id}
                        className={`p-2 rounded border cursor-pointer flex flex-col transition ${layers.basemap === b.id
                          ? "bg-mars-panel border-mars-orange text-white"
                          : "bg-mars-darker border-mars-border text-slate-400 hover:text-slate-200"
                          }`}
                      >
                        <div className="flex items-center space-x-2">
                          <input
                            type="radio"
                            name="basemap"
                            value={b.id}
                            checked={layers.basemap === b.id}
                            onChange={() => setLayers(prev => ({ ...prev, basemap: b.id }))}
                            className="accent-mars-orange"
                          />
                          <span className="font-semibold">{b.name}</span>
                        </div>
                        <span className="text-[10px] text-slate-500 ml-5">{b.desc}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="pt-3 border-t border-mars-border">
                  <div className="text-slate-400 font-semibold uppercase mb-2">Overlays & Vectors</div>
                  <div className="space-y-2">
                    {[
                      { key: "showTraverse", label: "Perseverance Rover Traverse (Sols 0-1230)", color: "#ff6b35" },
                      { key: "showDiscoveries", label: "Scientific Target & Sample Pins", color: "#00ffc8" },
                      { key: "showRoute", label: "Calculated Terrain-Aware Route", color: "#00d2ff" },
                      { key: "showHazards", label: "Séítah Sand Dune Hazard Boundary", color: "#c1440e" }
                    ].map(item => (
                      <label key={item.key} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={layers[item.key]}
                          onChange={(e) => setLayers(prev => ({ ...prev, [item.key]: e.target.checked }))}
                          className="accent-mars-orange w-4 h-4 cursor-pointer"
                        />
                        <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: item.color }}></span>
                        <span className="text-slate-300">{item.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </aside>
        )}

        {/* -----------------------------------------------------
            INTERFACE 2: EXPLORER MODE VIEW
            ----------------------------------------------------- */}
        {activeMode === "EXPLORER_MODE" && (
          <aside className="w-96 border-r border-mars-border bg-mars-darker flex flex-col z-10 shrink-0">
            {/* Virtual Companion Header */}
            <div className="p-4 border-b border-mars-border bg-gradient-to-b from-mars-panel to-mars-darker">
              <div className="flex items-center space-x-3 mb-3">
                <div className="relative">
                  <img
                    src="/static/img/astra_avatar.png"
                    alt="ASTRA Virtual Companion"
                    className="w-16 h-16 object-contain drop-shadow-lg companion-pulse"
                  />
                  {isSpeaking && (
                    <div className="absolute -bottom-1 -right-1 px-1.5 py-0.2 rounded-full bg-mars-neon text-mars-darkest font-mono text-[9px] font-bold">
                      SPEAKING
                    </div>
                  )}
                </div>

                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mission font-bold text-sm text-slate-100">ASTRA VIRTUAL COMPANION</span>
                  </div>
                  <div className="text-[10px] font-mono text-mars-cyan">
                    Autonomous Scientific & Terrain Reconnaissance Assistant
                  </div>
                </div>
              </div>

              {/* Waypoint Step Navigation */}
              {(selectedCheckpointIds || []).length > 0 && (
                <div className="flex items-center justify-between bg-mars-darkest/70 p-2 rounded border border-mars-border text-xs font-mono">
                  <button
                    disabled={currentWaypointIndex <= 0}
                    onClick={() => setCurrentWaypointIndex(prev => Math.max(0, prev - 1))}
                    className="px-2 py-1 rounded bg-mars-panel hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
                  >
                    ◀ PREV
                  </button>

                  <span className="text-mars-orange font-bold">
                    LOCATION {currentWaypointIndex + 1} OF {(selectedCheckpointIds || []).length}
                  </span>

                  <button
                    disabled={currentWaypointIndex >= (selectedCheckpointIds || []).length - 1}
                    onClick={() => setCurrentWaypointIndex(prev => Math.min((selectedCheckpointIds || []).length - 1, prev + 1))}
                    className="px-2 py-1 rounded bg-mars-panel hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
                  >
                    NEXT ▶
                  </button>
                </div>
              )}
            </div>

            {/* Companion Dialogue & Deep-Dive Scientific Dossier */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {currentWaypointDiscovery ? (
                <>
                  {/* Speech Bubble Narrative */}
                  <div className="relative p-3.5 rounded-xl bg-gradient-to-br from-mars-panel to-slate-900 border border-mars-cyan/40 shadow-md shadow-mars-cyan/10">
                    <div className="text-xs font-mono text-mars-cyan font-semibold mb-1 flex items-center justify-between">
                      <span>ASTRA EXPEDITION LOG:</span>
                      <button
                        onClick={() => speakText(currentWaypointDiscovery.companion_insight)}
                        className="text-[10px] text-slate-400 hover:text-mars-cyan flex items-center gap-1"
                      >
                        <IconVolume /> Replay
                      </button>
                    </div>
                    <p className="text-xs text-slate-100 leading-relaxed font-sans">
                      "{currentWaypointDiscovery.companion_insight}"
                    </p>
                  </div>

                  {/* Scientific Fact Sheet */}
                  <div className="p-3.5 rounded-lg bg-mars-panel/60 border border-mars-border space-y-2.5 text-xs">
                    <div className="flex items-center justify-between border-b border-mars-border pb-2">
                      <span className="font-bold text-slate-100 text-sm">{currentWaypointDiscovery.target_name}</span>
                      <span className="font-mono text-mars-orange text-xs">Sol {currentWaypointDiscovery.sol}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                      <div>
                        <span className="text-slate-400">Elevation:</span>
                        <div className="text-slate-200 font-semibold">{currentWaypointDiscovery.elevation_m} m</div>
                      </div>
                      <div>
                        <span className="text-slate-400">Formation:</span>
                        <div className="text-slate-200 font-semibold truncate">{currentWaypointDiscovery.geological_formation}</div>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-mars-border/60">
                      <div className="text-[11px] font-mono text-slate-400 mb-1">Key Minerals Detected:</div>
                      <div className="flex flex-wrap gap-1">
                        {currentWaypointDiscovery.mineralogy_detected.map((m, i) => (
                          <span key={i} className="px-1.5 py-0.5 rounded bg-mars-darker text-mars-cyan text-[10px] font-mono border border-mars-border">
                            {m}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="pt-2 border-t border-mars-border/60">
                      <div className="text-[11px] font-mono text-slate-400 mb-0.5">Biosignature Potential:</div>
                      <div className="text-amber-400 font-semibold text-[11px]">{currentWaypointDiscovery.biosignature_potential}</div>
                    </div>

                    {currentWaypointDiscovery.sample_acquired && (
                      <div className="p-2 rounded bg-emerald-950/40 border border-emerald-800/60 text-emerald-300 text-[11px] font-mono">
                        <div className="font-bold">🧪 Hermetically Sealed Sample Acquired</div>
                        <div>Name: {currentWaypointDiscovery.sample_name}</div>
                        <div>Tube ID: {currentWaypointDiscovery.sample_tube_serial}</div>
                        <div className="text-[10px] text-emerald-400/80">Status: {currentWaypointDiscovery.cache_status}</div>
                      </div>
                    )}

                    <div className="pt-2 border-t border-mars-border/60 text-[10px] text-slate-500 font-mono">
                      <strong>NASA PDS Citation:</strong> {currentWaypointDiscovery.nasa_pds_citation}
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-8 text-center text-slate-500 font-mono text-xs">
                  Please select an objective and checkpoints in Mission Control to start guided Explorer Mode.
                </div>
              )}
            </div>
          </aside>
        )}

        {/* -----------------------------------------------------
            CENTER: INTERACTIVE MARS MAP (LEAFLET)
            ----------------------------------------------------- */}
        <div className="flex-1 flex flex-col relative h-full">
          {/* Map Viewport Container */}
          <div ref={mapContainerRef} className="flex-1 w-full h-full relative z-0"></div>

          {/* Terrain Inspection Overlay (Click Probe) */}
          {probePoint && (
            <div className="absolute top-4 left-4 z-10 glass-panel p-3 rounded-lg border border-mars-border text-xs font-mono shadow-xl max-w-xs space-y-1">
              <div className="flex items-center justify-between border-b border-mars-border/60 pb-1 mb-1">
                <span className="font-bold text-mars-neon flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-mars-neon animate-ping"></span>
                  TERRAIN PROBE
                </span>
                <button
                  onClick={() => setProbePoint(null)}
                  className="text-slate-400 hover:text-white text-xs px-1"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-1.5 text-slate-300">
                {probePoint.in_jezero_dem_bounds === false || probePoint.elevation_meters === null || probePoint.elevation_meters === undefined || probePoint.elevation_meters < -10000 || probePoint.elevation_meters > 30000 ? (
                  <div className="space-y-1.5 py-0.5">
                    <div className="text-amber-400 font-bold flex items-center gap-1">
                      <span>⚠</span>
                      <span>OUTSIDE JEZERO DEM COVERAGE</span>
                    </div>
                    <p className="text-[10px] text-slate-400 leading-tight">
                      Authentic USGS CTX (20m) & HiRISE (1m) DEM rasters are focused on Jezero Crater (~77.0°E–78.6°E, 17.6°N–19.3°N).
                    </p>
                    <button
                      onClick={() => {
                        if (mapRef.current) {
                          mapRef.current.setView([18.4447, 77.4200], 12);
                        }
                      }}
                      className="w-full mt-1 py-1 px-2 rounded bg-mars-orange/20 hover:bg-mars-orange/30 text-mars-orange border border-mars-orange/50 text-[10px] font-bold text-center transition flex items-center justify-center gap-1"
                    >
                      <span>🎯</span>
                      <span>Re-center on Jezero Crater</span>
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="flex justify-between">
                      <span>Elevation:</span>
                      <span className="font-bold text-white">{probePoint.elevation_meters} m</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Slope Pitch:</span>
                      <span className={`font-bold ${probePoint.slope_degrees > 15 ? 'text-rose-400' : (probePoint.slope_degrees > 10 ? 'text-amber-400' : 'text-emerald-400')}`}>
                        {probePoint.slope_degrees}° ({probePoint.terrain_classification || probePoint.terrain_hazard || 'NOMINAL'})
                      </span>
                    </div>
                    {probePoint.primary_source && (
                      <div className="text-[9px] text-cyan-400/80 truncate">
                        {probePoint.primary_source}
                      </div>
                    )}
                  </>
                )}
                <div className="flex justify-between text-slate-400 text-[10px] pt-1 border-t border-mars-border/40">
                  <span>Coordinates:</span>
                  <span>{probePoint.latitude}°N, {probePoint.longitude}°E</span>
                </div>
              </div>
            </div>
          )}

          {/* Quick Action: Re-center on Jezero button under zoom control */}
          <button
            onClick={() => {
              if (mapRef.current) {
                mapRef.current.setView([18.4447, 77.4200], 12);
              }
            }}
            title="Re-center map on Jezero Crater landing site"
            className="absolute top-20 right-3 z-10 glass-panel px-2 py-1.5 rounded border border-mars-border text-[10px] font-mono text-slate-300 hover:text-mars-orange hover:border-mars-orange shadow-lg flex items-center gap-1 transition"
          >
            <span>🎯</span>
            <span className="hidden sm:inline">Jezero</span>
          </button>

          {/* Map Legend Overlay */}
          <div className="absolute top-4 right-14 z-10 glass-panel px-3 py-2 rounded border border-mars-border text-[10px] font-mono text-slate-300 space-y-1 shadow-lg">
            <div className="text-slate-400 font-bold mb-1">MAP LEGEND</div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-mars-orange"></span>
              <span>Perseverance Traverse</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 border-t-2 border-dashed border-mars-neon"></span>
              <span>A* Planned Route</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              <span>Core Sample Cached</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
              <span>Organic/Biosignature</span>
            </div>
          </div>

          {/* ---------------------------------------------------
              BOTTOM DRAWER: ELEVATION PROFILE CHART
              --------------------------------------------------- */}
          {routeResult && routeResult.elevation_profile && routeResult.elevation_profile.length > 0 && (
            <div className="h-44 border-t border-mars-border bg-mars-darker/95 backdrop-blur px-4 py-2 flex flex-col z-10 shrink-0">
              <div className="flex items-center justify-between text-xs font-mono mb-1">
                <div className="flex items-center space-x-3">
                  <span className="font-bold text-mars-orange flex items-center gap-1.5">
                    <IconGauge /> TERRAIN-AWARE ELEVATION PROFILE
                  </span>
                  <span className="text-slate-400 text-[11px]">
                    Distance: {routeResult.total_distance_km} km | Gain: +{routeResult.total_elevation_gain_m}m | Max Pitch: {routeResult.max_slope_deg}°
                  </span>
                </div>

                {routeHoverPoint && (
                  <div className="text-mars-cyan text-[11px] font-bold">
                    At {(routeHoverPoint.distance_meters / 1000).toFixed(2)} km: Elev {routeHoverPoint.elevation_m}m (Slope {routeHoverPoint.slope_deg}°)
                  </div>
                )}
              </div>

              {/* Interactive SVG Elevation Chart */}
              <div className="flex-1 w-full relative">
                <ElevationSvgChart
                  profile={routeResult.elevation_profile}
                  onHover={(pt) => setRouteHoverPoint(pt)}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* =======================================================
          MODAL: FULL SCIENTIFIC DOSSIER (Perseverance Target)
          ======================================================= */}
      {selectedDiscoveryModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-mars-darker border border-mars-border rounded-xl max-w-xl w-full p-6 shadow-2xl relative space-y-4">
            <button
              onClick={() => setSelectedDiscoveryModal(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white font-mono text-sm"
            >
              ✕
            </button>

            <div className="flex items-center justify-between border-b border-mars-border pb-3">
              <div>
                <h2 className="text-lg font-mission font-bold text-mars-orange">{selectedDiscoveryModal.target_name}</h2>
                <div className="text-xs font-mono text-slate-400">
                  Jezero Crater | Sol {selectedDiscoveryModal.sol} ({selectedDiscoveryModal.earth_date})
                </div>
              </div>
              <span className="px-2.5 py-1 rounded bg-mars-panel text-mars-cyan font-mono text-xs border border-mars-border">
                {selectedDiscoveryModal.elevation_m}m Elev
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="font-mono text-slate-400 font-bold uppercase">Geological Context:</span>
                <p className="text-slate-200 mt-0.5 leading-relaxed">
                  <strong>Formation:</strong> {selectedDiscoveryModal.geological_formation}<br />
                  <strong>Lithology:</strong> {selectedDiscoveryModal.lithology}
                </p>
              </div>

              <div>
                <span className="font-mono text-slate-400 font-bold uppercase">Scientific Findings:</span>
                <p className="text-slate-200 mt-0.5 leading-relaxed">{selectedDiscoveryModal.scientific_summary}</p>
              </div>

              <div>
                <span className="font-mono text-slate-400 font-bold uppercase">Detected Minerals:</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {selectedDiscoveryModal.mineralogy_detected.map((m, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-mars-cyan font-mono text-[11px] border border-slate-700">
                      {m}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="font-mono text-slate-400 font-bold uppercase">Biosignature Significance:</span>
                <div className="p-2.5 rounded bg-amber-950/30 border border-amber-800/60 text-amber-300 mt-1">
                  {selectedDiscoveryModal.biosignature_potential}
                </div>
              </div>

              {selectedDiscoveryModal.sample_acquired && (
                <div className="p-3 rounded bg-emerald-950/30 border border-emerald-800/60 text-emerald-300 font-mono space-y-1">
                  <div className="font-bold">🧪 Hermetically Sealed Core Sample</div>
                  <div>Sample Name: {selectedDiscoveryModal.sample_name}</div>
                  <div>Titanium Tube Serial: {selectedDiscoveryModal.sample_tube_serial}</div>
                  <div>Depot / Carousel Status: {selectedDiscoveryModal.cache_status}</div>
                </div>
              )}

              <div className="p-2.5 rounded bg-mars-panel text-[11px] font-mono text-slate-400">
                <strong>NASA PDS / Science Publication Citation:</strong><br />
                {selectedDiscoveryModal.nasa_pds_citation}
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedDiscoveryModal(null)}
                className="px-4 py-2 rounded bg-mars-rust hover:bg-mars-red text-white font-mono text-xs font-semibold"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =======================================================
          MODAL: NASA ATTRIBUTION & PROVENANCE
          ======================================================= */}
      {showAttributionModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-mars-darker border border-mars-border rounded-xl max-w-xl w-full p-6 shadow-2xl relative space-y-4 font-mono text-xs">
            <button
              onClick={() => setShowAttributionModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white text-sm"
            >
              ✕
            </button>

            <div className="border-b border-mars-border pb-3">
              <h2 className="text-base font-mission font-bold text-slate-100 flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                NASA DATASET PROVENANCE & ATTRIBUTION
              </h2>
              <div className="text-[11px] text-slate-400 mt-1">
                Mangalverse complies with strict planetary data standards. All measurements, coordinates, and scientific analyses originate from authentic NASA mission releases.
              </div>
            </div>

            <div className="space-y-3">
              <div className="p-3 rounded bg-mars-panel border border-mars-border">
                <div className="text-mars-orange font-bold">1. Jezero Crater Elevation & Topography</div>
                <div className="text-slate-300 mt-0.5">MRO HiRISE Stereo DTM & CTX Mosaic / USGS Astrogeology Science Center.</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Fergason et al., Mars 2020 Terrain Relative Navigation (TRN) HiRISE DTM Mosaic, USGS Astropedia.</div>
              </div>

              <div className="p-3 rounded bg-mars-panel border border-mars-border">
                <div className="text-mars-cyan font-bold">2. Mars Environmental Dynamics Analyzer (MEDA)</div>
                <div className="text-slate-300 mt-0.5">Atmospheric pressure, air/ground temperature, dust optical depth (tau), and wind.</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Rodriguez-Manfredi et al., The Mars Environmental Dynamics Analyzer (MEDA) Instrument Suite, Space Sci Rev (2021).</div>
              </div>

              <div className="p-3 rounded bg-mars-panel border border-mars-border">
                <div className="text-emerald-400 font-bold">3. Perseverance Rover Scientific Discoveries & Samples</div>
                <div className="text-slate-300 mt-0.5">SHERLOC, PIXL, SuperCam, Mastcam-Z verified rock cores and observations.</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Farley et al., A lacustrine environment in Jezero crater, Mars, Science (2022); Scheller et al., Science (2022); Sharma et al., Nature (2023).</div>
              </div>

              <div className="p-3 rounded bg-mars-panel border border-mars-border">
                <div className="text-slate-200 font-bold">4. Rover Traverse & Localization Telemetry</div>
                <div className="text-slate-300 mt-0.5">NASA Jet Propulsion Laboratory (JPL) MMGIS & Planetary Data System (PDS) Geosciences Node.</div>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setShowAttributionModal(false)}
                className="px-4 py-2 rounded bg-mars-panel hover:bg-slate-700 text-slate-200 font-semibold border border-mars-border"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

// -------------------------------------------------------------
// SUBCOMPONENT: INTERACTIVE SVG ELEVATION CHART
// -------------------------------------------------------------
function ElevationSvgChart({ profile, onHover }) {
  if (!profile || profile.length < 2) return null;

  const width = 800;
  const height = 100;
  const padLeft = 40;
  const padRight = 20;
  const padTop = 15;
  const padBottom = 20;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  const dists = profile.map(p => p.distance_meters);
  const elevs = profile.map(p => p.elevation_m);

  const maxDist = Math.max(...dists);
  const minElev = Math.min(...elevs) - 5;
  const maxElev = Math.max(...elevs) + 5;
  const elevRange = maxElev - minElev || 1;

  // Build SVG Path
  const points = profile.map(p => {
    const x = padLeft + (p.distance_meters / (maxDist || 1)) * chartW;
    const y = padTop + chartH - ((p.elevation_m - minElev) / elevRange) * chartH;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const polylineStr = points.join(" ");
  const areaStr = `${padLeft},${padTop + chartH} ${polylineStr} ${padLeft + chartW},${padTop + chartH}`;

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const scaleX = width / rect.width;
    const svgX = clickX * scaleX;

    if (svgX >= padLeft && svgX <= padLeft + chartW) {
      const frac = (svgX - padLeft) / chartW;
      const targetDist = frac * maxDist;

      // Find closest profile point
      let closest = profile[0];
      let minDiff = Infinity;
      profile.forEach(p => {
        const diff = Math.abs(p.distance_meters - targetDist);
        if (diff < minDiff) {
          minDiff = diff;
          closest = p;
        }
      });
      onHover(closest);
    }
  };

  const handleMouseLeave = () => {
    onHover(null);
  };

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="w-full h-full cursor-crosshair overflow-visible"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <defs>
        <linearGradient id="elevationGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#00d2ff" stopOpacity="0.4" />
          <stop offset="100%" stopColor="#00d2ff" stopOpacity="0.0" />
        </linearGradient>
      </defs>

      {/* Grid Lines */}
      <line x1={padLeft} y1={padTop} x2={padLeft + chartW} y2={padTop} stroke="#1e293b" strokeDasharray="3,3" />
      <line x1={padLeft} y1={padTop + chartH / 2} x2={padLeft + chartW} y2={padTop + chartH / 2} stroke="#1e293b" strokeDasharray="3,3" />
      <line x1={padLeft} y1={padTop + chartH} x2={padLeft + chartW} y2={padTop + chartH} stroke="#334155" />

      {/* Elevation Area Fill & Curve */}
      <polygon points={areaStr} fill="url(#elevationGrad)" />
      <polyline points={polylineStr} fill="none" stroke="#00d2ff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />

      {/* Axis Labels */}
      <text x={padLeft - 6} y={padTop + 4} fill="#64748b" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">
        {Math.round(maxElev)}m
      </text>
      <text x={padLeft - 6} y={padTop + chartH + 3} fill="#64748b" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">
        {Math.round(minElev)}m
      </text>

      <text x={padLeft} y={height - 4} fill="#64748b" fontSize="9" fontFamily="JetBrains Mono">
        0 km
      </text>
      <text x={padLeft + chartW} y={height - 4} fill="#64748b" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">
        {(maxDist / 1000).toFixed(1)} km
      </text>
    </svg>
  );
}

// Mount the React Application
const rootElement = document.getElementById('root');
const root = ReactDOM.createRoot(rootElement);
root.render(<MarsExplorerApp />);
