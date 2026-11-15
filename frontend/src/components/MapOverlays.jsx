// MapOverlays – all floating map overlays assembled in one place
// Renders inside the map container div (position: relative)

import ElevationChart   from './ElevationChart'
import MapToolbar       from './mission/MapToolbar'
import CoordinateHUD    from './mission/CoordinateHUD'
import LayerControlPanel from './mission/LayerControlPanel'
import { IconGauge, IconX } from './Icons'

function MapOverlays({
  // Terrain probe
  probePoint,
  onClearProbe,
  // Elevation profile
  routeResult,
  routeHoverPoint,
  onSetRouteHoverPoint,
  // Map tool
  mapTool,
  setMapTool,
  onResetView,
  onFitDiscoveries,
  // Cursor / zoom
  cursorPos,
  zoom,
  // Layers
  layers,
  setLayers,
}) {
  return (
    <>
      {/* ── Floating tool strip (left) ── */}
      <div className="absolute inset-0 pointer-events-none z-10">
        <div className="pointer-events-auto">
          <MapToolbar
            mapTool={mapTool}
            setMapTool={setMapTool}
            onResetView={onResetView}
            onFitDiscoveries={onFitDiscoveries}
          />
        </div>
      </div>

      {/* ── Layer control panel (top-right, above Leaflet zoom) ── */}
      <div className="absolute inset-0 pointer-events-none z-10">
        <div className="pointer-events-auto">
          <LayerControlPanel layers={layers} setLayers={setLayers} />
        </div>
      </div>

      {/* ── Terrain probe card (top-left, below toolbar) ── */}
      {probePoint && (
        <div className="absolute top-4 left-16 z-10 glass-panel p-3 rounded-lg border border-mars-neon/40 text-xs font-mono shadow-xl max-w-xs space-y-1 pointer-events-auto">
          <div className="flex items-center justify-between border-b border-mars-border/60 pb-1 mb-1">
            <span className="font-bold text-mars-neon flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-mars-neon animate-ping" />
              TERRAIN PROBE
            </span>
            <button onClick={onClearProbe} className="text-slate-400 hover:text-white px-1 transition" title="Dismiss">
              <IconX className="w-3 h-3" />
            </button>
          </div>
          <div className="flex justify-between text-slate-300">
            <span>Elevation:</span>
            <span className="font-bold text-white">{probePoint.elevation_meters ?? probePoint.elevation_m ?? '—'} m</span>
          </div>
          <div className="flex justify-between text-slate-300">
            <span>Slope Pitch:</span>
            <span className={`font-bold ${
              (probePoint.slope_degrees ?? 0) > 15 ? 'text-rose-400' :
              (probePoint.slope_degrees ?? 0) > 10 ? 'text-amber-400' : 'text-emerald-400'
            }`}>
              {probePoint.slope_degrees ?? '—'}° ({probePoint.terrain_hazard ?? '—'})
            </span>
          </div>
          <div className="flex justify-between text-slate-400 text-[10px] pt-1 border-t border-mars-border/40">
            <span>Coordinates:</span>
            <span>{(probePoint.latitude ?? probePoint.lat)?.toFixed(5)}°N, {(probePoint.longitude ?? probePoint.lng)?.toFixed(5)}°E</span>
          </div>
          {probePoint.data_source === 'mock' && (
            <div className="text-[9px] text-amber-500/70 pt-0.5">⚠ Estimated – backend not connected</div>
          )}
        </div>
      )}

      {/* ── Map legend (top-right, below layer panel button) ── */}
      <div className="absolute top-14 right-16 z-10 glass-panel px-3 py-2 rounded border border-mars-border text-[10px] font-mono text-slate-300 space-y-1 shadow-lg pointer-events-none">
        <div className="text-slate-400 font-bold mb-1 uppercase tracking-wider text-[9px]">Legend</div>
        {[
          { el: <span className="w-5 h-0.5 bg-mars-orange inline-block" />, label: 'Traverse' },
          { el: <span className="w-5 h-0.5 border-t-2 border-dashed border-mars-neon inline-block" />, label: 'A* Route' },
          { el: <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" />, label: 'Sample' },
          { el: <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />, label: 'Biosig.' },
          { el: <span className="w-2.5 h-2.5 rounded-full bg-mars-neon inline-block" />, label: 'Env. Station' },
        ].map((item, i) => (
          <div key={i} className="flex items-center gap-2">
            {item.el}
            <span>{item.label}</span>
          </div>
        ))}
      </div>

      {/* ── Coordinate HUD (bottom-left) ── */}
      <CoordinateHUD cursorPos={cursorPos} zoom={zoom} mapTool={mapTool} />

      {/* ── Elevation profile drawer (bottom) ── */}
      {routeResult?.elevation_profile?.length > 0 && (
        <div className="absolute bottom-10 left-0 right-0 h-40 border-t border-mars-border bg-mars-darker/95 backdrop-blur px-4 py-2 flex flex-col z-10 pointer-events-auto">
          <div className="flex items-center justify-between text-xs font-mono mb-1">
            <div className="flex items-center gap-3">
              <span className="font-bold text-mars-orange flex items-center gap-1.5">
                <IconGauge className="w-3.5 h-3.5" /> ELEVATION PROFILE
              </span>
              <span className="text-slate-400 text-[11px] hidden sm:inline">
                {routeResult.total_distance_km ?? routeResult.distance_km} km ·
                +{routeResult.total_elevation_gain_m ?? routeResult.elevation_gain_m}m ·
                Max {routeResult.max_slope_deg}°
              </span>
            </div>
            {routeHoverPoint && (
              <div className="text-mars-cyan text-[11px] font-bold">
                {(routeHoverPoint.distance_meters / 1000).toFixed(2)} km · {routeHoverPoint.elevation_m}m · {routeHoverPoint.slope_deg}°
              </div>
            )}
          </div>
          <div className="flex-1 w-full">
            <ElevationChart profile={routeResult.elevation_profile} onHover={onSetRouteHoverPoint} />
          </div>
        </div>
      )}
    </>
  )
}

export default MapOverlays
