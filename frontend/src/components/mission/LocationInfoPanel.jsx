// LocationInfoPanel – right-side panel showing selected point/discovery details
// Appears when user probes terrain, selects a discovery, or sets start/dest

import { IconX, IconFlask, IconThermometer, IconGauge, IconShield, IconAlert } from '../Icons'

// ── Section header ────────────────────────────────────────────────────────────
function SectionHead({ label }) {
  return (
    <div className="text-[9px] font-mono uppercase tracking-widest text-slate-500 mt-3 mb-1 first:mt-0">
      {label}
    </div>
  )
}

// ── KV row ───────────────────────────────────────────────────────────────────
function KV({ label, value, valueClass = 'text-slate-200' }) {
  return (
    <div className="flex items-start justify-between gap-2 py-0.5">
      <span className="text-[10px] font-mono text-slate-500 shrink-0">{label}</span>
      <span className={`text-[10px] font-mono text-right ${valueClass}`}>{value}</span>
    </div>
  )
}

// ── Hazard badge ─────────────────────────────────────────────────────────────
function HazardBadge({ level }) {
  const map = {
    SAFE:     { bg: 'bg-emerald-900/40 border-emerald-700/60', text: 'text-emerald-400' },
    CAUTION:  { bg: 'bg-amber-900/40 border-amber-700/60',    text: 'text-amber-400' },
    CRITICAL: { bg: 'bg-red-900/40 border-red-700/60',        text: 'text-red-400' },
  }
  const s = map[level] ?? map.SAFE
  return (
    <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${s.bg} ${s.text}`}>
      {level}
    </span>
  )
}

// ── Discovery type badge ──────────────────────────────────────────────────────
function TypeBadge({ type }) {
  const map = {
    biosignature: { label: 'BIOSIGNATURE', bg: 'bg-amber-900/40 border-amber-700/50', text: 'text-amber-400' },
    sample:       { label: 'SAMPLE CACHED', bg: 'bg-emerald-900/40 border-emerald-700/50', text: 'text-emerald-400' },
    geological:   { label: 'GEOLOGICAL',   bg: 'bg-violet-900/40 border-violet-700/50', text: 'text-violet-400' },
    hazard:       { label: 'HAZARD ZONE',  bg: 'bg-red-900/40 border-red-700/50',       text: 'text-red-400' },
    waypoint:     { label: 'WAYPOINT',     bg: 'bg-mars-cyan/10 border-mars-cyan/40',    text: 'text-mars-cyan' },
  }
  const s = map[type] ?? map.geological
  return (
    <span className={`text-[9px] font-mono font-semibold px-2 py-0.5 rounded border ${s.bg} ${s.text}`}>
      {s.label}
    </span>
  )
}

// ── Terrain probe view ────────────────────────────────────────────────────────
function TerrainView({ point }) {
  return (
    <>
      <SectionHead label="Coordinates" />
      <KV label="Latitude"  value={`${point.latitude ?? point.lat}°N`} valueClass="text-mars-cyan" />
      <KV label="Longitude" value={`${point.longitude ?? point.lng}°E`} valueClass="text-mars-cyan" />

      <SectionHead label="Terrain" />
      {point.error ? (
        <div className="mt-1 flex items-start gap-1.5 p-1.5 rounded bg-red-950/30 border border-red-800/40 text-[10px] text-red-400 font-mono">
          <IconAlert className="w-3 h-3 shrink-0 mt-0.5" />
          <span>{point.error}</span>
        </div>
      ) : (
        <>
          <KV label="Elevation" value={`${point.elevation_meters ?? point.elevation_m ?? '—'} m`} valueClass="text-mars-gold" />
          <div className="flex items-center justify-between gap-2 py-0.5">
            <span className="text-[10px] font-mono text-slate-500">Slope</span>
            <div className="flex items-center gap-2">
              <span className={`text-[10px] font-mono ${
                (point.slope_degrees ?? 0) > 15 ? 'text-red-400' :
                (point.slope_degrees ?? 0) > 10 ? 'text-amber-400' : 'text-emerald-400'
              }`}>
                {point.slope_degrees ?? '—'}°
              </span>
              {point.terrain_hazard && <HazardBadge level={point.terrain_hazard} />}
            </div>
          </div>
        </>
      )}

      {point.data_source && point.data_source !== 'error' && (
        <>
          <SectionHead label="Provenance" />
          <KV label="Data source" value={point.data_source} />
        </>
      )}
    </>
  )
}

// ── Discovery view ────────────────────────────────────────────────────────────
function DiscoveryView({ disc }) {
  const bsScore = disc.biosignature_potential
  const scoreBar = typeof bsScore === 'number'
    ? Math.min(100, Math.round(bsScore * 100))
    : null

  return (
    <>
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <div className="text-sm font-mission font-bold text-slate-100 leading-tight">{disc.name ?? disc.target_name}</div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">Sol {disc.sol}</div>
        </div>
        <TypeBadge type={disc.type ?? (disc.sample_acquired ? 'sample' : 'geological')} />
      </div>

      {disc.description && (
        <p className="text-[11px] text-slate-400 leading-relaxed mb-2">{disc.description ?? disc.scientific_summary}</p>
      )}

      <SectionHead label="Location" />
      <KV label="Latitude"  value={`${(disc.lat ?? disc.latitude)}°N`} />
      <KV label="Longitude" value={`${(disc.lon ?? disc.longitude)}°E`} />
      <KV label="Elevation" value={`${disc.elevation_m} m`} valueClass="text-mars-gold" />

      {disc.geological_formation && (
        <>
          <SectionHead label="Geology" />
          <KV label="Formation" value={disc.geological_formation} />
          {disc.lithology && <KV label="Lithology" value={disc.lithology} />}
        </>
      )}

      {(disc.minerals?.length > 0 || disc.mineralogy_detected?.length > 0) && (
        <>
          <SectionHead label="Mineralogy" />
          <div className="flex flex-wrap gap-1">
            {(disc.minerals ?? disc.mineralogy_detected ?? []).map((m, i) => (
              <span key={i} className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-mars-darker border border-mars-border text-mars-cyan">
                {m}
              </span>
            ))}
          </div>
        </>
      )}

      {scoreBar !== null && (
        <>
          <SectionHead label="Biosignature Potential" />
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  scoreBar > 70 ? 'bg-amber-500' : scoreBar > 40 ? 'bg-mars-cyan' : 'bg-slate-500'
                }`}
                style={{ width: `${scoreBar}%` }}
              />
            </div>
            <span className={`text-[10px] font-mono font-bold ${
              scoreBar > 70 ? 'text-amber-400' : scoreBar > 40 ? 'text-mars-cyan' : 'text-slate-400'
            }`}>{scoreBar}%</span>
          </div>
        </>
      )}

      {disc.sample_acquired && (
        <div className="mt-3 p-2 rounded bg-emerald-950/40 border border-emerald-800/50 text-[10px] font-mono text-emerald-300 space-y-0.5">
          <div className="font-semibold">🧪 Core Sample Cached</div>
          {disc.sample_name && <div>Name: {disc.sample_name}</div>}
          {disc.sample_tube_serial && <div>Tube: {disc.sample_tube_serial}</div>}
        </div>
      )}

      {disc.nasa_pds_citation && (
        <>
          <SectionHead label="Citation" />
          <div className="text-[9px] font-mono text-slate-600 leading-relaxed">{disc.nasa_pds_citation}</div>
        </>
      )}
    </>
  )
}

