// Top mission header / navigation bar
import { IconRocket, IconBot, IconVolume, IconVolumeMute, IconInfo } from './Icons'

function TopBar({ activeMode, setActiveMode, currentMedaReport, isVoiceEnabled, setIsVoiceEnabled, isSpeaking, onShowAttribution, onBackToLanding }) {
  const sol = currentMedaReport?.sol ?? '—'

  const handleVoiceToggle = () => {
    const next = !isVoiceEnabled
    setIsVoiceEnabled(next)
    if (!next && 'speechSynthesis' in window) window.speechSynthesis.cancel()
  }

  return (
    <header className="h-14 border-b border-mars-border bg-mars-darker flex items-center justify-between px-4 z-20 shrink-0 gap-2">
      {/* Brand */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onBackToLanding}
          title="Back to mode selection"
          className="w-8 h-8 rounded bg-gradient-to-br from-mars-rust to-mars-red flex items-center justify-center shadow-lg shadow-mars-red/20 border border-mars-orange/40 hover:scale-105 transition-transform shrink-0"
        >
          <span className="text-white font-mission font-bold text-xs">ME</span>
        </button>
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mission font-bold text-sm tracking-wider text-slate-100 whitespace-nowrap">MARS EXPLORER</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-mars-rust/30 text-mars-orange border border-mars-rust/50 font-semibold whitespace-nowrap">
              JEZERO CRATER
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/50 flex items-center gap-1 whitespace-nowrap">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              NASA VERIFIED
            </span>
          </div>
          <div className="hidden sm:flex text-[10px] font-mono text-slate-400 items-center gap-3">
            <span>LAT: 18.4447°N</span>
            <span>LON: 77.4508°E</span>
            <span>DATUM: MOLA AREOID</span>
            <span className="text-mars-cyan">SOL {sol}</span>
          </div>
        </div>
      </div>

      {/* Mode switcher */}
      <div className="flex items-center bg-mars-panel p-1 rounded-lg border border-mars-border shrink-0">
        <button
          onClick={() => setActiveMode('MISSION_CONTROL')}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-mono transition-all ${
            activeMode === 'MISSION_CONTROL'
              ? 'bg-mars-rust text-white shadow-md shadow-mars-rust/30 font-semibold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <IconRocket />
          <span className="hidden sm:inline">MISSION CONTROL</span>
          <span className="sm:hidden">MC</span>
        </button>
        <button
          onClick={() => setActiveMode('EXPLORER_MODE')}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-mono transition-all ${
            activeMode === 'EXPLORER_MODE'
              ? 'bg-mars-cyan text-mars-darkest font-bold shadow-md shadow-mars-cyan/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <IconBot />
          <span className="hidden sm:inline">EXPLORER MODE</span>
          <span className="sm:hidden">EX</span>
        </button>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-2 shrink-0">
        {activeMode === 'EXPLORER_MODE' && (
          <button
            onClick={handleVoiceToggle}
            title={isVoiceEnabled ? 'Mute ARES' : 'Enable ARES voice'}
            className={`p-2 rounded border text-xs font-mono flex items-center gap-1 transition ${
              isVoiceEnabled
                ? 'bg-mars-cyan/20 border-mars-cyan/50 text-mars-cyan'
                : 'bg-mars-panel border-mars-border text-slate-400'
            }`}
          >
            {isVoiceEnabled ? <IconVolume /> : <IconVolumeMute />}
            <span className="hidden sm:inline">{isSpeaking ? 'SPEAKING…' : 'ARES AUDIO'}</span>
          </button>
        )}
        <button
          onClick={onShowAttribution}
          className="px-2.5 py-1.5 rounded bg-mars-panel hover:bg-mars-border border border-mars-border text-xs font-mono text-slate-300 flex items-center gap-1.5 transition"
        >
          <IconInfo />
          <span className="hidden sm:inline">NASA SOURCES</span>
        </button>
      </div>
    </header>
  )
}

export default TopBar
