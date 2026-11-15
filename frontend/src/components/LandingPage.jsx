// Landing page – two mode-selection cards, project intro
import StarField from './StarField'
import { IconRocket, IconBot, IconChevronRight, IconStar, IconMap, IconFlask } from './Icons'

const FEATURES_MC = [
  { icon: <IconMap className="w-4 h-4" />, text: 'Interactive Leaflet GIS Map' },
  { icon: <IconFlask className="w-4 h-4" />, text: 'A* Terrain-Aware Pathfinding' },
  { icon: <IconStar className="w-4 h-4" />, text: 'NASA MEDA Environmental Telemetry' },
]

const FEATURES_EX = [
  { icon: <IconBot className="w-4 h-4" />, text: 'ARES Virtual Companion (voice)' },
  { icon: <IconStar className="w-4 h-4" />, text: 'Step-by-step waypoint narration' },
  { icon: <IconFlask className="w-4 h-4" />, text: 'Deep scientific dossiers' },
]

function ModeCard({ title, subtitle, description, Icon, features, accent, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`
        group relative flex flex-col text-left rounded-2xl border p-7 w-full max-w-sm
        bg-mars-darker/80 backdrop-blur-sm
        transition-all duration-300
        hover:scale-[1.03] hover:shadow-2xl
        ${accent === 'rust'
          ? 'border-mars-rust/40 hover:border-mars-orange hover:shadow-mars-rust/20'
          : 'border-mars-cyan/30  hover:border-mars-cyan  hover:shadow-mars-cyan/20'}
      `}
    >
      {/* Glow blob */}
      <div className={`
        pointer-events-none absolute -top-6 -right-6 w-32 h-32 rounded-full blur-3xl opacity-0
        group-hover:opacity-25 transition-opacity duration-500
        ${accent === 'rust' ? 'bg-mars-orange' : 'bg-mars-cyan'}
      `} />

      {/* Icon badge */}
      <div className={`
        mb-4 w-12 h-12 rounded-xl flex items-center justify-center shadow-lg border
        ${accent === 'rust'
          ? 'bg-gradient-to-br from-mars-rust to-mars-red border-mars-orange/40 text-white shadow-mars-rust/30'
          : 'bg-gradient-to-br from-teal-800 to-cyan-700 border-mars-cyan/40 text-mars-neon shadow-mars-cyan/30'}
      `}>
        <Icon className="w-6 h-6" />
      </div>

      <div className={`text-[11px] font-mono uppercase tracking-widest mb-1 ${accent === 'rust' ? 'text-mars-orange' : 'text-mars-cyan'}`}>
        {subtitle}
      </div>
      <h2 className="text-xl font-mission font-bold text-slate-100 mb-2">{title}</h2>
      <p className="text-sm text-slate-400 leading-relaxed mb-5">{description}</p>

      <ul className="space-y-2 mb-6">
        {features.map((f, i) => (
          <li key={i} className="flex items-center gap-2 text-xs text-slate-300">
            <span className={accent === 'rust' ? 'text-mars-orange' : 'text-mars-cyan'}>{f.icon}</span>
            {f.text}
          </li>
        ))}
      </ul>

      <div className={`
        mt-auto flex items-center gap-2 text-sm font-mono font-semibold
        ${accent === 'rust' ? 'text-mars-orange' : 'text-mars-cyan'}
        group-hover:gap-3 transition-all duration-200
      `}>
        Launch {title}
        <IconChevronRight className="w-4 h-4" />
      </div>
    </button>
  )
}

function LandingPage({ onSelectMode }) {
  return (
    <div className="relative min-h-screen bg-mars-darkest flex flex-col overflow-hidden">
      <StarField />

      {/* Top bar */}
      <header className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-mars-border/40">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-mars-rust to-mars-red flex items-center justify-center shadow-lg shadow-mars-red/20 border border-mars-orange/40">
            <span className="text-white font-mission font-bold text-xs">ME</span>
          </div>
          <span className="font-mission font-bold text-sm tracking-wider text-slate-200">MARS EXPLORER</span>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono text-slate-500">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          NASA Space Apps Challenge
        </div>
      </header>

      {/* Hero */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 py-16 text-center">

        {/* Mars planet graphic */}
        <div className="mb-8 relative">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-mars-rust via-mars-red to-orange-900 shadow-2xl shadow-mars-rust/40 border border-mars-orange/30 relative overflow-hidden mx-auto">
            <div className="absolute w-10 h-10 rounded-full bg-mars-darker/60 blur-sm top-4 left-5" />
            <div className="absolute w-7 h-7 rounded-full bg-mars-darker/40 blur-sm bottom-5 right-4" />
          </div>
          {/* Orbit ring */}
          <div className="absolute inset-0 rounded-full border border-mars-cyan/20 scale-125 m-auto w-24 h-24" style={{ top: 0 }} />
        </div>

        <div className="animate-float-up">
          <div className="flex items-center justify-center gap-2 mb-3">
            <span className="text-[11px] font-mono uppercase tracking-widest text-mars-cyan px-2.5 py-1 rounded border border-mars-cyan/30 bg-mars-cyan/10">
              Jezero Crater · 18.44°N · 77.45°E
            </span>
          </div>

          <h1 className="font-mission font-bold text-5xl sm:text-6xl text-slate-100 tracking-wide mb-4">
            MARS <span className="text-mars-orange">EXPLORER</span>
          </h1>

          <p className="max-w-xl mx-auto text-slate-400 text-base leading-relaxed mb-2">
            Objective-driven Martian surface exploration platform powered by verified NASA mission data —
            Perseverance telemetry, MEDA atmospheric readings, and USGS orbital terrain models.
          </p>
          <p className="text-xs font-mono text-slate-500 mb-12">
            Mars 2020 Mission · Perseverance Rover · Sols 0–1230
          </p>

          {/* Mode cards */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-stretch">
            <ModeCard
              title="Mission Control"
              subtitle="Tactical GIS Command Center"
              description="Professional scientific interface with interactive Mars cartography, A* terrain-aware route planning, NASA MEDA telemetry, and objective-driven checkpoint selection."
              Icon={IconRocket}
              features={FEATURES_MC}
              accent="rust"
              onClick={() => onSelectMode('MISSION_CONTROL')}
            />
            <ModeCard
              title="Explorer Mode"
              subtitle="Guided Exploration Experience"
              description="Accessible narrative interface guided by ARES, your virtual companion. Voice narration, step-by-step waypoint exploration, and deep scientific dossiers."
              Icon={IconBot}
              features={FEATURES_EX}
              accent="cyan"
              onClick={() => onSelectMode('EXPLORER_MODE')}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-4 px-6 border-t border-mars-border/30 flex flex-wrap gap-3 items-center justify-between text-[10px] font-mono text-slate-600">
        <span>Data: NASA JPL · USGS Astrogeology · OpenPlanetaryMap · MEDA (CAB-CSIC)</span>
        <span>Mars 2020 Perseverance Rover · NASA Space Apps Challenge 2026</span>
      </footer>
    </div>
  )
}

export default LandingPage
