// RouteComparisonPanel – 3-way route comparison (shortest / safest / balanced)
// Right-side panel; shown after route calculation completes

import { useState } from 'react'
import { IconAlert, IconCheck, IconX } from '../Icons'

// ── Icons ─────────────────────────────────────────────────────────────────────
const IconDistance = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.5 12.5"/>
    <path d="M2 2l20 20"/>
  </svg>
)

const IconClock = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
    <circle cx="12" cy="12" r="10"/>
    <polyline points="12 6 12 12 16 14"/>
  </svg>
)

const IconSlope = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
    <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
    <polyline points="16 7 22 7 22 13"/>
  </svg>
)

const IconElevation = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
    <polygon points="12 2 22 20 2 20"/>
  </svg>
)

// ── Route variant definitions ─────────────────────────────────────────────────
const VARIANTS = [
  {
    key: 'shortest',
    label: 'SHORTEST',
    icon: '⚡',
    description: 'Minimum distance path',
    accentBg:   'bg-mars-orange/10',
    accentBorder:'border-mars-orange/40',
    accentText:  'text-mars-orange',
    barColor:    'bg-mars-orange',
  },
  {
    key: 'safest',
    label: 'SAFEST',
    icon: '🛡',
    description: 'Minimum slope & hazards',
    accentBg:   'bg-emerald-900/15',
    accentBorder:'border-emerald-700/40',
    accentText:  'text-emerald-400',
    barColor:    'bg-emerald-500',
  },
  {
    key: 'balanced',
    label: 'BALANCED',
    icon: '⚖',
    description: 'Optimal distance vs. safety',
    accentBg:   'bg-mars-cyan/10',
    accentBorder:'border-mars-cyan/40',
    accentText:  'text-mars-cyan',
    barColor:    'bg-mars-cyan',
  },
]

// ── Metric row ────────────────────────────────────────────────────────────────
function MetricRow({ icon, label, value, valueClass = 'text-slate-200' }) {
  return (
    <div className="flex items-center justify-between gap-2">
      <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-500">
        {icon}
        <span>{label}</span>
      </div>
      <span className={`text-[11px] font-mono font-semibold ${valueClass}`}>{value}</span>
    </div>
  )
}

// ── Single route card ─────────────────────────────────────────────────────────
function RouteCard({ variant, data, isActive, isSelected, onClick, onSelect }) {
  const v = variant

  // Safety score: 0-100 based on max slope (lower = safer)
  const safetyScore = data ? Math.max(0, Math.round(100 - (data.max_slope_deg ?? 0) * 4.5)) : null
  const efficiencyScore = data
    ? Math.max(0, Math.round(100 - ((data.distance_km ?? 10) - 4) * 8))
    : null

  return (
    <div
      className={`rounded-xl border p-3 cursor-pointer transition-all duration-200 ${
        isActive
          ? `${v.accentBg} ${v.accentBorder} shadow-lg`
          : 'border-mars-border hover:border-mars-border/80 hover:bg-mars-panel/40'
      }`}
      onClick={onClick}
    >
      {/* Card header */}
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-2">
          <span className="text-sm">{v.icon}</span>
          <div>
            <div className={`text-[11px] font-mono font-bold tracking-wider ${isActive ? v.accentText : 'text-slate-300'}`}>
              {v.label}
            </div>
            <div className="text-[9px] font-mono text-slate-600">{v.description}</div>
          </div>
        </div>

        {/* Select button */}
        <button
          onClick={e => { e.stopPropagation(); onSelect() }}
          className={`text-[9px] font-mono px-2 py-1 rounded border transition-all ${
            isSelected
              ? `${v.accentBg} ${v.accentBorder} ${v.accentText} font-semibold`
              : 'border-mars-border text-slate-500 hover:border-mars-border/80 hover:text-slate-300'
          }`}
        >
          {isSelected ? '✓ ACTIVE' : 'USE'}
        </button>
      </div>

      {/* Metrics (only shown when data present) */}
      {data ? (
        <div className="space-y-1.5">
          <MetricRow icon={<IconDistance />} label="Distance"
            value={`${data.distance_km?.toFixed(1)} km`}
            valueClass={isActive ? v.accentText : 'text-slate-200'}
          />
          <MetricRow icon={<IconClock />} label="Est. Duration"
            value={`${data.duration_hours?.toFixed(1)} hrs`}
          />
          <MetricRow icon={<IconSlope />} label="Max / Avg Slope"
            value={`${data.max_slope_deg?.toFixed(1)}° / ${data.avg_slope_deg?.toFixed(1)}°`}
            valueClass={
              (data.max_slope_deg ?? 0) > 15 ? 'text-red-400' :
              (data.max_slope_deg ?? 0) > 10 ? 'text-amber-400' : 'text-emerald-400'
            }
          />
          <MetricRow icon={<IconElevation />} label="Elevation Gain"
            value={`+${data.elevation_gain_m} m`}
          />

          {/* Score bars */}
          <div className="pt-1.5 border-t border-mars-border/50 space-y-1.5">
            {[
              { label: 'Safety',     val: safetyScore },
              { label: 'Efficiency', val: efficiencyScore },
            ].map(s => (
              <div key={s.label} className="flex items-center gap-2">
                <span className="text-[9px] font-mono text-slate-600 w-16">{s.label}</span>
                <div className="flex-1 bg-slate-800 h-1 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${v.barColor} transition-all duration-500`}
                    style={{ width: `${s.val}%` }}
                  />
                </div>
                <span className="text-[9px] font-mono text-slate-500 w-7 text-right">{s.val}%</span>
              </div>
            ))}
          </div>

          {/* Warnings */}
          {data.warnings?.length > 0 && (
            <div className="pt-1.5 border-t border-mars-border/50 space-y-1">
              {data.warnings.map((w, i) => (
                <div key={i} className="flex items-start gap-1 text-[9px] font-mono text-amber-400">
                  <IconAlert className="w-3 h-3 shrink-0 mt-0.5 text-amber-400" />
                  <span>{w}</span>
                </div>
              ))}
            </div>
          )}

          {data.warnings?.length === 0 && (
            <div className="flex items-center gap-1 text-[9px] font-mono text-emerald-400 pt-1 border-t border-mars-border/50">
              <IconCheck className="w-3 h-3" />
              No terrain warnings
            </div>
          )}
        </div>
      ) : (
        <div className="text-[10px] font-mono text-slate-600 italic">
          Awaiting calculation…
        </div>
      )}
    </div>
  )
}

