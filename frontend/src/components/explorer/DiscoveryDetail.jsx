// DiscoveryDetail – full scientific detail view for a selected discovery
import { IconFlask, IconMap, IconCompass, IconInfo, IconAlert, IconCheck, IconStar } from '../Icons'
import { parseBioScore } from './DiscoveryCard'

function DetailRow({ label, value, accent }) {
  return (
    <div className="flex items-start justify-between gap-3 py-1.5 border-b border-mars-border/50 last:border-0">
      <span className="text-[11px] font-mono text-slate-500 shrink-0">{label}</span>
      <span className={`text-[11px] font-mono text-right font-semibold ${accent || 'text-slate-200'}`}>
        {value ?? '—'}
      </span>
    </div>
  )
}

function SectionTitle({ children }) {
  return (
    <div className="text-[10px] font-mono text-slate-400 uppercase tracking-widest font-semibold mb-2 flex items-center gap-2">
      <div className="flex-1 h-px bg-mars-border" />
      {children}
      <div className="flex-1 h-px bg-mars-border" />
    </div>
  )
}

// Template literal strings avoid JSX apostrophe escaping issues
const WHY_HIGH = `This site shows some of the strongest indicators of past habitability yet found on Mars.
If ancient life ever existed here, it may have left chemical or mineralogical signatures in these rocks.`

const WHY_MED = `Understanding the mineralogy of this site helps scientists reconstruct ancient Martian
climate and water activity — essential context for assessing Mars's past habitability.`

const WHY_LOW = `Geological diversity like this helps build a complete picture of Mars's geological
history. Even sites with lower biosignature potential constrain the geological timeline.`

