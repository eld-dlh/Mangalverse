// MapToolbar – floating vertical tool strip on the left side of the map
// Provides map interaction mode selection + utility actions

const TOOLS = [
  {
    id: 'pan',
    label: 'Pan / Select',
    title: 'Pan & Inspect (default)',
    accent: 'text-slate-200',
    activeBg: 'bg-mars-panel',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
        <path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"/>
        <path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"/>
        <path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v3"/>
        <path d="M18 11a2 2 0 1 1 4 0v3a8 8 0 0 1-8 8h-2a8 8 0 0 1-8-8v-5"/>
      </svg>
    ),
  },
  {
    id: 'probe',
    label: 'Terrain Probe',
    title: 'Click map to inspect elevation & slope',
    accent: 'text-mars-neon',
    activeBg: 'bg-mars-neon/10 border-mars-neon/40',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
        <circle cx="12" cy="12" r="1"/>
        <path d="M20.2 20.2c2.04-2.03.02-7.36-4.5-11.9C11.17 3.77 5.84 1.75 3.8 3.8c-2.04 2.04-.02 7.37 4.5 11.91 4.54 4.5 9.87 6.52 11.9 4.49z"/>
        <path d="M15.7 15.7c4.52 4.52 6.54 9.85 4.5 11.9"/>
      </svg>
    ),
  },
  {
    id: 'select-start',
    label: 'Set Start Point',
    title: 'Click map to set route start location',
    accent: 'text-emerald-400',
    activeBg: 'bg-emerald-900/20 border-emerald-500/40',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
        <circle cx="12" cy="12" r="10"/>
        <circle cx="12" cy="12" r="3"/>
        <line x1="12" y1="2" x2="12" y2="5"/>
        <line x1="12" y1="19" x2="12" y2="22"/>
        <line x1="2" y1="12" x2="5" y2="12"/>
        <line x1="19" y1="12" x2="22" y2="12"/>
      </svg>
    ),
  },
  {
    id: 'select-dest',
    label: 'Set Destination',
    title: 'Click map to set route destination',
    accent: 'text-mars-orange',
    activeBg: 'bg-mars-rust/15 border-mars-orange/40',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
        <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
        <circle cx="12" cy="10" r="3"/>
      </svg>
    ),
  },
  {
    id: 'add-checkpoint',
    label: 'Add Checkpoint',
    title: 'Click map to add an intermediate checkpoint',
    accent: 'text-mars-cyan',
    activeBg: 'bg-mars-cyan/10 border-mars-cyan/40',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="16"/>
        <line x1="8" y1="12" x2="16" y2="12"/>
      </svg>
    ),
  },
]

const IconHome = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
    <polyline points="9 22 9 12 15 12 15 22"/>
  </svg>
)

const IconFit = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
    <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
  </svg>
)

function MapToolbar({ mapTool, setMapTool, onResetView, onFitDiscoveries }) {
  return (
    <div className="absolute top-4 left-4 z-20 flex flex-col gap-1 pointer-events-auto">
      <div className="flex flex-col gap-0.5 bg-mars-darker/90 border border-mars-border rounded-xl backdrop-blur-sm shadow-xl p-1.5">
        {TOOLS.map(tool => {
          const isActive = mapTool === tool.id
          return (
            <button
              key={tool.id}
              title={tool.title}
              onClick={() => setMapTool(tool.id)}
              className={`
                w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-150
                border
                ${isActive
                  ? `${tool.activeBg} ${tool.accent} border-current/30 shadow-sm`
                  : 'border-transparent text-slate-500 hover:text-slate-200 hover:bg-mars-panel/60'}
              `}
            >
              {tool.icon}
            </button>
          )
        })}

        {/* Divider */}
        <div className="my-1 border-t border-mars-border/60" />

        {/* Reset view */}
        <button
          title="Reset to Jezero Crater"
          onClick={onResetView}
          className="w-9 h-9 rounded-lg flex items-center justify-center border border-transparent text-slate-500 hover:text-slate-200 hover:bg-mars-panel/60 transition-all"
        >
          <IconHome />
        </button>

        {/* Fit all discoveries */}
        <button
          title="Fit view to all discoveries"
          onClick={onFitDiscoveries}
          className="w-9 h-9 rounded-lg flex items-center justify-center border border-transparent text-slate-500 hover:text-slate-200 hover:bg-mars-panel/60 transition-all"
        >
          <IconFit />
        </button>
      </div>

      {/* Active tool label */}
      {mapTool !== 'pan' && (
        <div className="bg-mars-darker/90 border border-mars-border rounded-lg px-2 py-1 backdrop-blur-sm">
          <div className="text-[9px] font-mono uppercase tracking-widest text-slate-500">Active</div>
          <div className={`text-[10px] font-mono font-semibold ${TOOLS.find(t => t.id === mapTool)?.accent}`}>
            {TOOLS.find(t => t.id === mapTool)?.label}
          </div>
        </div>
      )}
    </div>
  )
}

export default MapToolbar
