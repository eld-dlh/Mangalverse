// DiscoveryCard – selectable exploration point for Explorer Mode
import { IconFlask, IconStar, IconCheck } from '../Icons'

// Map biosignature_potential string → numeric score for display
function parseBioScore(val) {
  if (typeof val === 'number') return val
  const map = {
    'very high': 0.9, 'high': 0.75, 'moderate': 0.5,
    'low': 0.25, 'very low': 0.1, 'none detected': 0.0,
  }
  return map[String(val).toLowerCase()] ?? 0.5
}

function BioBar({ score }) {
  const pct = Math.round(score * 100)
  const color =
    score >= 0.75 ? 'bg-emerald-400' :
    score >= 0.5  ? 'bg-amber-400'   :
    score >= 0.25 ? 'bg-mars-orange' : 'bg-slate-600'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div className={`${color} h-full rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`text-[10px] font-mono font-bold ${
        score >= 0.75 ? 'text-emerald-400' : score >= 0.5 ? 'text-amber-400' : 'text-mars-orange'
      }`}>{pct}%</span>
    </div>
  )
}

export function DiscoveryCard({ discovery, isSelected, isCurrent, onClick }) {
  const bioScore = parseBioScore(discovery.biosignature_potential)
  const name = discovery.target_name || discovery.name || 'Unknown Target'
  const sol  = discovery.sol ?? '—'

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-3 rounded-lg border transition-all duration-200 group ${
        isCurrent
          ? 'bg-mars-cyan/10 border-mars-cyan/60 shadow-sm shadow-mars-cyan/20'
          : isSelected
          ? 'bg-mars-panel border-mars-orange/50'
          : 'bg-mars-darker hover:bg-mars-panel/60 border-mars-border'
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          {/* Type icon */}
          <div className={`shrink-0 w-7 h-7 rounded flex items-center justify-center ${
            discovery.sample_acquired ? 'bg-emerald-900/60 border border-emerald-700/50' : 'bg-mars-panel border border-mars-border'
          }`}>
            {discovery.sample_acquired
              ? <IconFlask className="w-3.5 h-3.5 text-emerald-400" />
              : <IconStar className="w-3.5 h-3.5 text-mars-orange" />
            }
          </div>
          <div className="min-w-0">
            <div className="text-xs font-semibold text-slate-100 truncate leading-tight">{name}</div>
            <div className="text-[10px] font-mono text-slate-500 mt-0.5">Sol {sol}</div>
          </div>
        </div>
        {isCurrent && (
          <span className="shrink-0 px-1.5 py-0.5 rounded bg-mars-cyan/20 text-mars-cyan text-[9px] font-mono font-bold border border-mars-cyan/30">
            HERE
          </span>
        )}
        {isSelected && !isCurrent && (
          <IconCheck className="shrink-0 w-3.5 h-3.5 text-mars-orange" />
        )}
      </div>

      {/* Formation */}
      <div className="text-[10px] font-mono text-slate-500 mb-2 truncate">
        {discovery.geological_formation || discovery.type || 'Formation data pending'}
      </div>

      {/* Bio bar */}
      <div>
        <div className="text-[10px] font-mono text-slate-500 mb-1">Biosignature Potential</div>
        <BioBar score={bioScore} />
      </div>
    </button>
  )
}

export { parseBioScore }
