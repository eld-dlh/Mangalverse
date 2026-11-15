// LayerControlPanel – GIS-style floating layer control
// Collapsible panel: collapsed = icon button, expanded = full layer tree

import { useState } from 'react'

// ── Toggle switch ─────────────────────────────────────────────────────────────
function ToggleSwitch({ checked, onChange, color = 'bg-mars-neon' }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-4 w-7 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none ${
        checked ? color : 'bg-slate-700'
      }`}
    >
      <span
        className={`inline-block h-3 w-3 transform rounded-full bg-white shadow transition-transform duration-200 ${
          checked ? 'translate-x-3' : 'translate-x-0'
        }`}
      />
    </button>
  )
}

// ── Color dot ────────────────────────────────────────────────────────────────
function Dot({ color }) {
  return <span className="w-2 h-2 rounded-full shrink-0 inline-block" style={{ background: color }} />
}

// ── Layer row ─────────────────────────────────────────────────────────────────
function LayerRow({ dot, label, sublabel, checked, onChange, color }) {
  return (
    <div className="flex items-center justify-between gap-2 py-1.5">
      <div className="flex items-center gap-2 min-w-0">
        <Dot color={dot} />
        <div className="min-w-0">
          <div className="text-[11px] font-mono text-slate-300 leading-tight truncate">{label}</div>
          {sublabel && <div className="text-[9px] font-mono text-slate-600 leading-tight">{sublabel}</div>}
        </div>
      </div>
      <ToggleSwitch checked={checked} onChange={onChange} color={color} />
    </div>
  )
}

// ── Icons ─────────────────────────────────────────────────────────────────────
const IconLayers = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
    <polygon points="12 2 2 7 12 12 22 7 12 2"/>
    <polyline points="2 17 12 22 22 17"/>
    <polyline points="2 12 12 17 22 12"/>
  </svg>
)

const IconX = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
)

// ── Basemap option ────────────────────────────────────────────────────────────
const BASEMAPS = [
  { id: 'OPM',  label: 'Mars Surface',    sub: 'OPM / MDIM 2.1' },
  { id: 'MOLA', label: 'MOLA Topography', sub: 'Color elevation' },
  { id: 'SOIL', label: 'Shaded Relief',   sub: 'Surface morphology' },
]

// ── Main component ────────────────────────────────────────────────────────────
function LayerControlPanel({ layers, setLayers }) {
  const [open, setOpen] = useState(false)

  const set = key => val => setLayers(prev => ({ ...prev, [key]: val }))
  const setBasemap = id => setLayers(prev => ({ ...prev, basemap: id }))

  return (
    <div className="absolute top-4 right-16 z-20 pointer-events-auto">
      {/* Collapsed button */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          title="Open layer control"
          className="flex items-center gap-1.5 bg-mars-darker/90 border border-mars-border rounded-lg px-3 py-2 backdrop-blur-sm shadow-lg text-slate-300 hover:text-white hover:border-mars-border/80 transition-all text-[11px] font-mono uppercase tracking-wider"
        >
          <IconLayers />
          <span>Layers</span>
        </button>
      )}

      {/* Expanded panel */}
      {open && (
        <div className="w-56 bg-mars-darker/95 border border-mars-border rounded-xl backdrop-blur-sm shadow-2xl overflow-hidden">

          {/* Header */}
          <div className="flex items-center justify-between px-3 py-2.5 border-b border-mars-border bg-mars-panel/60">
            <div className="flex items-center gap-2 text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-200">
              <IconLayers />
              Map Layers
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-slate-500 hover:text-white transition-colors p-0.5"
              title="Close"
            >
              <IconX />
            </button>
          </div>

          <div className="px-3 py-2 space-y-3 max-h-[75vh] overflow-y-auto">

            {/* ── Basemap ── */}
            <div>
              <div className="text-[9px] font-mono uppercase tracking-widest text-slate-500 mb-1.5">Basemap</div>
              <div className="space-y-1">
                {BASEMAPS.map(b => (
                  <label
                    key={b.id}
                    className={`flex items-center gap-2 px-2 py-1.5 rounded-lg cursor-pointer border transition-all ${
                      layers.basemap === b.id
                        ? 'border-mars-orange/50 bg-mars-rust/10 text-white'
                        : 'border-transparent hover:border-mars-border text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <input
                      type="radio"
                      name="basemap"
                      value={b.id}
                      checked={layers.basemap === b.id}
                      onChange={() => setBasemap(b.id)}
                      className="sr-only"
                    />
                    <div className={`w-2.5 h-2.5 rounded-full border-2 shrink-0 transition-colors ${
                      layers.basemap === b.id ? 'border-mars-orange bg-mars-orange' : 'border-slate-600'
                    }`} />
                    <div>
                      <div className="text-[11px] font-mono leading-tight">{b.label}</div>
                      <div className="text-[9px] font-mono text-slate-600 leading-tight">{b.sub}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="border-t border-mars-border/50" />

            {/* ── Overlay layers ── */}
            <div>
              <div className="text-[9px] font-mono uppercase tracking-widest text-slate-500 mb-1">Overlays</div>
              <div className="space-y-0.5">
                <LayerRow
                  dot="#ff6b35" label="Surface Traverse"
                  sublabel="Perseverance Sols 0–1230"
                  checked={layers.showTraverse ?? true}
                  onChange={set('showTraverse')}
                  color="bg-mars-orange"
                />
                <LayerRow
                  dot="#6366f1" label="Elevation / DEM"
                  sublabel="MOLA contours"
                  checked={layers.showElevation ?? false}
                  onChange={set('showElevation')}
                  color="bg-indigo-500"
                />
                <LayerRow
                  dot="#c1440e" label="Terrain & Hazards"
                  sublabel="Slope & sand dunes"
                  checked={layers.showHazards ?? true}
                  onChange={set('showHazards')}
                  color="bg-mars-rust"
                />
                <LayerRow
                  dot="#f59e0b" label="Discoveries"
                  sublabel="Scientific targets"
                  checked={layers.showDiscoveries ?? true}
                  onChange={set('showDiscoveries')}
                  color="bg-amber-500"
                />
                <LayerRow
                  dot="#00d2ff" label="Routes"
                  sublabel="Calculated paths"
                  checked={layers.showRoute ?? true}
                  onChange={set('showRoute')}
                  color="bg-mars-cyan"
                />
                <LayerRow
                  dot="#00ffc8" label="Env. Stations"
                  sublabel="MEDA measurement points"
                  checked={layers.showEnvironment ?? true}
                  onChange={set('showEnvironment')}
                  color="bg-mars-neon"
                />
                <LayerRow
                  dot="#8b5cf6" label="Geological Units"
                  sublabel="USGS SIM 3464 vector"
                  checked={layers.showGeology ?? false}
                  onChange={set('showGeology')}
                  color="bg-violet-500"
                />
              </div>
            </div>

            <div className="border-t border-mars-border/50" />

            {/* ── Opacity note ── */}
            <div className="text-[9px] font-mono text-slate-600 leading-relaxed pb-1">
              Raster overlay opacity controlled via map context menu. Full tile server integration pending.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LayerControlPanel
