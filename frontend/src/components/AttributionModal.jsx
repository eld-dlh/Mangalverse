// Modal: NASA data attribution & provenance
import { IconX } from './Icons'

function AttributionModal({ onClose }) {
  const sources = [
    {
      color: 'text-mars-orange',
      title: '1. Jezero Crater Elevation & Topography',
      desc:  'MRO HiRISE Stereo DTM & CTX Mosaic / USGS Astrogeology Science Center.',
      cite:  'Fergason et al., Mars 2020 Terrain Relative Navigation (TRN) HiRISE DTM Mosaic, USGS Astropedia.',
    },
    {
      color: 'text-mars-cyan',
      title: '2. Mars Environmental Dynamics Analyzer (MEDA)',
      desc:  'Atmospheric pressure, air/ground temperature, dust optical depth (tau), and wind.',
      cite:  'Rodriguez-Manfredi et al., The Mars Environmental Dynamics Analyzer (MEDA) Instrument Suite, Space Sci Rev (2021).',
    },
    {
      color: 'text-emerald-400',
      title: '3. Perseverance Rover Scientific Discoveries & Samples',
      desc:  'SHERLOC, PIXL, SuperCam, Mastcam-Z verified rock cores and observations.',
      cite:  'Farley et al., Science (2022); Scheller et al., Science (2022); Sharma et al., Nature (2023).',
    },
    {
      color: 'text-slate-200',
      title: '4. Rover Traverse & Localization Telemetry',
      desc:  'NASA Jet Propulsion Laboratory (JPL) MMGIS & Planetary Data System (PDS) Geosciences Node.',
      cite:  '',
    },
  ]

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="bg-mars-darker border border-mars-border rounded-xl max-w-xl w-full p-6 shadow-2xl relative space-y-4 font-mono text-xs max-h-[90vh] overflow-y-auto">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white transition">
          <IconX className="w-5 h-5" />
        </button>

        <div className="border-b border-mars-border pb-3">
          <h2 className="text-base font-mission font-bold text-slate-100 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
            NASA DATASET PROVENANCE & ATTRIBUTION
          </h2>
          <p className="text-[11px] text-slate-400 mt-1">
            Mangalverse complies with strict planetary data standards. All measurements, coordinates, and scientific analyses originate from authentic NASA mission releases.
          </p>
        </div>

        <div className="space-y-3">
          {sources.map((s, i) => (
            <div key={i} className="p-3 rounded bg-mars-panel border border-mars-border">
              <div className={`font-bold ${s.color}`}>{s.title}</div>
              <div className="text-slate-300 mt-0.5">{s.desc}</div>
              {s.cite && <div className="text-[10px] text-slate-500 mt-0.5">{s.cite}</div>}
            </div>
          ))}
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded bg-mars-panel hover:bg-slate-700 text-slate-200 font-semibold border border-mars-border transition"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  )
}

export default AttributionModal
