// WorkflowPanel – Mission Control sidebar tabs: Planner / MEDA / Layers
import { useState } from 'react'
import {
  IconCompass, IconThermometer, IconLayers,
  IconGauge, IconWind, IconShield, IconAlert, IconCheck
} from './Icons'

// ── Step badge ───────────────────────────────────────────────────────────────
function StepBadge({ n }) {
  return (
    <span className="w-4 h-4 rounded-full bg-mars-rust text-white flex items-center justify-center text-[9px] font-bold shrink-0">
      {n}
    </span>
  )
}

// ── PLANNER tab ──────────────────────────────────────────────────────────────
function PlannerTab({
  objectives, selectedObjectiveId, currentObjective,
  filteredDiscoveries, selectedCheckpointIds,
  maxSafeSlope, avoidSand, routeResult, isCalculatingRoute,
  startPoint, destPoint, isComparingRoutes,
  onSelectObjective, onToggleCheckpoint, onSetMaxSlope, onToggleSand,
  onCalculateRoute, onCompareRoutes,
}) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">

      {/* Step 1: Objective */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
            <StepBadge n={1} /> Scientific Objective
          </span>
          <span className="text-[10px] font-mono text-mars-orange">{objectives.length} Missions</span>
        </div>

        <select
          value={selectedObjectiveId}
          onChange={e => onSelectObjective(e.target.value)}
          className="w-full bg-mars-panel border border-mars-border rounded px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-mars-orange"
        >
          {objectives.map(obj => (
            <option key={obj.id} value={obj.id}>{obj.code} – {obj.title}</option>
          ))}
        </select>

        {currentObjective && (
          <div className="mt-2 p-2.5 rounded bg-mars-panel/60 border border-mars-border text-[11px] text-slate-300 space-y-1.5">
            <p className="leading-relaxed">{currentObjective.description}</p>
            <div className="pt-1.5 border-t border-mars-border flex flex-wrap gap-1">
              {currentObjective.primary_instruments?.map((inst, i) => (
                <span key={i} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-mono border border-slate-700">{inst}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Step 2: Checkpoints */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
            <StepBadge n={2} /> Target Checkpoints
          </span>
          <span className="text-[10px] font-mono text-mars-cyan">{selectedCheckpointIds.length} Selected</span>
        </div>

        <div className="space-y-1.5 max-h-52 overflow-y-auto pr-1">
          {filteredDiscoveries.map(disc => {
            const isChecked = selectedCheckpointIds.includes(disc.id)
            return (
              <div
                key={disc.id}
                onClick={() => onToggleCheckpoint(disc.id)}
                className={`p-2 rounded border cursor-pointer transition flex items-start gap-2 ${
                  isChecked
                    ? 'bg-mars-panel border-mars-orange/60 shadow-sm'
                    : 'bg-mars-darker hover:bg-mars-panel/50 border-mars-border'
                }`}
              >
                <div className={`mt-0.5 w-3.5 h-3.5 rounded border flex items-center justify-center shrink-0 ${
                  isChecked ? 'bg-mars-orange border-mars-orange text-white' : 'border-slate-600'
                }`}>
                  {isChecked && <IconCheck className="w-2.5 h-2.5" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-xs font-semibold text-slate-200 truncate">{disc.target_name}</span>
                    <span className="text-[10px] font-mono text-slate-400 shrink-0">Sol {disc.sol}</span>
                  </div>
                  <div className="text-[10px] text-slate-400 truncate">{disc.geological_formation}</div>
                  {disc.sample_acquired && (
                    <div className="text-[10px] text-emerald-400 font-mono flex items-center gap-1 mt-0.5">
                      🧪 {disc.sample_name}
                      <span className="text-slate-500">({disc.sample_tube_serial})</span>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Step 3: Safety constraints */}
      <div className="p-3 rounded-lg bg-mars-panel/60 border border-mars-border space-y-3">
        <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
          <StepBadge n={3} /> Rover Safety Constraints
        </div>

        <div>
          <div className="flex justify-between text-xs font-mono mb-1">
            <span className="text-slate-300">Max Safe Slope:</span>
            <span className="text-mars-orange font-bold">{maxSafeSlope}° pitch</span>
          </div>
          <input
            type="range" min="8" max="22" step="1"
            value={maxSafeSlope}
            onChange={e => onSetMaxSlope(parseFloat(e.target.value))}
            className="w-full accent-mars-orange cursor-pointer"
          />
          <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-0.5">
            <span>Strict (8°)</span>
            <span>Percy Limit (15°)</span>
            <span>Extreme (22°)</span>
          </div>
        </div>

        <label className="flex items-center justify-between text-xs font-mono cursor-pointer pt-1 border-t border-mars-border/60">
          <span className="text-slate-300">Avoid Séítah Dune Fields:</span>
          <input
            type="checkbox" checked={avoidSand}
            onChange={e => onToggleSand(e.target.checked)}
            className="accent-mars-orange w-4 h-4 cursor-pointer"
          />
        </label>
      </div>

      {/* Step 4: Calculate */}
      <button
        onClick={onCalculateRoute}
        disabled={isCalculatingRoute || selectedCheckpointIds.length === 0}
        className="w-full py-2.5 px-4 rounded bg-gradient-to-r from-mars-rust to-mars-orange hover:from-mars-red hover:to-mars-rust text-white font-mono text-xs font-bold uppercase tracking-wider shadow-lg shadow-mars-rust/20 border border-mars-orange/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition"
      >
        {isCalculatingRoute ? (
          <>
            <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Computing A* Terrain Path…
          </>
        ) : (
          <>
            <IconCompass />
            Calculate Terrain-Aware Route
          </>
        )}
      </button>

      {/* Step 5: Compare Routes (3-way) */}
      <button
        onClick={onCompareRoutes}
        disabled={isComparingRoutes || !startPoint || !destPoint}
        className="w-full py-2.5 px-4 rounded bg-mars-darker hover:bg-mars-panel text-mars-cyan font-mono text-xs font-bold uppercase tracking-wider border border-mars-cyan/40 hover:border-mars-cyan/80 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition"
        title={!startPoint || !destPoint ? 'Set a start and destination on the map first' : 'Compare Shortest / Safest / Balanced routes'}
      >
        {isComparingRoutes ? (
          <>
            <div className="w-3.5 h-3.5 border-2 border-mars-cyan border-t-transparent rounded-full animate-spin" />
            Calculating 3 Routes…
          </>
        ) : (
          <>
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Compare 3 Routes
          </>
        )}
      </button>
      {(!startPoint || !destPoint) && (
        <p className="text-[10px] text-slate-500 font-mono text-center -mt-2">
          Use map tools to set Start &amp; Destination first
        </p>
      )}

      {/* Route metrics */}
      {routeResult && (
        <div className="space-y-2 pt-2 border-t border-mars-border">
          <div className="text-[11px] font-mono text-slate-400 font-semibold uppercase tracking-wider">
            Planned Route Metrics
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            {[
              { label: 'Total Distance', value: `${routeResult.total_distance_km} km`, color: 'text-mars-orange' },
              { label: 'Drive Duration', value: `${routeResult.estimated_drive_duration_hours} hrs`, color: 'text-mars-cyan' },
              { label: 'Max / Avg Slope', value: `${routeResult.max_slope_deg}° / ${routeResult.avg_slope_deg}°`, color: 'text-slate-200' },
              { label: 'Elevation Ascent', value: `+${routeResult.total_elevation_gain_m} m`, color: 'text-emerald-400' },
            ].map(m => (
              <div key={m.label} className="p-2 rounded bg-mars-panel border border-mars-border">
                <div className="text-[10px] text-slate-400">{m.label}</div>
                <div className={`font-bold text-sm ${m.color}`}>{m.value}</div>
              </div>
            ))}
          </div>

          {routeResult.safety_warnings?.length > 0 && (
            <div className="p-2.5 rounded bg-amber-950/40 border border-amber-800/60 text-[11px] text-amber-300 space-y-1">
              {routeResult.safety_warnings.map((w, i) => (
                <div key={i} className="flex items-start gap-1.5">
                  <span className="shrink-0 mt-0.5"><IconAlert /></span>
                  <span className="leading-tight">{w}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── MEDA tab ─────────────────────────────────────────────────────────────────
function EnvironmentTab({ medaTelemetry, selectedSol, onSelectSol, currentMedaReport }) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono font-bold text-slate-200 uppercase">MEDA Sol Observations</span>
        {medaTelemetry && (
          <select
            value={selectedSol ?? ''}
            onChange={e => onSelectSol(parseInt(e.target.value))}
            className="bg-mars-panel border border-mars-border rounded px-2 py-1 text-xs font-mono text-mars-cyan"
          >
            {medaTelemetry.recent_sols.map(s => (
              <option key={s.sol} value={s.sol}>Sol {s.sol} ({s.season_name?.split(' ')[0]})</option>
            ))}
          </select>
        )}
      </div>

      {currentMedaReport && (
        <div className="space-y-3 font-mono">
          {/* Pressure */}
          <div className="p-3 rounded bg-mars-panel border border-mars-border">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span className="flex items-center gap-1.5"><IconGauge /> Atmospheric Pressure</span>
              <span className="text-mars-cyan font-bold">{currentMedaReport.pressure_pa} Pa</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-mars-cyan h-full rounded-full"
                style={{ width: `${Math.min(100, Math.max(0, ((currentMedaReport.pressure_pa - 550) / 300) * 100))}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>550 Pa</span>
              <span>{(currentMedaReport.pressure_pa / 100).toFixed(2)} hPa</span>
              <span>850 Pa</span>
            </div>
            {/* Provenance badge (from Person 2 handover) */}
            {currentMedaReport.sol === 1 && (
              <div className="mt-2 flex items-start gap-1.5 p-1.5 rounded bg-amber-950/40 border border-amber-800/50 text-[10px] text-amber-300">
                <IconAlert className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />
                <span>Pressure data provisional – transducer switch during Sol 1 checkout</span>
              </div>
            )}
          </div>

          {/* Temperature */}
          <div className="p-3 rounded bg-mars-panel border border-mars-border space-y-2">
            <div className="text-xs text-slate-400 flex items-center gap-1.5"><IconThermometer /> Diurnal Temperature Range</div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded bg-mars-darker border border-slate-800">
                <div className="text-[10px] text-slate-500">Air Temp (1.5m)</div>
                <div className="text-mars-orange font-bold">{currentMedaReport.temp_air_avg_c}°C</div>
                <div className="text-[10px] text-slate-400">{currentMedaReport.temp_air_min_c}°C to {currentMedaReport.temp_air_max_c}°C</div>
              </div>
              <div className="p-2 rounded bg-mars-darker border border-slate-800">
                <div className="text-[10px] text-slate-500">Ground Surface</div>
                <div className="text-amber-400 font-bold">{currentMedaReport.temp_ground_avg_c}°C</div>
                <div className="text-[10px] text-slate-400">{currentMedaReport.temp_ground_min_c}°C to {currentMedaReport.temp_ground_max_c}°C</div>
              </div>
            </div>
          </div>

          {/* Wind & Dust */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 rounded bg-mars-panel border border-mars-border">
              <div className="text-[10px] text-slate-400 flex items-center gap-1"><IconWind /> Wind Speed</div>
              <div className="text-slate-100 font-bold text-sm mt-0.5">{currentMedaReport.wind_speed_avg_ms} m/s</div>
              <div className="text-[10px] text-slate-500">Gusts to {currentMedaReport.wind_speed_max_ms} m/s</div>
            </div>
            <div className="p-2.5 rounded bg-mars-panel border border-mars-border">
              <div className="text-[10px] text-slate-400 flex items-center gap-1"><IconShield /> Dust Tau (τ)</div>
              <div className="text-amber-400 font-bold text-sm mt-0.5">{currentMedaReport.dust_opacity_tau}</div>
              <div className="text-[10px] text-slate-500">
                {currentMedaReport.dust_opacity_tau > 0.8 ? 'Dust Storm Alert' : 'Clear Atmosphere'}
              </div>
            </div>
          </div>

          {/* Timestamps (UTC / LMST / LTST) */}
          {(currentMedaReport.utc_start || currentMedaReport.lmst_start) && (
            <div className="p-2.5 rounded bg-mars-panel border border-mars-border text-[10px] font-mono space-y-1">
              <div className="text-slate-400 font-semibold uppercase mb-1">Observation Window</div>
              {currentMedaReport.utc_start && (
                <div className="flex justify-between gap-2">
                  <span className="text-slate-500">UTC Start</span>
                  <span className="text-slate-300">{currentMedaReport.utc_start}</span>
                </div>
              )}
              {currentMedaReport.lmst_start && (
                <div className="flex justify-between gap-2">
                  <span className="text-slate-500">LMST Start</span>
                  <span className="text-slate-300">{currentMedaReport.lmst_start}</span>
                </div>
              )}
              {currentMedaReport.ltst_start && (
                <div className="flex justify-between gap-2">
                  <span className="text-slate-500">LTST Start</span>
                  <span className="text-slate-300">{currentMedaReport.ltst_start}</span>
                </div>
              )}
            </div>
          )}

          {/* Survival Assessment */}
          <div className="p-3 rounded bg-slate-900 border border-slate-700 text-xs space-y-1.5">
            <div className="text-emerald-400 font-bold flex items-center gap-1">
              <IconShield /> Survival Assessment:
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed font-sans">{currentMedaReport.survival_assessment}</p>
            {currentMedaReport.eva_suit_warnings?.length > 0 && (
              <div className="pt-2 border-t border-slate-800 space-y-1">
                <div className="text-[10px] text-slate-400 font-semibold uppercase">EVA Suit Parameters:</div>
                {currentMedaReport.eva_suit_warnings.map((w, i) => (
                  <div key={i} className="text-[10px] text-amber-300 font-sans flex items-start gap-1">
                    <span>•</span><span>{w}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {!currentMedaReport && (
        <div className="text-center text-slate-500 font-mono text-xs py-8">Loading MEDA telemetry…</div>
      )}
    </div>
  )
}

// ── LAYERS tab ───────────────────────────────────────────────────────────────
function LayersTab({ layers, setLayers }) {
  const basemaps = [
    { id: 'OPM',  name: 'OpenPlanetaryMap Mars Surface', desc: 'MDIM 2.1 Imagery + Nomenclature' },
    { id: 'MOLA', name: 'USGS MOLA Color Topography',   desc: 'Color-coded elevation benchmarks' },
    { id: 'SOIL', name: 'Mars Shaded Relief & Morphology', desc: 'Monochrome surface texture' },
  ]
  const overlays = [
    { key: 'showTraverse',    label: 'Perseverance Rover Traverse (Sols 0–1230)',  color: '#ff6b35' },
    { key: 'showDiscoveries', label: 'Scientific Target & Sample Pins',           color: '#00ffc8' },
    { key: 'showRoute',       label: 'Calculated Terrain-Aware Route',            color: '#00d2ff' },
    { key: 'showHazards',     label: 'Séítah Sand Dune Hazard Boundary',         color: '#c1440e' },
    { key: 'showElevation',   label: 'Elevation Contours (MOLA)',                 color: '#6366f1' },
    { key: 'showGeology',     label: 'Geological Units (USGS SIM 3464)',          color: '#8b5cf6' },
    { key: 'showEnvironment', label: 'Environmental Stations (MEDA)',             color: '#00ffc8' },
  ]

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
      <div>
        <div className="text-slate-400 font-semibold uppercase mb-2">Mars Surface Basemap</div>
        <div className="space-y-1.5">
          {basemaps.map(b => (
            <label key={b.id} className={`p-2 rounded border cursor-pointer flex flex-col transition ${
              layers.basemap === b.id
                ? 'bg-mars-panel border-mars-orange text-white'
                : 'bg-mars-darker border-mars-border text-slate-400 hover:text-slate-200'
            }`}>
              <div className="flex items-center gap-2">
                <input
                  type="radio" name="basemap" value={b.id}
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
          {overlays.map(item => (
            <label key={item.key} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={layers[item.key]}
                onChange={e => setLayers(prev => ({ ...prev, [item.key]: e.target.checked }))}
                className="accent-mars-orange w-4 h-4 cursor-pointer"
              />
              <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: item.color }} />
              <span className="text-slate-300">{item.label}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── Main exported component ──────────────────────────────────────────────────
function WorkflowPanel(props) {
  const [activeTab, setActiveTab] = useState('WORKFLOW')

  const tabs = [
    { id: 'WORKFLOW',    label: 'PLANNER',     icon: <IconCompass />, activeColor: 'border-mars-orange text-mars-orange' },
    { id: 'ENVIRONMENT', label: 'MEDA WEATHER', icon: <IconThermometer />, activeColor: 'border-mars-cyan text-mars-cyan' },
    { id: 'LAYERS',      label: 'LAYERS',       icon: <IconLayers />, activeColor: 'border-emerald-400 text-emerald-400' },
  ]

  return (
    <aside className="w-80 xl:w-96 border-r border-mars-border bg-mars-darker flex flex-col z-10 shrink-0">
      {/* Tab bar */}
      <div className="flex border-b border-mars-border bg-mars-panel text-xs font-mono">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`flex-1 py-2.5 px-2 flex items-center justify-center gap-1.5 border-b-2 transition ${
              activeTab === t.id
                ? `${t.activeColor} bg-mars-darker font-semibold`
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {t.icon}
            <span className="hidden sm:inline">{t.label}</span>
          </button>
        ))}
      </div>

      {activeTab === 'WORKFLOW'    && <PlannerTab     {...props} />}
      {activeTab === 'ENVIRONMENT' && <EnvironmentTab {...props} />}
      {activeTab === 'LAYERS'      && <LayersTab      layers={props.layers} setLayers={props.setLayers} />}
    </aside>
  )
}

export default WorkflowPanel