// ── Waypoint (start/dest) view ────────────────────────────────────────────────
function WaypointView({ point, role }) {
  const roleLabel = role === 'start' ? 'START POINT' : role === 'dest' ? 'DESTINATION' : 'CHECKPOINT'
  const roleColor = role === 'start' ? 'text-emerald-400' : role === 'dest' ? 'text-mars-orange' : 'text-mars-cyan'
  return (
    <>
      <div className={`text-[10px] font-mono font-semibold uppercase tracking-widest mb-2 ${roleColor}`}>{roleLabel}</div>
      <SectionHead label="Coordinates" />
      <KV label="Latitude"  value={`${(point.lat ?? point.latitude ?? 0).toFixed(5)}°N`} valueClass="text-mars-cyan" />
      <KV label="Longitude" value={`${(point.lng ?? point.longitude ?? 0).toFixed(5)}°E`} valueClass="text-mars-cyan" />
      {point.elevation_meters && (
        <KV label="Elevation" value={`${point.elevation_meters} m`} valueClass="text-mars-gold" />
      )}
      <p className="mt-3 text-[10px] font-mono text-slate-500 leading-relaxed">
        This point has been set as the {roleLabel.toLowerCase()} for route planning.
        Use the route panel to calculate paths.
      </p>
    </>
  )
}

