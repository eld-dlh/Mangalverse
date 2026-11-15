// MARS EXPLORER – Root Application
// Orchestrates state, API calls, navigation, and renders all major views.

import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import LandingPage        from './components/LandingPage'
import TopBar             from './components/TopBar'
import WorkflowPanel      from './components/WorkflowPanel'
import ExplorerPanel      from './components/ExplorerPanel'
import MarsMap            from './components/MarsMap'
import MapOverlays        from './components/MapOverlays'
import LocationInfoPanel  from './components/mission/LocationInfoPanel'
import RouteComparisonPanel from './components/mission/RouteComparisonPanel'
import DossierModal       from './components/DossierModal'
import AttributionModal   from './components/AttributionModal'

// ── View states ──────────────────────────────────────────────────────────────
// 'LANDING' | 'MISSION_CONTROL' | 'EXPLORER_MODE'

function App() {
  // ── View ──────────────────────────────────────────────────────────────────
  const [view,       setView]       = useState('LANDING')
  const [activeMode, setActiveMode] = useState('MISSION_CONTROL')

  // ── Remote data ───────────────────────────────────────────────────────────
  const [objectives,      setObjectives]      = useState([])
  const [discoveries,     setDiscoveries]     = useState([])
  const [traverseGeoJSON, setTraverseGeoJSON] = useState(null)
  const [medaTelemetry,   setMedaTelemetry]   = useState(null)
  const [selectedSol,     setSelectedSol]     = useState(null)

  // ── Workflow ──────────────────────────────────────────────────────────────
  const [selectedObjectiveId,    setSelectedObjectiveId]    = useState('OBJ-1')
  const [selectedCheckpointIds,  setSelectedCheckpointIds]  = useState([])
  const [maxSafeSlope,           setMaxSafeSlope]           = useState(15)
  const [avoidSand,              setAvoidSand]              = useState(true)

  // ── Route ─────────────────────────────────────────────────────────────────
  const [routeResult,        setRouteResult]        = useState(null)
  const [isCalculatingRoute, setIsCalculatingRoute] = useState(false)
  const [routeHoverPoint,    setRouteHoverPoint]    = useState(null)
  const [routeComparison,    setRouteComparison]    = useState(null)
  const [isComparingRoutes,  setIsComparingRoutes]  = useState(false)
  const [selectedRouteVariant, setSelectedRouteVariant] = useState('balanced')

  // ── Map interaction state ─────────────────────────────────────────────────
  const [mapTool,       setMapTool]       = useState('pan')
  const [cursorPos,     setCursorPos]     = useState(null)
  const [zoom,          setZoom]          = useState(12)
  const [startPoint,    setStartPoint]    = useState(null)
  const [destPoint,     setDestPoint]     = useState(null)
  const [mapCheckpoints, setMapCheckpoints] = useState([])

  // ── Right panel (location info or route comparison) ───────────────────────
  const [rightPanel, setRightPanel] = useState(null) // { type: 'location'|'routes', data? }

  // ── Explorer Mode ─────────────────────────────────────────────────────────
  const [currentWaypointIndex, setCurrentWaypointIndex] = useState(0)
  const [isVoiceEnabled,       setIsVoiceEnabled]       = useState(true)
  const [isSpeaking,           setIsSpeaking]           = useState(false)

  // ── Map / UI ──────────────────────────────────────────────────────────────
  const [probePoint,        setProbePoint]        = useState(null)
  const [selectedDiscovery, setSelectedDiscovery] = useState(null)
  const [showAttribution,   setShowAttribution]   = useState(false)

  const [layers, setLayers] = useState({
    basemap:          'OPM',
    showTraverse:     true,
    showDiscoveries:  true,
    showRoute:        true,
    showHazards:      true,
    showElevation:    false,
    showGeology:      false,
    showEnvironment:  true,
  })

  // Leaflet map instance ref
  const mapInstanceRef = useRef(null)

  // ── Data fetching (once on mount) ─────────────────────────────────────────
  useEffect(() => {
    fetch('/api/objectives')
      .then(r => r.json())
      .then(data => {
        setObjectives(data)
        if (data.length) {
          setSelectedObjectiveId(data[0].id)
          setSelectedCheckpointIds(data[0].recommended_checkpoint_ids ?? [])
        }
      })
      .catch(() => {})

    fetch('/api/discoveries')
      .then(r => r.json())
      .then(setDiscoveries)
      .catch(() => {})

    fetch('/api/rover/traverse')
      .then(r => r.json())
      .then(setTraverseGeoJSON)
      .catch(() => {})

    fetch('/api/environment/meda')
      .then(r => r.json())
      .then(data => { setMedaTelemetry(data); setSelectedSol(data.latest_sol?.sol) })
      .catch(() => {})
  }, [])

  // ── Derived selectors ─────────────────────────────────────────────────────
  const filteredDiscoveries = useMemo(() => {
    if (!selectedObjectiveId) return discoveries
    return discoveries.filter(d => d.primary_objective_id === selectedObjectiveId)
  }, [discoveries, selectedObjectiveId])

  const currentObjective = useMemo(
    () => objectives.find(o => o.id === selectedObjectiveId),
    [objectives, selectedObjectiveId]
  )

  const currentMedaReport = useMemo(() => {
    if (!medaTelemetry) return null
    if (!selectedSol)   return medaTelemetry.latest_sol
    return medaTelemetry.recent_sols?.find(s => s.sol === selectedSol) ?? medaTelemetry.latest_sol
  }, [medaTelemetry, selectedSol])

  const currentWaypointDiscovery = useMemo(() => {
    if (!selectedCheckpointIds.length) return null
    const idx = Math.min(currentWaypointIndex, selectedCheckpointIds.length - 1)
    const id  = selectedCheckpointIds[idx]
    return discoveries.find(d => d.id === id) ?? null
  }, [selectedCheckpointIds, currentWaypointIndex, discoveries])

  // ── Route calculation ─────────────────────────────────────────────────────
  const handleCalculateRoute = useCallback(() => {
    setIsCalculatingRoute(true)
    fetch('/api/route/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_point: startPoint
          ? [startPoint.lng, startPoint.lat]
          : [77.4508, 18.4447],
        checkpoint_ids:    selectedCheckpointIds,
        max_safe_slope_deg: parseFloat(maxSafeSlope),
        avoid_sand_hazards: avoidSand,
        speed_kmh: 0.12,
      }),
    })
      .then(r => { if (!r.ok) throw new Error(); return r.json() })
      .then(data => { setRouteResult(data); setIsCalculatingRoute(false) })
      .catch(() => setIsCalculatingRoute(false))
  }, [selectedCheckpointIds, maxSafeSlope, avoidSand, startPoint])

  // Auto-recalculate when checkpoints change
  useEffect(() => {
    if (selectedCheckpointIds.length > 0) handleCalculateRoute()
  }, [selectedCheckpointIds]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Route comparison (3-way) ──────────────────────────────────────────────
  const handleRouteComparison = useCallback(async () => {
    if (!startPoint || !destPoint) return
    setIsComparingRoutes(true)
    setRightPanel({ type: 'routes' })

    try {
      const { fetchRouteComparison } = await import('./services/api')
      const data = await fetchRouteComparison({
        start:              [startPoint.lng, startPoint.lat],
        end:                [destPoint.lng,  destPoint.lat],
        waypoints:          mapCheckpoints.map(cp => [cp.lng, cp.lat]),
        checkpoint_ids:     selectedCheckpointIds,
        max_safe_slope_deg: maxSafeSlope,
        avoid_sand_hazards: avoidSand,
      })
      setRouteComparison(data)
    } catch (_) {
      // mock fallback already handled in api.js
    } finally {
      setIsComparingRoutes(false)
    }
  }, [startPoint, destPoint, mapCheckpoints, selectedCheckpointIds, maxSafeSlope, avoidSand])

  // ── Objective selection ───────────────────────────────────────────────────
  const handleSelectObjective = id => {
    setSelectedObjectiveId(id)
    const obj = objectives.find(o => o.id === id)
    if (obj?.recommended_checkpoint_ids) setSelectedCheckpointIds(obj.recommended_checkpoint_ids)
  }

  const toggleCheckpoint = id => {
    setSelectedCheckpointIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  // ── Map interaction callbacks ─────────────────────────────────────────────
  const handleSetStart = useCallback(pt => {
    setStartPoint(pt)
    setRightPanel({ type: 'location', data: { type: 'start', data: pt } })
  }, [])

  const handleSetDest = useCallback(pt => {
    setDestPoint(pt)
    setRightPanel({ type: 'location', data: { type: 'dest', data: pt } })
  }, [])

  const handleAddCheckpoint = useCallback(pt => {
    setMapCheckpoints(prev => [...prev, pt])
  }, [])

  const handleDiscoveryClick = useCallback(disc => {
    setRightPanel({ type: 'location', data: { type: 'discovery', data: disc } })
  }, [])

  const handleProbePoint = useCallback(pt => {
    setProbePoint(pt)
    setRightPanel({ type: 'location', data: { type: 'probe', data: pt } })
  }, [])

  const handleMapReady = useCallback(map => {
    mapInstanceRef.current = map
  }, [])

  const handleResetView = useCallback(() => {
    mapInstanceRef.current?.setView([18.4447, 77.42], 12)
  }, [])

  const handleFitDiscoveries = useCallback(() => {
    if (!mapInstanceRef.current || !discoveries.length) return
    const bounds = discoveries.map(d => [
      d.latitude  ?? d.lat,
      d.longitude ?? d.lon,
    ])
    if (bounds.length) mapInstanceRef.current.fitBounds(bounds, { padding: [40, 40] })
  }, [discoveries])

  // ── ARES speech synthesis ─────────────────────────────────────────────────
  const speakText = useCallback(text => {
    if (!isVoiceEnabled || !('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const utt   = new SpeechSynthesisUtterance(text)
    utt.rate    = 1.0
    utt.pitch   = 0.95
    const voices = window.speechSynthesis.getVoices()
    const best   = voices.find(v =>
      v.lang.startsWith('en') &&
      (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha'))
    )
    if (best) utt.voice = best
    utt.onstart = () => setIsSpeaking(true)
    utt.onend   = () => setIsSpeaking(false)
    utt.onerror = () => setIsSpeaking(false)
    window.speechSynthesis.speak(utt)
  }, [isVoiceEnabled])

  // Auto-narrate and fly to waypoint in Explorer Mode
  useEffect(() => {
    if (view !== 'EXPLORER_MODE' && activeMode !== 'EXPLORER_MODE') return
    if (!currentWaypointDiscovery) return
    speakText(currentWaypointDiscovery.companion_insight)
  }, [activeMode, view, currentWaypointIndex, currentWaypointDiscovery]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Navigation ────────────────────────────────────────────────────────────
  const handleSelectMode = mode => {
    setActiveMode(mode)
    setView(mode)
  }

  const handleSwitchMode = mode => {
    setActiveMode(mode)
    setView(mode)
  }

  // ── Landing page ──────────────────────────────────────────────────────────
  if (view === 'LANDING') {
    return <LandingPage onSelectMode={handleSelectMode} />
  }

  // ── Main platform ─────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-mars-darkest">

      <TopBar
        activeMode={activeMode}
        setActiveMode={handleSwitchMode}
        currentMedaReport={currentMedaReport}
        isVoiceEnabled={isVoiceEnabled}
        setIsVoiceEnabled={setIsVoiceEnabled}
        isSpeaking={isSpeaking}
        onShowAttribution={() => setShowAttribution(true)}
        onBackToLanding={() => setView('LANDING')}
      />

      <div className="flex-1 flex overflow-hidden relative">

        {/* ── MISSION CONTROL SIDEBAR ── */}
        {activeMode === 'MISSION_CONTROL' && (
          <WorkflowPanel
            objectives={objectives}
            selectedObjectiveId={selectedObjectiveId}
            currentObjective={currentObjective}
            filteredDiscoveries={filteredDiscoveries}
            selectedCheckpointIds={selectedCheckpointIds}
            maxSafeSlope={maxSafeSlope}
            avoidSand={avoidSand}
            routeResult={routeResult}
            isCalculatingRoute={isCalculatingRoute}
            medaTelemetry={medaTelemetry}
            selectedSol={selectedSol}
            currentMedaReport={currentMedaReport}
            layers={layers}
            setLayers={setLayers}
            startPoint={startPoint}
            destPoint={destPoint}
            isComparingRoutes={isComparingRoutes}
            onSelectObjective={handleSelectObjective}
            onToggleCheckpoint={toggleCheckpoint}
            onSetMaxSlope={setMaxSafeSlope}
            onToggleSand={setAvoidSand}
            onCalculateRoute={handleCalculateRoute}
            onCompareRoutes={handleRouteComparison}
            onSelectSol={setSelectedSol}
          />
        )}

        {/* ── EXPLORER MODE SIDEBAR ── */}
        {activeMode === 'EXPLORER_MODE' && (
          <ExplorerPanel
            discoveries={discoveries}
            selectedCheckpointIds={selectedCheckpointIds}
            currentWaypointIndex={currentWaypointIndex}
            currentWaypointDiscovery={currentWaypointDiscovery}
            currentMedaReport={currentMedaReport}
            isSpeaking={isSpeaking}
            speakText={speakText}
            onPrev={() => setCurrentWaypointIndex(i => Math.max(0, i - 1))}
            onNext={() => setCurrentWaypointIndex(i => Math.min(selectedCheckpointIds.length - 1, i + 1))}
            onSwitchToMission={() => handleSwitchMode('MISSION_CONTROL')}
            onFlyToDiscovery={(disc) => {
              const lat = disc.latitude ?? disc.lat
              const lon = disc.longitude ?? disc.lon
              if (lat != null && lon != null && mapInstanceRef.current) {
                mapInstanceRef.current.flyTo([lat, lon], 15, { duration: 1.5 })
              }
            }}
          />
        )}

        {/* ── MAP AREA ── */}
        <div className="flex-1 flex flex-col relative h-full overflow-hidden min-w-0">
          <MarsMap
            traverseGeoJSON={traverseGeoJSON}
            discoveries={discoveries}
            selectedCheckpointIds={selectedCheckpointIds}
            selectedObjectiveId={selectedObjectiveId}
            layers={layers}
            routeResult={routeResult}
            routeHoverPoint={routeHoverPoint}
            routeComparison={routeComparison}
            selectedRouteVariant={selectedRouteVariant}
            startPoint={startPoint}
            destPoint={destPoint}
            mapCheckpoints={mapCheckpoints}
            mapTool={mapTool}
            onProbePoint={handleProbePoint}
            onSetStart={handleSetStart}
            onSetDest={handleSetDest}
            onAddCheckpoint={handleAddCheckpoint}
            onDiscoveryClick={handleDiscoveryClick}
            onCursorMove={setCursorPos}
            onZoomChange={setZoom}
            onMapReady={handleMapReady}
          />
          <MapOverlays
            probePoint={probePoint}
            onClearProbe={() => { setProbePoint(null); setRightPanel(null) }}
            routeResult={routeResult}
            routeHoverPoint={routeHoverPoint}
            onSetRouteHoverPoint={setRouteHoverPoint}
            mapTool={mapTool}
            setMapTool={setMapTool}
            onResetView={handleResetView}
            onFitDiscoveries={handleFitDiscoveries}
            cursorPos={cursorPos}
            zoom={zoom}
            layers={layers}
            setLayers={setLayers}
          />
        </div>

        {/* ── RIGHT PANEL: Location Info ── */}
        {activeMode === 'MISSION_CONTROL' && rightPanel?.type === 'location' && (
          <LocationInfoPanel
            selection={rightPanel.data}
            onClose={() => setRightPanel(null)}
          />
        )}

        {/* ── RIGHT PANEL: Route Comparison ── */}
        {activeMode === 'MISSION_CONTROL' && (rightPanel?.type === 'routes' || isComparingRoutes) && (
          <RouteComparisonPanel
            routeComparison={routeComparison}
            isCalculating={isComparingRoutes}
            selectedVariant={selectedRouteVariant}
            onSelectVariant={setSelectedRouteVariant}
            onClose={() => setRightPanel(null)}
            startPoint={startPoint}
            destPoint={destPoint}
          />
        )}

      </div>

      {/* ── MODALS ── */}
      {selectedDiscovery && (
        <DossierModal discovery={selectedDiscovery} onClose={() => setSelectedDiscovery(null)} />
      )}
      {showAttribution && (
        <AttributionModal onClose={() => setShowAttribution(false)} />
      )}
    </div>
  )
}

export default App
