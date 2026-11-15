// Modal: Full scientific dossier for a Perseverance discovery target
import { IconX } from './Icons'

function DossierModal({ discovery, onClose }) {
  if (!discovery) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="bg-mars-darker border border-mars-border rounded-xl max-w-xl w-full p-6 shadow-2xl relative space-y-4 max-h-[90vh] overflow-y-auto">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white transition" title="Close">
          <IconX className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-start justify-between border-b border-mars-border pb-3 pr-8">
          <div>
            <h2 className="text-lg font-mission font-bold text-mars-orange">{discovery.target_name}</h2>
            <div className="text-xs font-mono text-slate-400">
              Jezero Crater · Sol {discovery.sol}{discovery.earth_date ? ` (${discovery.earth_date})` : ''}
            </div>
          </div>
          <span className="px-2.5 py-1 rounded bg-mars-panel text-mars-cyan font-mono text-xs border border-mars-border shrink-0">
            {discovery.elevation_m}m Elev
          </span>
        </div>

        {/* Body */}
        <div className="space-y-3 text-xs">
          <div>
            <span className="font-mono text-slate-400 font-bold uppercase">Geological Context:</span>
            <p className="text-slate-200 mt-0.5 leading-relaxed">
              <strong>Formation:</strong> {discovery.geological_formation}<br/>
              <strong>Lithology:</strong> {discovery.lithology}
            </p>
          </div>

          <div>
            <span className="font-mono text-slate-400 font-bold uppercase">Scientific Findings:</span>
            <p className="text-slate-200 mt-0.5 leading-relaxed">{discovery.scientific_summary}</p>
          </div>

          <div>
            <span className="font-mono text-slate-400 font-bold uppercase">Detected Minerals:</span>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {discovery.mineralogy_detected?.map((m, i) => (
                <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-mars-cyan font-mono text-[11px] border border-slate-700">{m}</span>
              ))}
            </div>
          </div>

          <div>
            <span className="font-mono text-slate-400 font-bold uppercase">Biosignature Significance:</span>
            <div className="p-2.5 rounded bg-amber-950/30 border border-amber-800/60 text-amber-300 mt-1">
              {discovery.biosignature_potential}
            </div>
          </div>

          {discovery.sample_acquired && (
            <div className="p-3 rounded bg-emerald-950/30 border border-emerald-800/60 text-emerald-300 font-mono space-y-1">
              <div className="font-bold">🧪 Hermetically Sealed Core Sample</div>
              <div>Sample Name: {discovery.sample_name}</div>
              <div>Titanium Tube Serial: {discovery.sample_tube_serial}</div>
              <div>Depot / Carousel Status: {discovery.cache_status}</div>
            </div>
          )}

          <div className="p-2.5 rounded bg-mars-panel text-[11px] font-mono text-slate-400">
            <strong>NASA PDS / Science Publication Citation:</strong><br/>
            {discovery.nasa_pds_citation}
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded bg-mars-rust hover:bg-mars-red text-white font-mono text-xs font-semibold transition"
          >
            Close Dossier
          </button>
        </div>
      </div>
    </div>
  )
}

export default DossierModal