// ── Main exported component ───────────────────────────────────────────────────
function LocationInfoPanel({ selection, onClose, onOpenDossier }) {
  if (!selection) return null

  const { type, data } = selection  // type: 'probe' | 'discovery' | 'start' | 'dest' | 'checkpoint'

  const title = {
    probe:      'TERRAIN ANALYSIS',
    discovery:  'SCIENTIFIC TARGET',
    start:      'START LOCATION',
    dest:       'DESTINATION',
    checkpoint: 'CHECKPOINT',
  }[type] ?? 'LOCATION'

  const accent = {
    probe:      'border-mars-neon/40',
    discovery:  'border-amber-500/30',
    start:      'border-emerald-500/30',
    dest:       'border-mars-orange/30',
    checkpoint: 'border-mars-cyan/30',
  }[type] ?? 'border-mars-border'

  return (
    <aside className={`w-72 xl:w-80 border-l ${accent} bg-mars-darker flex flex-col shrink-0 z-10`}>
      {/* Panel header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-mars-border bg-mars-panel/50 shrink-0">
        <div className="text-[10px] font-mono font-semibold uppercase tracking-widest text-slate-400">
          {title}
        </div>
        <button
          onClick={onClose}
          className="text-slate-500 hover:text-white transition-colors p-0.5"
          title="Close panel"
        >
          <IconX className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-3">
        {type === 'probe'      && <TerrainView    point={data} />}
        {type === 'discovery'  && <DiscoveryView  disc={data} />}
        {(type === 'start' || type === 'dest' || type === 'checkpoint') && (
          <WaypointView point={data} role={type} />
        )}
      </div>

      {/* Footer: quick actions */}
      {type === 'discovery' && (
        <div className="px-4 pb-4 shrink-0 space-y-1.5 border-t border-mars-border pt-3">
          <div className="text-[9px] font-mono uppercase tracking-widest text-slate-600 mb-1.5">Quick Actions</div>
          <div className="flex gap-1.5">
            <button className="flex-1 py-1.5 rounded bg-emerald-900/30 border border-emerald-700/40 text-[10px] font-mono text-emerald-400 hover:bg-emerald-900/50 transition-colors">
              Set as Start
            </button>
            <button className="flex-1 py-1.5 rounded bg-mars-rust/20 border border-mars-orange/40 text-[10px] font-mono text-mars-orange hover:bg-mars-rust/30 transition-colors">
              Set as Dest.
            </button>
            <button className="flex-1 py-1.5 rounded bg-mars-cyan/10 border border-mars-cyan/40 text-[10px] font-mono text-mars-cyan hover:bg-mars-cyan/20 transition-colors">
              Checkpoint
            </button>
          </div>
          {onOpenDossier && (
            <button
              onClick={() => onOpenDossier(data)}
              className="w-full py-1.5 rounded bg-violet-900/30 border border-violet-700/40 text-[10px] font-mono text-violet-400 hover:bg-violet-900/50 transition-colors"
            >
              Full Scientific Dossier
            </button>
          )}
        </div>
      )}
    </aside>
  )
}

export default LocationInfoPanel
