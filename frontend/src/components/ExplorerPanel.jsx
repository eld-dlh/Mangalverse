// ExplorerPanel – Explorer Mode sidebar
// VERA (Virtual Exploration & Reconnaissance Assistant) guided experience.
// All discovery data comes from real API/mock via props — nothing invented.

import { useState, useEffect, useMemo } from 'react'
import { VERAAvatar, VERASpeechBubble } from './explorer/VERACompanion'
import { DiscoveryCard }                from './explorer/DiscoveryCard'
import { DiscoveryDetail }              from './explorer/DiscoveryDetail'
import { IconCompass, IconFlask, IconMap, IconRocket } from './Icons'

// ── VERA intro messages (scientifically grounded, friendly) ──────────────────
const VERA_INTROS = [
  "Welcome to Jezero Crater — an ancient lake bed that dried up roughly 3.5 billion years ago. The delta region ahead holds some of the most promising biosignature targets on Mars.",
  "I'm VERA, your Exploration & Reconnaissance Assistant. My role is to help you understand what Perseverance has discovered at each science target. Select any location to begin.",
  "Jezero's delta was once a river mouth where sediment accumulated — exactly the kind of environment where organic molecules can be preserved. Let's see what's here.",
]

// ── VERA commentary by discovery type ────────────────────────────────────────
function getVERADialogue(discovery) {
  if (!discovery) return null
  const name = discovery.target_name || discovery.name || 'this target'

  if (discovery.biosignature_potential === 'High' ||
      (typeof discovery.biosignature_potential === 'number' && discovery.biosignature_potential >= 0.75)) {
    return `${name} is one of the highest-priority targets in the entire mission. The laminated mudstone here formed under water — slowly, over long periods — creating conditions where ancient organic molecules could be trapped and preserved.`
  }
  if (discovery.sample_acquired) {
    return `A sample from ${name} has already been hermetically sealed inside a titanium tube. If a future mission returns it to Earth, lab instruments could detect biosignatures far too subtle for rover instruments to resolve.`
  }
  if (discovery.geological_formation) {
    return `${name} sits within the ${discovery.geological_formation} formation. Understanding how this rock unit formed — whether from volcanic activity, water deposition, or impact — is key to reconstructing Mars's early history.`
  }
  return `${name} is a science target selected because its surface texture, mineralogy, or location makes it geologically significant. Every data point collected here refines our model of ancient Mars.`
}

// ── Empty state when no checkpoints selected ─────────────────────────────────
function EmptyState({ onSwitchToMission }) {
  return (
    <div className="flex flex-col items-center justify-center text-center gap-5 py-10 px-4">
      <div className="w-16 h-16 rounded-full bg-mars-panel border border-mars-border flex items-center justify-center">
        <IconMap className="w-7 h-7 text-slate-600" />
      </div>
      <div>
        <div className="text-slate-300 font-semibold text-sm mb-1">No exploration targets loaded</div>
        <div className="text-slate-500 font-mono text-xs leading-relaxed max-w-[200px] mx-auto">
          Switch to Mission Control and select an objective with checkpoints to begin guided exploration.
        </div>
      </div>
      <button
        onClick={onSwitchToMission}
        className="mt-2 px-4 py-2 rounded-lg bg-mars-panel border border-mars-border text-slate-300 font-mono text-xs hover:border-mars-orange/60 hover:text-mars-orange flex items-center gap-2 transition"
      >
        <IconCompass className="w-3.5 h-3.5" />
        Open Mission Control
      </button>
    </div>
  )
}

// ── Discovery list panel ──────────────────────────────────────────────────────
function DiscoveryList({ discoveries, selectedId, currentId, onSelect }) {
  if (!discoveries.length) return (
    <div className="p-4 text-center text-xs font-mono text-slate-500">
      No discoveries match the current objective.
    </div>
  )
  return (
    <div className="space-y-2">
      {discoveries.map(d => (
        <DiscoveryCard
          key={d.id}
          discovery={d}
          isSelected={selectedId === d.id}
          isCurrent={currentId === d.id}
          onClick={() => onSelect(d)}
        />
      ))}
    </div>
  )
}