// ── Main exported component ───────────────────────────────────────────────────
function RouteComparisonPanel({ routeComparison, isCalculating, selectedVariant, onSelectVariant, onClose, startPoint, destPoint }) {
  const [expanded, setExpanded] = useState('balanced')

  const hasPoints = startPoint && destPoint
  const hasData   = !!routeComparison

  return (
    <aside className="w-72 xl:w-80 border-l border-mars-cyan/30 bg-mars-darker flex flex-col shrink-0 z-10">

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-mars-border bg-mars-panel/50 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-mars-cyan animate-pulse" />
          <span className="text-[10px] font-mono font-semibold uppercase tracking-widest text-slate-300">
            Route Comparison
          </span>
        </div>
        <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors p-0.5" title="Close">
          <IconX className="w-4 h-4" />
        </button>
      </div>

      {/* Route points status */}
      <div className="px-4 py-2.5 border-b border-mars-border shrink-0">
        <div className="grid grid-cols-2 gap-1.5">
          <div className={`flex items-center gap-1.5 p-1.5 rounded border text-[10px] font-mono ${
            startPoint
              ? 'border-emerald-700/40 bg-emerald-900/15 text-emerald-400'
              : 'border-mars-border text-slate-600'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${startPoint ? 'bg-emerald-400' : 'bg-slate-600'}`} />
            {startPoint ? 'Start Set' : 'No Start'}
          </div>
          <div className={`flex items-center gap-1.5 p-1.5 rounded border text-[10px] font-mono ${
            destPoint
              ? 'border-mars-orange/40 bg-mars-rust/10 text-mars-orange'
              : 'border-mars-border text-slate-600'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${destPoint ? 'bg-mars-orange' : 'bg-slate-600'}`} />
            {destPoint ? 'Dest. Set' : 'No Dest.'}
          </div>
        </div>

        {!hasPoints && (
          <p className="mt-1.5 text-[9px] font-mono text-slate-600 leading-relaxed">
            Use the toolbar tools to set a start point and destination on the map.
          </p>
        )}
      </div>

      {/* Loading state */}
      {isCalculating && (
        <div className="flex items-center justify-center gap-3 py-8 px-4">
          <div className="w-5 h-5 border-2 border-mars-cyan border-t-transparent rounded-full animate-spin" />
          <div className="text-[11px] font-mono text-mars-cyan">Computing routes…</div>
        </div>
      )}

      {/* Route cards */}
      {!isCalculating && (
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2.5">
          {!hasData && (
            <div className="text-center py-8">
              <div className="text-3xl mb-3">🗺️</div>
              <div className="text-[11px] font-mono text-slate-500 leading-relaxed px-4">
                Set a start point and destination on the map, then calculate routes to compare options.
              </div>
            </div>
          )}

          {VARIANTS.map(variant => (
            <RouteCard
              key={variant.key}
              variant={variant}
              data={routeComparison?.[variant.key]}
              isActive={expanded === variant.key}
              isSelected={selectedVariant === variant.key}
              onClick={() => setExpanded(expanded === variant.key ? null : variant.key)}
              onSelect={() => onSelectVariant(variant.key)}
            />
          ))}
        </div>
      )}

      {/* Footer note */}
      <div className="px-4 pb-3 pt-2 border-t border-mars-border shrink-0">
        <div className="text-[9px] font-mono text-slate-600 leading-relaxed">
          Pathfinding: A* on USGS CTX DEM (20m) + HiRISE DTM (1m). Speed: 0.12 km/h autonomous.
        </div>
      </div>
    </aside>
  )
}

export default RouteComparisonPanel
