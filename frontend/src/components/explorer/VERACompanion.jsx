// VERA – Virtual Exploration & Reconnaissance Assistant
// Original character design — geometric SVG avatar, not cartoon

export function VERAAvatar({ isSpeaking, size = 'md' }) {
  const dim = size === 'lg' ? 72 : size === 'sm' ? 36 : 52

  return (
    <div
      className={`relative shrink-0 rounded-full flex items-center justify-center ${isSpeaking ? 'companion-pulse' : ''}`}
      style={{ width: dim, height: dim }}
    >
      {/* Outer ring glow */}
      <div
        className="absolute inset-0 rounded-full opacity-30"
        style={{
          background: 'conic-gradient(from 180deg, #00d2ff, #00ffc8, #c1440e, #00d2ff)',
          animation: 'spin 8s linear infinite',
        }}
      />
      {/* Inner face plate */}
      <div
        className="absolute rounded-full bg-gradient-to-br from-slate-900 to-mars-darkest border border-mars-cyan/40"
        style={{ inset: 3 }}
      />
      {/* SVG Face — geometric, not cartoon */}
      <svg
        viewBox="0 0 48 48"
        fill="none"
        style={{ width: dim * 0.65, height: dim * 0.65, position: 'relative', zIndex: 1 }}
      >
        {/* Sensor array — top horizontal bar */}
        <rect x="10" y="10" width="28" height="3" rx="1.5" fill="#00d2ff" opacity="0.9" />
        {/* Left optical sensor */}
        <circle cx="16" cy="22" r="4" fill="none" stroke="#00ffc8" strokeWidth="1.5" />
        <circle cx="16" cy="22" r="2" fill="#00ffc8" opacity={isSpeaking ? 1 : 0.7} />
        {/* Right optical sensor */}
        <circle cx="32" cy="22" r="4" fill="none" stroke="#00ffc8" strokeWidth="1.5" />
        <circle cx="32" cy="22" r="2" fill="#00ffc8" opacity={isSpeaking ? 1 : 0.7} />
        {/* Voice array — animated bars when speaking */}
        {isSpeaking ? (
          <>
            <rect x="13" y="32" width="3" height="6" rx="1" fill="#00d2ff">
              <animate attributeName="height" values="6;10;4;8;6" dur="0.4s" repeatCount="indefinite" />
              <animate attributeName="y" values="32;30;34;31;32" dur="0.4s" repeatCount="indefinite" />
            </rect>
            <rect x="18" y="30" width="3" height="8" rx="1" fill="#00ffc8">
              <animate attributeName="height" values="8;4;10;5;8" dur="0.5s" repeatCount="indefinite" />
              <animate attributeName="y" values="30;34;28;33;30" dur="0.5s" repeatCount="indefinite" />
            </rect>
            <rect x="23" y="28" width="3" height="12" rx="1" fill="#00d2ff">
              <animate attributeName="height" values="12;6;14;8;12" dur="0.35s" repeatCount="indefinite" />
              <animate attributeName="y" values="28;32;26;31;28" dur="0.35s" repeatCount="indefinite" />
            </rect>
            <rect x="28" y="30" width="3" height="8" rx="1" fill="#00ffc8">
              <animate attributeName="height" values="8;12;5;10;8" dur="0.45s" repeatCount="indefinite" />
              <animate attributeName="y" values="30;27;33;29;30" dur="0.45s" repeatCount="indefinite" />
            </rect>
            <rect x="33" y="32" width="3" height="6" rx="1" fill="#00d2ff">
              <animate attributeName="height" values="6;9;4;7;6" dur="0.55s" repeatCount="indefinite" />
              <animate attributeName="y" values="32;30;34;31;32" dur="0.55s" repeatCount="indefinite" />
            </rect>
          </>
        ) : (
          /* Idle status bar */
          <rect x="13" y="34" width="22" height="2" rx="1" fill="#2c354e" />
        )}
        {/* Signal indicator dots — top right */}
        <circle cx="38" cy="10" r="1.5" fill={isSpeaking ? '#00ffc8' : '#2c354e'} />
        <circle cx="42" cy="10" r="1.5" fill={isSpeaking ? '#00d2ff' : '#1f2538'} />
      </svg>

      {/* Speaking badge */}
      {isSpeaking && (
        <div className="absolute -bottom-1 -right-1 px-1.5 py-0.5 rounded-full bg-mars-neon text-mars-darkest font-mono text-[8px] font-bold leading-none whitespace-nowrap z-10">
          LIVE
        </div>
      )}
    </div>
  )
}

export function VERASpeechBubble({ text, onReplay, isSpeaking }) {
  if (!text) return null
  return (
    <div className="relative">
      {/* Bubble tail */}
      <div className="absolute -top-2 left-8 w-0 h-0 border-l-[8px] border-r-[8px] border-b-[8px] border-transparent border-b-mars-cyan/30" />
      <div className="p-4 rounded-xl bg-gradient-to-br from-slate-900/95 to-mars-darkest border border-mars-cyan/30 shadow-lg shadow-mars-cyan/10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-mono text-mars-cyan font-semibold tracking-wider uppercase">
            VERA · Expedition Log
          </span>
          <button
            onClick={onReplay}
            disabled={isSpeaking}
            title="Replay narration"
            className="text-[10px] text-slate-500 hover:text-mars-cyan flex items-center gap-1 transition disabled:opacity-40"
          >
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            {isSpeaking ? 'Playing…' : 'Replay'}
          </button>
        </div>
        <p className="text-sm text-slate-100 leading-relaxed font-sans">
          "{text}"
        </p>
      </div>
    </div>
  )
}
