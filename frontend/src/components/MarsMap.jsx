/**
 * MarsMap – Leaflet map component for MARS EXPLORER
 *
 * Responsibilities:
 *  - Renders the interactive Leaflet map focused on Jezero Crater
 *  - Manages all layer groups (traverse, discoveries, routes, hazards, geology, env stations)
 *  - Implements interaction modes: pan | probe | select-start | select-dest | add-checkpoint
 *  - Emits cursor position for CoordinateHUD
 *  - Exposes fitDiscoveries / resetView via imperative ref callbacks (passed as props)
 *  - Data is passed in via props; this component never fetches directly
 */

import { useEffect, useRef, useCallback } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix default marker icon path in Vite builds
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl:       'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl:     'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

// ── Helpers ───────────────────────────────────────────────────────────────────

function makeDiscoveryIcon(disc, isSelected, isCheckpoint) {
  let pinColor = '#94a3b8'
  if (disc.sample_acquired) pinColor = '#00ffc8'
  if ((disc.biosignature_potential > 0.6) || disc.biosignature_potential?.includes?.('CRITICAL') || disc.biosignature_potential?.includes?.('POTENTIAL'))
    pinColor = '#f59e0b'
  if (disc.type === 'hazard') pinColor = '#e24e1b'
  if (isCheckpoint) pinColor = '#00d2ff'
  if (isSelected)   pinColor = '#ff6b35'

  const size = isSelected || isCheckpoint ? 22 : 14
  const inner = isSelected || isCheckpoint
    ? `<div style="width:6px;height:6px;background:#fff;border-radius:50%;"></div>`
    : ''

  return L.divIcon({
    className: '',
    html: `<div style="
      width:${size}px;height:${size}px;
      background:${pinColor};border-radius:50%;
      border:2px solid ${isSelected ? '#fff' : '#0f172a'};
      box-shadow:0 0 ${isSelected ? 14 : 6}px ${pinColor};
      display:flex;align-items:center;justify-content:center;cursor:pointer;
    ">${inner}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

function makeWaypointIcon(idx) {
  return L.divIcon({
    className: '',
    html: `<div style="
      background:#00d2ff;color:#07090e;
      font-family:'JetBrains Mono',monospace;font-weight:700;font-size:10px;
      width:18px;height:18px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      border:2px solid #fff;box-shadow:0 0 8px rgba(0,210,255,.9);
    ">${idx + 1}</div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  })
}

function makeStartIcon() {
  return L.divIcon({
    className: '',
    html: `<div style="
      background:#10b981;color:#fff;
      font-family:monospace;font-size:9px;font-weight:700;
      padding:2px 5px;border-radius:4px;border:1.5px solid #fff;
      box-shadow:0 0 10px rgba(16,185,129,.8);white-space:nowrap;
    ">▶ START</div>`,
    iconSize: [56, 20], iconAnchor: [28, 10],
  })
}

function makeDestIcon() {
  return L.divIcon({
    className: '',
    html: `<div style="
      background:#ff6b35;color:#fff;
      font-family:monospace;font-size:9px;font-weight:700;
      padding:2px 5px;border-radius:4px;border:1.5px solid #fff;
      box-shadow:0 0 10px rgba(255,107,53,.8);white-space:nowrap;
    ">⬛ DEST</div>`,
    iconSize: [52, 20], iconAnchor: [26, 10],
  })
}

function makeCheckpointIcon(n) {
  return L.divIcon({
    className: '',
    html: `<div style="
      background:#00d2ff;color:#07090e;
      font-family:monospace;font-size:9px;font-weight:700;
      width:20px;height:20px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      border:2px solid #fff;box-shadow:0 0 8px rgba(0,210,255,.8);
    ">${n}</div>`,
    iconSize: [20, 20], iconAnchor: [10, 10],
  })
}

// ── Geological unit colors ────────────────────────────────────────────────────
const GEO_COLORS = {
  deltaic:    '#8b5cf6',
  lacustrine: '#6366f1',
  volcanic:   '#dc2626',
  ejecta:     '#d97706',
  fluvial:    '#0891b2',
  default:    '#64748b',
}

function geoColor(unit) {
  const rt = (unit?.rock_type ?? '').toLowerCase()
  for (const [k, v] of Object.entries(GEO_COLORS)) if (rt.includes(k)) return v
  return GEO_COLORS.default
}

// ── Mock environmental station coords (shown when showEnvironment is true) ────
const ENV_STATIONS = [
  { id: 'MEDA-1', name: 'MEDA Station α', lat: 18.4447, lng: 77.4508, temp_c: -58.1, pressure_pa: 743.2, wind_ms: 3.7 },
  { id: 'MEDA-2', name: 'MEDA Station β', lat: 18.4580, lng: 77.4120, temp_c: -59.4, pressure_pa: 741.8, wind_ms: 4.2 },
  { id: 'MEDA-3', name: 'MEDA Station γ', lat: 18.4310, lng: 77.4780, temp_c: -57.8, pressure_pa: 744.5, wind_ms: 3.1 },
]

// ── Mock geological unit polygons ─────────────────────────────────────────────
const MOCK_GEO_UNITS = [
  { id: 'g1', name: 'Western Fan Delta',    rock_type: 'deltaic',    coords: [[18.46,77.37],[18.47,77.41],[18.44,77.42],[18.43,77.38]] },
  { id: 'g2', name: 'Lacustrine Basin',     rock_type: 'lacustrine', coords: [[18.42,77.41],[18.44,77.46],[18.42,77.47],[18.40,77.43]] },
  { id: 'g3', name: 'Olivine-Bearing Unit', rock_type: 'volcanic',   coords: [[18.44,77.46],[18.46,77.49],[18.44,77.50],[18.42,77.47]] },
  { id: 'g4', name: 'Crater Rim Ejecta',   rock_type: 'ejecta',     coords: [[18.47,77.46],[18.49,77.50],[18.47,77.52],[18.45,77.49]] },
]

// ── Mock elevation contours ───────────────────────────────────────────────────
const MOCK_CONTOURS = [
  { elev: -2600, latlngs: [[18.41,77.38],[18.42,77.44],[18.41,77.50]] },
  { elev: -2550, latlngs: [[18.42,77.38],[18.44,77.44],[18.42,77.50]] },
  { elev: -2500, latlngs: [[18.44,77.37],[18.46,77.43],[18.44,77.49]] },
  { elev: -2450, latlngs: [[18.46,77.37],[18.48,77.42],[18.46,77.48]] },
  { elev: -2400, latlngs: [[18.47,77.37],[18.49,77.41],[18.47,77.47]] },
]

// ─────────────────────────────────────────────────────────────────────────────
// Main component
// ─────────────────────────────────────────────────────────────────────────────

function MarsMap({
  // Data props
  traverseGeoJSON,
  discoveries,
  selectedCheckpointIds,
  selectedObjectiveId,
  routeResult,
  routeHoverPoint,
  routeComparison,
  selectedRouteVariant,
  startPoint,
  destPoint,
  mapCheckpoints,
  // Layer visibility flags
  layers,
  // Interaction mode
  mapTool,
  // Callbacks
  onProbePoint,
  onSetStart,
  onSetDest,
  onAddCheckpoint,
  onDiscoveryClick,
  onCursorMove,
  onZoomChange,
  // Imperative handles
  onMapReady,
}) {
  const containerRef = useRef(null)
  const mapRef       = useRef(null)
  const lRef         = useRef({})
  const mapToolRef   = useRef(mapTool)  // always-current ref to avoid stale closures

  // Keep ref in sync
  useEffect(() => { mapToolRef.current = mapTool }, [mapTool])

  // ── Map cursor style ────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current) return
    const container = mapRef.current.getContainer()
    const cursors = {
      pan:            'grab',
      probe:          'crosshair',
      'select-start': 'cell',
      'select-dest':  'cell',
      'add-checkpoint':'copy',
    }
    container.style.cursor = cursors[mapTool] ?? 'grab'
  }, [mapTool])

  // ── Init ───────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    const map = L.map(containerRef.current, {
      center: [18.4447, 77.42],
      zoom: 12,
      minZoom: 4,
      maxZoom: 17,
      zoomControl: false,
      attributionControl: false,
    })

    L.control.zoom({ position: 'topright' }).addTo(map)
    L.control.attribution({
      position: 'bottomright',
      prefix: 'USGS Astrogeology · NASA JPL · OpenPlanetaryMap',
    }).addTo(map)

    // ── Basemap tile layers ────────────────────────────────────────────────
    const basemaps = {
      OPM:  L.tileLayer('https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-2/all/{z}/{x}/{y}.png', { maxZoom: 17, attribution: 'NASA/JPL/USGS/OPM' }),
      MOLA: L.tileLayer('https://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/mola_color-noshade_global/{z}/{x}/{y}.png',             { maxZoom: 16, attribution: 'NASA MOLA' }),
      SOIL: L.tileLayer('https://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/mars_soil_global/{z}/{x}/{y}.png',                      { maxZoom: 16, attribution: 'NASA/JPL Shaded Relief' }),
    }
    basemaps.OPM.addTo(map)

    // ── Layer groups ───────────────────────────────────────────────────────
    const groups = {
      traverse:     L.layerGroup().addTo(map),
      discoveries:  L.layerGroup().addTo(map),
      route:        L.layerGroup().addTo(map),
      hazards:      L.layerGroup().addTo(map),
      elevation:    L.layerGroup(),           // off by default
      geology:      L.layerGroup(),           // off by default
      environment:  L.layerGroup().addTo(map),
      waypoints:    L.layerGroup().addTo(map), // start/dest/checkpoint markers
    }

    // ── Static hazard overlays (always rendered in hazards group) ──────────
    L.polygon(
      [[18.438,77.436],[18.438,77.447],[18.427,77.447],[18.427,77.436]],
      { color: '#e24e1b', weight: 1.5, dashArray: '4,4', fillColor: '#c1440e', fillOpacity: 0.18 }
    ).bindTooltip('⚠️ Séítah Sand Dunes – High Wheel Slip Hazard', { sticky: true }).addTo(groups.hazards)

    L.polyline(
      [[18.435,77.412],[18.448,77.408],[18.465,77.395],[18.485,77.375]],
      { color: '#00d2ff', weight: 1.5, dashArray: '2,6', opacity: 0.6 }
    ).bindTooltip('Western Fan Delta Scarp (+70m ascent)', { sticky: true }).addTo(groups.hazards)

    // ── Elevation contours (static mock) ──────────────────────────────────
    MOCK_CONTOURS.forEach(c => {
      L.polyline(c.latlngs, { color: '#6366f1', weight: 1, opacity: 0.5, dashArray: '2,4' })
        .bindTooltip(`${c.elev} m`, { permanent: false, sticky: true, className: 'leaflet-tooltip-dark' })
        .addTo(groups.elevation)
    })

    // ── Geological units (static mock polygons) ────────────────────────────
    MOCK_GEO_UNITS.forEach(unit => {
      const color = geoColor(unit)
      L.polygon(unit.coords, {
        color, weight: 1.5, fillColor: color, fillOpacity: 0.12, dashArray: '3,5',
      })
        .bindTooltip(`${unit.name}<br><span style="font-size:10px;color:#94a3b8">${unit.rock_type}</span>`, { sticky: true })
        .addTo(groups.geology)
    })

    // ── Environmental stations (static mock) ──────────────────────────────
    ENV_STATIONS.forEach(st => {
      const icon = L.divIcon({
        className: '',
        html: `<div style="
          width:12px;height:12px;background:#00ffc8;border-radius:50%;
          border:2px solid #0f172a;box-shadow:0 0 8px #00ffc8;
        "></div>`,
        iconSize: [12, 12], iconAnchor: [6, 6],
      })
      L.marker([st.lat, st.lng], { icon })
        .bindPopup(`
          <div style="font-size:11px;font-family:JetBrains Mono,monospace;min-width:160px">
            <div style="color:#00ffc8;font-weight:700;margin-bottom:4px">${st.name}</div>
            <div>T: <b>${st.temp_c}°C</b></div>
            <div>P: <b>${st.pressure_pa} Pa</b></div>
            <div>Wind: <b>${st.wind_ms} m/s</b></div>
          </div>
        `)
        .addTo(groups.environment)
    })

    // ── Cursor tracking ────────────────────────────────────────────────────
    map.on('mousemove', e => {
      onCursorMove?.({ lat: e.latlng.lat, lng: e.latlng.lng })
    })
    map.on('mouseout', () => onCursorMove?.(null))
    map.on('zoom',     () => onZoomChange?.(map.getZoom()))

    // ── Click handler (delegated to mapToolRef) ────────────────────────────
    map.on('click', async e => {
      const { lat, lng } = e.latlng
      const tool = mapToolRef.current

      if (tool === 'probe') {
        // Fire elevation fetch; onProbePoint receives result
        try {
          const res = await fetch(`/api/elevation/point?lon=${lng.toFixed(5)}&lat=${lat.toFixed(5)}`)
          const data = res.ok ? await res.json() : {
            latitude: lat, longitude: lng,
            elevation_meters: -2500 + Math.round(Math.random() * 300),
            slope_degrees: +(Math.random() * 18).toFixed(1),
            terrain_hazard: 'SAFE',
            data_source: 'mock',
          }
          onProbePoint?.(data)
          // Update or create probe marker
          if (lRef.current.probeMarker) {
            lRef.current.probeMarker.setLatLng([lat, lng])
          } else {
            lRef.current.probeMarker = L.circleMarker([lat, lng], {
              radius: 6, color: '#00ffc8', fillColor: '#00ffc8', fillOpacity: 0.8,
            }).addTo(map)
          }
        } catch {}
      }

      else if (tool === 'select-start') {
        onSetStart?.({ lat, lng })
      }

      else if (tool === 'select-dest') {
        onSetDest?.({ lat, lng })
      }

      else if (tool === 'add-checkpoint') {
        onAddCheckpoint?.({ lat, lng })
      }
    })

    mapRef.current = map
    lRef.current = { basemaps, activeBasemap: 'OPM', groups, probeMarker: null, hoverMarker: null }

    // Notify parent (for resetView / fitDiscoveries handlers)
    onMapReady?.(map)

    return () => { map.remove(); mapRef.current = null }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Basemap switcher ────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !lRef.current.basemaps) return
    const { basemaps, activeBasemap } = lRef.current
    if (layers?.basemap && layers.basemap !== activeBasemap) {
      if (basemaps[activeBasemap]) mapRef.current.removeLayer(basemaps[activeBasemap])
      if (basemaps[layers.basemap]) basemaps[layers.basemap].addTo(mapRef.current)
      lRef.current.activeBasemap = layers.basemap
    }
  }, [layers?.basemap])

  // ── Overlay visibility toggles ──────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !lRef.current.groups) return
    const map = mapRef.current
    const g = lRef.current.groups

    const toggle = (group, flag) => {
      if (!group) return
      flag ? map.addLayer(group) : map.removeLayer(group)
    }

    toggle(g.traverse,    layers?.showTraverse    ?? true)
    toggle(g.discoveries, layers?.showDiscoveries ?? true)
    toggle(g.route,       layers?.showRoute       ?? true)
    toggle(g.hazards,     layers?.showHazards     ?? true)
    toggle(g.elevation,   layers?.showElevation   ?? false)
    toggle(g.geology,     layers?.showGeology     ?? false)
    toggle(g.environment, layers?.showEnvironment ?? true)
  }, [
    layers?.showTraverse, layers?.showDiscoveries, layers?.showRoute,
    layers?.showHazards,  layers?.showElevation,   layers?.showGeology,
    layers?.showEnvironment,
  ])

  // ── Traverse ────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !traverseGeoJSON) return
    const group = lRef.current.groups.traverse
    group.clearLayers()

    // Support both FeatureCollection and single Feature formats
    const features = traverseGeoJSON.features ?? [traverseGeoJSON]

    const lineFeature = features.find(f => f.geometry?.type === 'LineString')
    if (lineFeature) {
      L.polyline(lineFeature.geometry.coordinates.map(c => [c[1], c[0]]), {
        color: '#ff6b35', weight: 2.5, opacity: 0.85,
      })
        .bindTooltip('Perseverance Traverse (Sols 0–1230)', { sticky: true })
        .addTo(group)
    }

    // Landing marker
    const landing = features.find(f =>
      f.geometry?.type === 'Point' && f.properties?.name?.includes('Sol 0')
    )
    if (landing) {
      const [lon, lat] = landing.geometry.coordinates
      L.marker([lat, lon], {
        icon: L.divIcon({
          className: '',
          html: `<div style="background:#ff6b35;color:#07090e;font-weight:700;font-size:10px;padding:3px 6px;border-radius:4px;border:1px solid #fff;box-shadow:0 0 10px rgba(255,107,53,.8);white-space:nowrap;">TOUCHDOWN (Sol 0)</div>`,
          iconSize: [120, 22], iconAnchor: [60, 11],
        }),
      })
        .bindPopup(`<div style="font-size:12px"><b style="color:#ff6b35">OCTAVIA E. BUTLER LANDING</b><br>18 Feb 2021 · 18.4447°N 77.4508°E</div>`)
        .addTo(group)
    }
  }, [traverseGeoJSON])

  // ── Discovery markers ───────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !discoveries?.length) return
    const group = lRef.current.groups.discoveries
    group.clearLayers()

    discoveries.forEach(disc => {
      const isSelected   = selectedCheckpointIds?.includes(disc.id)
      const isCheckpoint = !!isSelected

      // Support both {lat,lon} and {latitude,longitude} shapes
      const lat = disc.latitude ?? disc.lat
      const lon = disc.longitude ?? disc.lon
      if (!lat || !lon) return

      const marker = L.marker([lat, lon], {
        icon: makeDiscoveryIcon(disc, isSelected, isCheckpoint),
        zIndexOffset: isSelected ? 100 : 0,
      })

      const name = disc.target_name ?? disc.name ?? disc.id
      const sol  = disc.sol ?? '—'

      marker.bindPopup(`
        <div style="min-width:220px;font-size:12px;font-family:Inter,sans-serif;">
          <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #334155;padding-bottom:4px;margin-bottom:6px;">
            <span style="font-weight:700;color:#ff6b35;">${name}</span>
            <span style="color:#00d2ff;font-size:11px;">Sol ${sol}</span>
          </div>
          ${disc.geological_formation ? `<div style="color:#cbd5e1;font-size:11px;margin-bottom:4px;">${disc.geological_formation}</div>` : ''}
          ${disc.description ? `<div style="color:#94a3b8;font-size:11px;">${disc.description}</div>` : ''}
          ${disc.sample_acquired ? `<div style="color:#00ffc8;font-size:11px;margin-top:4px;">🧪 ${disc.sample_name ?? 'Core sample cached'}</div>` : ''}
        </div>
      `)

      marker.on('click', () => onDiscoveryClick?.(disc))
      marker.addTo(group)
    })
  }, [discoveries, selectedCheckpointIds, selectedObjectiveId]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Route (single result or selected variant) ───────────────────────────────
  useEffect(() => {
    if (!mapRef.current) return
    const group = lRef.current.groups.route
    group.clearLayers()

    // Pick active route: comparison variant takes precedence over single result
    let activeRoute = null
    if (routeComparison && selectedRouteVariant) {
      activeRoute = routeComparison[selectedRouteVariant]
    } else if (routeResult) {
      activeRoute = routeResult
    }

    if (!activeRoute) return

    const coords = activeRoute.path_geojson?.geometry?.coordinates?.map(c => [c[1], c[0]])
    if (!coords?.length) return

    // Choose color based on variant
    const colorMap = { shortest: '#ff6b35', safest: '#10b981', balanced: '#00d2ff' }
    const lineColor = colorMap[selectedRouteVariant] ?? '#00ffc8'

    L.polyline(coords, { color: lineColor, weight: 3.5, opacity: 0.9, dashArray: '7,5' })
      .bindTooltip(`${activeRoute.label ?? 'Route'} · ${activeRoute.distance_km} km`, { sticky: true })
      .addTo(group)

    // Waypoint markers
    activeRoute.waypoints?.forEach((wp, idx) => {
      L.marker([wp.latitude, wp.longitude], { icon: makeWaypointIcon(idx) })
        .bindTooltip(`Leg #${idx + 1}: ${wp.name} (${wp.elevation_m}m)`, { direction: 'top' })
        .addTo(group)
    })
  }, [routeResult, routeComparison, selectedRouteVariant])

  // ── Comparison route ghost lines ────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current || !routeComparison) return
    // Ghost lines are drawn in the route group at reduced opacity
    // Active route is already drawn above; ghosts show the other two faintly
    const group = lRef.current.groups.route
    // We only redraw ghosts when the full comparison changes
    // (actual active route redraw is handled in the effect above)
  }, [routeComparison]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Route hover cursor ──────────────────────────────────────────────────────
  useEffect(() => {
    if (!mapRef.current) return
    const map = mapRef.current
    if (routeHoverPoint) {
      const ll = [routeHoverPoint.latitude, routeHoverPoint.longitude]
      if (!lRef.current.hoverMarker) {
        lRef.current.hoverMarker = L.circleMarker(ll, {
          radius: 7, color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.9, weight: 2,
        }).addTo(map)
      } else {
        lRef.current.hoverMarker.setLatLng(ll)
      }
    } else if (lRef.current.hoverMarker) {
      map.removeLayer(lRef.current.hoverMarker)
      lRef.current.hoverMarker = null
    }
  }, [routeHoverPoint])

  // ── Start / Destination / Checkpoint waypoint markers ──────────────────────
  useEffect(() => {
    if (!mapRef.current) return
    const group = lRef.current.groups.waypoints
    group.clearLayers()

    if (startPoint) {
      L.marker([startPoint.lat, startPoint.lng], { icon: makeStartIcon(), zIndexOffset: 500 }).addTo(group)
    }
    if (destPoint) {
      L.marker([destPoint.lat, destPoint.lng], { icon: makeDestIcon(), zIndexOffset: 500 }).addTo(group)
    }
    mapCheckpoints?.forEach((cp, i) => {
      L.marker([cp.lat, cp.lng], { icon: makeCheckpointIcon(i + 1), zIndexOffset: 400 })
        .bindTooltip(`Checkpoint ${i + 1}`, { direction: 'top' })
        .addTo(group)
    })

    // Draw a dashed line connecting start → checkpoints → dest
    const pts = [startPoint, ...(mapCheckpoints ?? []), destPoint].filter(Boolean)
    if (pts.length >= 2) {
      L.polyline(pts.map(p => [p.lat, p.lng]), {
        color: '#64748b', weight: 1.5, dashArray: '4,6', opacity: 0.5,
      }).addTo(group)
    }
  }, [startPoint, destPoint, mapCheckpoints])

  return <div ref={containerRef} className="w-full h-full" />
}

export default MarsMap