export function DiscoveryDetail({ discovery, currentMedaReport, onExplore, onViewMission, onClose, onOpenDossier }) {
  if (!discovery) return null

  const name     = discovery.target_name || discovery.name || 'Unknown Target'
  const lat      = (discovery.latitude  ?? discovery.lat)?.toFixed(5)  ?? '—'
  const lon      = (discovery.longitude ?? discovery.lon)?.toFixed(5)  ?? '—'
  const bioScore = parseBioScore(discovery.biosignature_potential)
  const bioLabel = typeof discovery.biosignature_potential === 'string'
    ? discovery.biosignature_potential
    : bioScore >= 0.75 ? 'High'
    : bioScore >= 0.5  ? 'Moderate'
    : bioScore >= 0.25 ? 'Low' : 'Minimal'
  const bioColor = bioScore >= 0.75 ? 'text-emerald-400'
    : bioScore >= 0.5 ? 'text-amber-400' : 'text-mars-orange'

  // Simple explanation derived from fields (not invented)
  const simpleExplanation = discovery.companion_insight
    || discovery.description
    || `${name} is a geological feature in the ${discovery.geological_formation || 'Jezero Crater'} formation, studied as part of the Perseverance science campaign.`

  // Why it matters — from scientific_summary or tier-based context
  const whyItMatters = discovery.scientific_summary
    || (bioScore >= 0.75 ? WHY_HIGH : bioScore >= 0.5 ? WHY_MED : WHY_LOW)

  // Mission context
  const mission = discovery.primary_objective_id
    ? `Perseverance Rover — Objective ${discovery.primary_objective_id}`
    : 'Perseverance Rover, Mars 2020 Mission'

  return (
    <div className="flex flex-col h-full animate-float-up">
      {/* Header */}
      <div className="p-4 border-b border-mars-border bg-gradient-to-b from-mars-panel to-transparent flex-shrink-0">
        <div className="flex items-start justify-between gap-2 mb-1">
          <h2 className="font-mission font-bold text-slate-100 text-base leading-tight">{name}</h2>
          <button
            onClick={onClose}
            className="shrink-0 w-6 h-6 rounded flex items-center justify-center text-slate-400 hover:text-slate-100 hover:bg-mars-border transition"
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] font-mono">
          <span className="flex items-center gap-1 text-mars-orange">
            <IconMap className="w-3 h-3" />
            {lat}°N, {lon}°E
          </span>
          <span className="text-slate-500">·</span>
          <span className="text-mars-cyan">{discovery.elevation_m ?? '—'} m MOLA</span>
          {discovery.sol && (
            <>
              <span className="text-slate-500">·</span>
              <span className="text-slate-400">Sol {discovery.sol}</span>
            </>
          )}
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">

        {/* Simple explanation */}
        <div className="p-3.5 rounded-lg bg-mars-panel/60 border border-mars-cyan/20">
          <div className="flex items-center gap-1.5 mb-2">
            <IconInfo className="w-3.5 h-3.5 text-mars-cyan" />
            <span className="text-[10px] font-mono text-mars-cyan font-semibold uppercase tracking-wider">What is this?</span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-line">{simpleExplanation}</p>
        </div>

        {/* Why it matters */}
        <div className="p-3.5 rounded-lg bg-amber-950/20 border border-amber-800/30">
          <div className="flex items-center gap-1.5 mb-2">
            <IconStar className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-[10px] font-mono text-amber-400 font-semibold uppercase tracking-wider">Why it matters</span>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">{whyItMatters}</p>
        </div>

        {/* Mission attribution */}
        <div>
          <SectionTitle>Mission</SectionTitle>
          <div className="p-3 rounded-lg bg-mars-panel border border-mars-border">
            <div className="text-xs text-slate-200 font-semibold">{mission}</div>
            {discovery.nasa_pds_citation && (
              <div className="text-[10px] font-mono text-slate-500 mt-1 leading-relaxed">
                {discovery.nasa_pds_citation}
              </div>
            )}
          </div>
        </div>

        {/* Key telemetry */}
        <div>
          <SectionTitle>Telemetry</SectionTitle>
          <div className="rounded-lg bg-mars-panel border border-mars-border overflow-hidden">
            <DetailRow label="Formation"              value={discovery.geological_formation} />
            <DetailRow label="Lithology"              value={discovery.lithology} />
            <DetailRow label="Elevation"              value={discovery.elevation_m != null ? `${discovery.elevation_m} m` : null} />
            <DetailRow label="Biosignature Potential" value={bioLabel} accent={bioColor} />
            <DetailRow label="Sol Observed"           value={discovery.sol?.toString()} />
            <DetailRow label="Earth Date"             value={discovery.earth_date} />
          </div>
        </div>

        {/* Mineralogy */}
        {(discovery.mineralogy_detected?.length || discovery.minerals?.length) && (
          <div>
            <SectionTitle>Mineralogy</SectionTitle>
            <div className="flex flex-wrap gap-1.5">
              {(discovery.mineralogy_detected || discovery.minerals || []).map((m, i) => (
                <span key={i} className="px-2 py-1 rounded-full bg-mars-darker border border-mars-border text-mars-cyan text-[11px] font-mono">
                  {m}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Sample status */}
        {discovery.sample_acquired && (
          <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-700/40">
            <div className="flex items-center gap-2 mb-2">
              <IconCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-semibold text-emerald-300">Sample Sealed &amp; Cached</span>
            </div>
            <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5 text-[11px] font-mono">
              {discovery.sample_name && (
                <><span className="text-slate-500">Sample</span><span className="text-emerald-300">{discovery.sample_name}</span></>
              )}
              {discovery.sample_tube_serial && (
                <><span className="text-slate-500">Tube ID</span><span className="text-emerald-300">{discovery.sample_tube_serial}</span></>
              )}
              {discovery.cache_status && (
                <><span className="text-slate-500">Cache</span><span className="text-emerald-300">{discovery.cache_status}</span></>
              )}
            </div>
          </div>
        )}

        {/* EVA warnings from MEDA */}
        {currentMedaReport?.eva_suit_warnings?.length > 0 && (
          <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-700/40">
            <div className="flex items-center gap-1.5 mb-1.5">
              <IconAlert className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[10px] font-mono text-amber-400 font-semibold uppercase tracking-wider">Current EVA Advisory</span>
            </div>
            {currentMedaReport.eva_suit_warnings.map((w, i) => (
              <div key={i} className="text-[11px] text-amber-200/80 font-mono">• {w}</div>
            ))}
          </div>
        )}

      </div>

      {/* Action bar */}
      <div className="p-4 border-t border-mars-border flex-shrink-0 space-y-2">
        <button
          onClick={onExplore}
          className="w-full py-2.5 rounded-lg bg-gradient-to-r from-mars-rust to-mars-orange text-white font-mono text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 shadow-md shadow-mars-rust/20 hover:from-mars-red hover:to-mars-rust transition"
        >
          <IconCompass className="w-4 h-4" />
          Explore This Location
        </button>
        {onOpenDossier && (
          <button
            onClick={() => onOpenDossier(discovery)}
            className="w-full py-2 rounded-lg bg-violet-900/20 border border-violet-700/40 text-violet-400 font-mono text-xs hover:bg-violet-900/40 hover:border-violet-500/60 flex items-center justify-center gap-2 transition"
          >
            <IconFlask className="w-3.5 h-3.5" />
            Full Scientific Dossier
          </button>
        )}
        <button
          onClick={onViewMission}
          className="w-full py-2 rounded-lg bg-mars-panel border border-mars-border text-slate-300 font-mono text-xs hover:border-mars-cyan/50 hover:text-mars-cyan flex items-center justify-center gap-2 transition"
        >
          <IconFlask className="w-3.5 h-3.5" />
          View in Mission Control
        </button>
      </div>
    </div>
  )
}
