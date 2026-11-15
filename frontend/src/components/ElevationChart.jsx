// Interactive SVG Elevation Profile chart
function ElevationSvgChart({ profile, onHover }) {
  if (!profile || profile.length < 2) return null

  const W = 800, H = 100
  const padL = 40, padR = 20, padT = 15, padB = 20
  const chartW = W - padL - padR
  const chartH = H - padT - padB

  const dists = profile.map(p => p.distance_meters)
  const elevs = profile.map(p => p.elevation_m)
  const maxDist = Math.max(...dists)
  const minElev = Math.min(...elevs) - 5
  const maxElev = Math.max(...elevs) + 5
  const elevRange = maxElev - minElev || 1

  const pts = profile.map(p => {
    const x = padL + (p.distance_meters / (maxDist || 1)) * chartW
    const y = padT + chartH - ((p.elevation_m - minElev) / elevRange) * chartH
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })

  const polylineStr = pts.join(' ')
  const areaStr = `${padL},${padT + chartH} ${polylineStr} ${padL + chartW},${padT + chartH}`

  const handleMove = e => {
    const rect = e.currentTarget.getBoundingClientRect()
    const svgX = ((e.clientX - rect.left) / rect.width) * W
    if (svgX < padL || svgX > padL + chartW) return
    const frac = (svgX - padL) / chartW
    const targetDist = frac * maxDist
    let closest = profile[0], minDiff = Infinity
    profile.forEach(p => {
      const d = Math.abs(p.distance_meters - targetDist)
      if (d < minDiff) { minDiff = d; closest = p }
    })
    onHover(closest)
  }

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="w-full h-full cursor-crosshair overflow-visible"
      onMouseMove={handleMove}
      onMouseLeave={() => onHover(null)}
    >
      <defs>
        <linearGradient id="elevGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stopColor="#00d2ff" stopOpacity="0.4" />
          <stop offset="100%" stopColor="#00d2ff" stopOpacity="0"   />
        </linearGradient>
      </defs>

      {/* Grid */}
      <line x1={padL} y1={padT}             x2={padL+chartW} y2={padT}             stroke="#1e293b" strokeDasharray="3,3" />
      <line x1={padL} y1={padT+chartH/2}    x2={padL+chartW} y2={padT+chartH/2}    stroke="#1e293b" strokeDasharray="3,3" />
      <line x1={padL} y1={padT+chartH}      x2={padL+chartW} y2={padT+chartH}      stroke="#334155" />

      {/* Area fill + line */}
      <polygon points={areaStr} fill="url(#elevGrad)" />
      <polyline points={polylineStr} fill="none" stroke="#00d2ff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />

      {/* Y labels */}
      <text x={padL-6} y={padT+4}       fill="#64748b" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">{Math.round(maxElev)}m</text>
      <text x={padL-6} y={padT+chartH+3} fill="#64748b" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">{Math.round(minElev)}m</text>
      {/* X labels */}
      <text x={padL}       y={H-4} fill="#64748b" fontSize="9"              fontFamily="JetBrains Mono">0 km</text>
      <text x={padL+chartW} y={H-4} fill="#64748b" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">{(maxDist/1000).toFixed(1)} km</text>
    </svg>
  )
}

export default ElevationSvgChart