// ── Waypoint progress bar ─────────────────────────────────────────────────────
function WaypointProgress({ current, total, onPrev, onNext }) {
  return (
    <div className="p-3 bg-mars-darkest/80 border-b border-mars-border">
      <div className="flex items-center gap-3">
        <button
          disabled={current <= 0}
          onClick={onPrev}
          className="w-8 h-8 rounded flex items-center justify-center bg-mars-panel border border-mars-border text-slate-400 hover:text-slate-100 hover:border-mars-border/80 disabled:opacity-30 disabled:cursor-not-allowed transition"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>

        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Checkpoint</span>
            <span className="text-[10px] font-mono text-mars-orange font-bold">{current + 1} / {total}</span>
          </div>
          <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-mars-rust to-mars-orange h-full rounded-full transition-all duration-500"
              style={{ width: `${((current + 1) / total) * 100}%` }}
            />
          </div>
        </div>

        <button
          disabled={current >= total - 1}
          onClick={onNext}
          className="w-8 h-8 rounded flex items-center justify-center bg-mars-panel border border-mars-border text-slate-400 hover:text-slate-100 hover:border-mars-border/80 disabled:opacity-30 disabled:cursor-not-allowed transition"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
      </div>
    </div>
  )
}

// ── Main ExplorerPanel component ──────────────────────────────────────────────
function ExplorerPanel({
  // Data from App.jsx
  discoveries,              // all discoveries from API
  selectedCheckpointIds,    // which checkpoint IDs are in the route
  currentWaypointIndex,
  currentWaypointDiscovery, // derived: discovery at current waypoint
  currentMedaReport,        // current sol MEDA weather
  isSpeaking,
  speakText,
  // Navigation actions
  onPrev,
  onNext,
  onSwitchToMission,        // new prop: go back to Mission Control
  // Map control
  onFlyToDiscovery,         // new prop: pan map to a discovery
}) {
  const total = selectedCheckpointIds.length

  // Local state: which discovery is selected for detail view
  const [selectedDiscovery, setSelectedDiscovery] = useState(null)
  // Panel sub-view: 'list' | 'detail'
  const [subView, setSubView] = useState('list')
  // Intro message index
  const [introIdx, setIntroIdx] = useState(0)
  // Track if VERA has spoken this waypoint
  const [spokenWaypoint, setSpokenWaypoint] = useState(-1)

  // Nearby discoveries = checkpoint discoveries in order, with full detail from API
  const checkpointDiscoveries = useMemo(() => {
    return selectedCheckpointIds
      .map(id => discoveries.find(d => d.id === id))
      .filter(Boolean)
  }, [selectedCheckpointIds, discoveries])

  // Auto-speak when waypoint changes
  useEffect(() => {
    if (!currentWaypointDiscovery) return
    if (spokenWaypoint === currentWaypointIndex) return
    const dialogue = getVERADialogue(currentWaypointDiscovery)
    if (dialogue) speakText(dialogue)
    setSpokenWaypoint(currentWaypointIndex)
  }, [currentWaypointIndex, currentWaypointDiscovery]) // eslint-disable-line

  // Auto-select current waypoint in list
  useEffect(() => {
    if (currentWaypointDiscovery && subView === 'list') {
      setSelectedDiscovery(currentWaypointDiscovery)
    }
  }, [currentWaypointDiscovery]) // eslint-disable-line

  // Intro cycle (idle message rotation)
  useEffect(() => {
    if (total > 0) return // stop cycling once expedition is active
    const id = setInterval(() => {
      setIntroIdx(i => (i + 1) % VERA_INTROS.length)
    }, 6000)
    return () => clearInterval(id)
  }, [total])

  // Handle "Explore this location" — fly map + go to detail
  const handleExplore = (disc) => {
    onFlyToDiscovery?.(disc)
    setSelectedDiscovery(disc)
    setSubView('detail')
  }

  // Handle selecting from list
  const handleSelectFromList = (disc) => {
    setSelectedDiscovery(disc)
    setSubView('detail')
  }

  // VERA text for speech bubble
  const veraText = total === 0
    ? VERA_INTROS[introIdx]
    : selectedDiscovery
    ? getVERADialogue(selectedDiscovery)
    : getVERADialogue(currentWaypointDiscovery)

  return (
    <aside className="w-80 xl:w-96 border-r border-mars-border bg-mars-darker flex flex-col z-10 shrink-0">

      {/* ── VERA Header ── */}
      <div className="p-4 border-b border-mars-border bg-gradient-to-b from-mars-panel to-mars-darker flex-shrink-0">
        <div className="flex items-start gap-3 mb-3">
          <VERAAvatar isSpeaking={isSpeaking} size="md" />
          <div className="min-w-0 flex-1">
            <div className="font-mission font-bold text-sm text-slate-100 leading-tight">VERA</div>
            <div className="text-[10px] font-mono text-mars-cyan mt-0.5">
              Virtual Exploration &amp; Reconnaissance Assistant
            </div>
            <div className="flex items-center gap-2 mt-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${total > 0 ? 'bg-mars-neon animate-pulse' : 'bg-slate-600'}`} />
              <span className="text-[10px] font-mono text-slate-500">
                {total > 0 ? `${total} target${total !== 1 ? 's' : ''} loaded · Jezero Crater` : 'Awaiting expedition parameters'}
              </span>
            </div>
          </div>
        </div>

        {/* Speech bubble */}
        <VERASpeechBubble
          text={veraText}
          isSpeaking={isSpeaking}
          onReplay={() => veraText && speakText(veraText)}
        />
      </div>

      {/* ── Waypoint navigator (when active) ── */}
      {total > 0 && (
        <WaypointProgress
          current={currentWaypointIndex}
          total={total}
          onPrev={onPrev}
          onNext={onNext}
        />
      )}

      {/* ── Sub-view toggle (List / Detail) ── */}
      {total > 0 && (
        <div className="flex border-b border-mars-border text-xs font-mono flex-shrink-0">
          <button
            onClick={() => setSubView('list')}
            className={`flex-1 py-2 flex items-center justify-center gap-1.5 border-b-2 transition ${
              subView === 'list'
                ? 'border-mars-orange text-mars-orange bg-mars-darker font-semibold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <IconMap className="w-3.5 h-3.5" />
            Exploration Targets
          </button>
          <button
            onClick={() => setSubView('detail')}
            disabled={!selectedDiscovery}
            className={`flex-1 py-2 flex items-center justify-center gap-1.5 border-b-2 transition disabled:opacity-30 disabled:cursor-not-allowed ${
              subView === 'detail'
                ? 'border-mars-cyan text-mars-cyan bg-mars-darker font-semibold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <IconFlask className="w-3.5 h-3.5" />
            Site Details
          </button>
        </div>
      )}

      {/* ── Main content area ── */}
      <div className="flex-1 overflow-hidden flex flex-col">

        {/* Empty state */}
        {total === 0 && (
          <EmptyState onSwitchToMission={onSwitchToMission} />
        )}

        {/* Discovery list */}
        {total > 0 && subView === 'list' && (
          <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
            <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2 px-1">
              Nearby Science Targets — Jezero Crater
            </div>
            <DiscoveryList
              discoveries={checkpointDiscoveries}
              selectedId={selectedDiscovery?.id}
              currentId={currentWaypointDiscovery?.id}
              onSelect={handleSelectFromList}
            />
          </div>
        )}

        {/* Discovery detail */}
        {total > 0 && subView === 'detail' && (
          <div className="flex-1 overflow-hidden flex flex-col">
            {selectedDiscovery ? (
              <DiscoveryDetail
                discovery={selectedDiscovery}
                currentMedaReport={currentMedaReport}
                onExplore={() => handleExplore(selectedDiscovery)}
                onViewMission={onSwitchToMission}
                onClose={() => setSubView('list')}
              />
            ) : (
              <div className="flex flex-col items-center justify-center gap-3 py-12 text-center px-4">
                <IconFlask className="w-8 h-8 text-slate-700" />
                <div className="text-slate-500 font-mono text-xs">
                  Select a target from the exploration list to view details.
                </div>
                <button
                  onClick={() => setSubView('list')}
                  className="text-mars-cyan text-xs font-mono underline hover:text-mars-neon transition"
                >
                  View targets →
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Footer action bar ── */}
      <div className="p-3 border-t border-mars-border flex-shrink-0 space-y-2">
        {/* Navigate to next checkpoint */}
        {total > 0 && currentWaypointIndex < total - 1 && (
          <button
            onClick={onNext}
            className="w-full py-2 rounded-lg bg-mars-panel border border-mars-orange/40 text-mars-orange font-mono text-xs hover:bg-mars-orange/10 hover:border-mars-orange flex items-center justify-center gap-2 transition"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <polyline points="9 18 15 12 9 6" />
            </svg>
            Next Checkpoint
          </button>
        )}
        {/* Switch to Mission Control */}
        <button
          onClick={onSwitchToMission}
          className="w-full py-2 rounded-lg bg-mars-darker border border-mars-border text-slate-400 font-mono text-xs hover:border-slate-500 hover:text-slate-200 flex items-center justify-center gap-2 transition"
        >
          <IconRocket className="w-3.5 h-3.5" />
          Switch to Mission Control
        </button>
      </div>
    </aside>
  )
}

export default ExplorerPanel
