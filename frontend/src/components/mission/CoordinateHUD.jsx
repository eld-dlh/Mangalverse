// CoordinateHUD – live cursor position, zoom level and active tool indicator

const TOOL_LABELS = {
  pan:            'PAN MODE',
  probe:          'TERRAIN PROBE',
  'select-start': 'SET START',
  'select-dest':  'SET DESTINATION',
  'add-checkpoint':'ADD CHECKPOINT',
}

const TOOL_COLORS = {
  pan:            'text-slate-400',
  probe:          'text-mars-neon',
  'select-start': 'text-emerald-400',
  'select-dest':  'text-mars-orange',
  'add-checkpoint':'text-mars-cyan',
}

function CoordinateHUD({ cursorPos, zoom, mapTool }) {
  const lat = cursorPos ? cursorPos.lat.toFixed(4) : '—'
  const lng = cursorPos ? cursorPos.lng.toFixed(4) : '—'
  const zoomVal = zoom ? zoom.toFixed(0) : '—'

  return (
    <div className="absolute bottom-4 left-4 z-20 pointer-events-none">
      <div className="flex items-center gap-3 bg-mars-darker/90 backdrop-blur-sm border border-mars-border rounded-lg px-3 py-1.5 shadow-lg">

        {/* Coordinates */}
        <div className="flex items-center gap-2 text-[10px] font-mono">
          <span className="text-slate-500 uppercase tracking-wider">LAT</span>
          <span className="text-mars-cyan tabular-nums w-16">{lat}°</span>
          <span className="text-slate-500 uppercase tracking-wider">LON</span>
          <span className="text-mars-cyan tabular-nums w-16">{lng}°</span>
        </div>

        {/* Divider */}
        <div className="w-px h-3 bg-mars-border" />

        {/* Zoom */}
        <div className="flex items-center gap-1.5 text-[10px] font-mono">
          <span className="text-slate-500 uppercase tracking-wider">ZOOM</span>
          <span className="text-slate-300 tabular-nums">{zoomVal}</span>
        </div>

        {/* Divider */}
        <div className="w-px h-3 bg-mars-border" />

        {/* Active tool */}
        <div className={`text-[10px] font-mono font-semibold uppercase tracking-wider ${TOOL_COLORS[mapTool] || 'text-slate-400'}`}>
          {TOOL_LABELS[mapTool] || 'PAN MODE'}
        </div>

        {/* Datum badge */}
        <div className="hidden sm:flex items-center gap-1 text-[9px] font-mono text-slate-600 uppercase">
          <span className="w-1 h-1 rounded-full bg-mars-border inline-block" />
          MOLA AREOID
        </div>
      </div>
    </div>
  )
}

export default CoordinateHUD
