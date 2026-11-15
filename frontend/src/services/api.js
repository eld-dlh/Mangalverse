/**
 * Mars Explorer API Service
 * Each function tries the real backend (/api/...) and falls back to mock data on error.
 */

// ---------------------------------------------------------------------------
// Mock fallback data
// ---------------------------------------------------------------------------

const MOCK_OBJECTIVES = [
  {
    id: 'obj-001',
    title: 'Characterize Ancient Habitability',
    description: 'Investigate the geology of Jezero Crater delta to assess past habitability.',
    priority: 'high',
    status: 'in_progress',
    progress: 68,
    sol_start: 1,
    sol_target: 400,
  },
  {
    id: 'obj-002',
    title: 'Sample Collection Campaign',
    description: 'Collect and cache 38 rock-core and regolith samples for potential Earth return.',
    priority: 'high',
    status: 'in_progress',
    progress: 42,
    sol_start: 50,
    sol_target: 600,
  },
  {
    id: 'obj-003',
    title: 'MOXIE Oxygen Production',
    description: 'Demonstrate in-situ oxygen production from CO₂ atmosphere via MOXIE instrument.',
    priority: 'medium',
    status: 'completed',
    progress: 100,
    sol_start: 10,
    sol_target: 300,
  },
  {
    id: 'obj-004',
    title: 'Ingenuity Flight Operations',
    description: 'Support Mars Helicopter scouting flights for route planning and science targets.',
    priority: 'medium',
    status: 'in_progress',
    progress: 55,
    sol_start: 5,
    sol_target: 500,
  },
];

const MOCK_DISCOVERIES = [
  {
    id: 'disc-001',
    name: 'Wildcat Ridge',
    type: 'biosignature',
    sol: 411,
    lon: 77.4312,
    lat: 18.4445,
    elevation_m: -2510,
    description: 'Mudstone outcrop with organic-rich laminations; highest biosignature potential to date.',
    biosignature_potential: 0.87,
    sample_acquired: true,
    minerals: ['olivine', 'carbonates', 'sulfates'],
  },
  {
    id: 'disc-002',
    name: 'Skinner Ridge',
    type: 'geological',
    sol: 356,
    lon: 77.4521,
    lat: 18.4398,
    elevation_m: -2490,
    description: 'Igneous breccia with signs of aqueous alteration.',
    biosignature_potential: 0.31,
    sample_acquired: true,
    minerals: ['pyroxene', 'feldspar', 'magnetite'],
  },
  {
    id: 'disc-003',
    name: 'Bellegarde',
    type: 'sample',
    sol: 288,
    lon: 77.4198,
    lat: 18.4512,
    elevation_m: -2525,
    description: 'Fine-grained sandstone deposited in delta foreset beds.',
    biosignature_potential: 0.52,
    sample_acquired: true,
    minerals: ['quartz', 'feldspar', 'chlorite'],
  },
];

const MOCK_TRAVERSE = {
  type: 'Feature',
  geometry: {
    type: 'LineString',
    coordinates: [
      [77.3812, 18.4421],
      [77.3934, 18.4467],
      [77.4078, 18.4502],
      [77.4213, 18.4489],
      [77.4312, 18.4445],
      [77.4421, 18.4398],
      [77.4521, 18.4356],
      [77.4634, 18.4312],
      [77.4745, 18.4278],
    ],
  },
  properties: {
    total_distance_km: 24.7,
    sols_driven: 312,
    start_sol: 1,
    current_sol: 870,
  },
};

const MOCK_MEDA = {
  sol: 870,
  timestamp: new Date().toISOString(),
  pressure_pa: 743.2,
  temperature: {
    surface_c: -63.4,
    air_1m_c: -58.1,
    air_1_5m_c: -59.2,
  },
  wind: {
    speed_ms: 3.7,
    direction_deg: 215,
  },
  humidity_pct: 0.8,
  uv_index: 2.1,
  dust_opacity: 0.42,
};

const MOCK_ELEVATION_POINT = {
  lon: 77.4312,
  lat: 18.4445,
  elevation_m: -2510.3,
  source: 'HRSC-mock',
};

const MOCK_ELEVATION_PROFILE = [
  { distance_km: 0.0, elevation_m: -2540 },
  { distance_km: 0.5, elevation_m: -2535 },
  { distance_km: 1.0, elevation_m: -2525 },
  { distance_km: 1.5, elevation_m: -2518 },
  { distance_km: 2.0, elevation_m: -2510 },
  { distance_km: 2.5, elevation_m: -2498 },
  { distance_km: 3.0, elevation_m: -2487 },
  { distance_km: 3.5, elevation_m: -2475 },
];

const MOCK_ROUTE_RESULT = {
  id: 'route-mock-001',
  status: 'calculated',
  distance_km: 5.4,
  duration_hours: 18.2,
  max_slope_deg: 12.3,
  avg_slope_deg: 4.1,
  elevation_gain_m: 85,
  warnings: ['Moderate slope near waypoint 3', 'Low battery margin at end'],
  path_geojson: {
    type: 'Feature',
    geometry: {
      type: 'LineString',
      coordinates: [
        [77.4100, 18.4350],
        [77.4178, 18.4389],
        [77.4245, 18.4421],
        [77.4312, 18.4445],
        [77.4389, 18.4418],
        [77.4456, 18.4392],
        [77.4521, 18.4356],
      ],
    },
    properties: {},
  },
};

const MOCK_ROUTE_COMPARISON = {
  shortest: {
    label: 'Shortest',
    distance_km: 4.2,
    duration_hours: 14.1,
    max_slope_deg: 18.5,
    avg_slope_deg: 7.3,
    elevation_gain_m: 112,
    warnings: ['Steep descent at waypoint 4 (18.5°)', 'Loose regolith detected'],
    path_geojson: {
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: [
          [77.4100, 18.4350],
          [77.4165, 18.4395],
          [77.4228, 18.4441],
          [77.4294, 18.4472],
          [77.4358, 18.4448],
          [77.4421, 18.4418],
          [77.4489, 18.4381],
          [77.4521, 18.4356],
        ],
      },
      properties: {},
    },
    metrics_color: 'text-mars-orange',
  },
  safest: {
    label: 'Safest',
    distance_km: 7.8,
    duration_hours: 26.4,
    max_slope_deg: 6.2,
    avg_slope_deg: 2.1,
    elevation_gain_m: 48,
    warnings: [],
    path_geojson: {
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: [
          [77.4100, 18.4350],
          [77.4132, 18.4312],
          [77.4198, 18.4290],
          [77.4278, 18.4310],
          [77.4345, 18.4352],
          [77.4412, 18.4388],
          [77.4478, 18.4365],
          [77.4521, 18.4356],
        ],
      },
      properties: {},
    },
    metrics_color: 'text-emerald-400',
  },
  balanced: {
    label: 'Balanced',
    distance_km: 5.4,
    duration_hours: 18.2,
    max_slope_deg: 11.4,
    avg_slope_deg: 4.1,
    elevation_gain_m: 73,
    warnings: ['Minor slope near waypoint 5'],
    path_geojson: {
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: [
          [77.4100, 18.4350],
          [77.4152, 18.4378],
          [77.4218, 18.4412],
          [77.4287, 18.4448],
          [77.4356, 18.4435],
          [77.4418, 18.4408],
          [77.4478, 18.4378],
          [77.4521, 18.4356],
        ],
      },
      properties: {},
    },
    metrics_color: 'text-mars-cyan',
  },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const BASE_URL = '';

/**
 * Build a query string from a plain object, skipping undefined/null values.
 * @param {Record<string, unknown>} params
 * @returns {string}
 */
function buildQuery(params) {
  const qs = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');
  return qs ? `?${qs}` : '';
}

/**
 * Generic GET helper.
 * @param {string} path
 * @returns {Promise<unknown>}
 */
async function get(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`GET ${path} → ${res.status} ${res.statusText}`);
  return res.json();
}

/**
 * Generic POST helper.
 * @param {string} path
 * @param {unknown} body
 * @returns {Promise<unknown>}
 */
async function post(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} → ${res.status} ${res.statusText}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Exported API functions
// ---------------------------------------------------------------------------

/**
 * Fetch mission objectives.
 * @returns {Promise<typeof MOCK_OBJECTIVES>}
 */
export async function fetchObjectives() {
  try {
    return await get('/api/objectives');
  } catch {
    console.warn('[api] fetchObjectives → using mock data');
    return MOCK_OBJECTIVES;
  }
}

/**
 * Fetch discoveries, optionally filtered.
 * @param {Record<string, unknown>} filters
 * @returns {Promise<typeof MOCK_DISCOVERIES>}
 */
export async function fetchDiscoveries(filters = {}) {
  try {
    return await get(`/api/discoveries${buildQuery(filters)}`);
  } catch {
    console.warn('[api] fetchDiscoveries → using mock data');
    return MOCK_DISCOVERIES;
  }
}

/**
 * Fetch the rover's full traverse path as GeoJSON.
 * @returns {Promise<typeof MOCK_TRAVERSE>}
 */
export async function fetchTraverse() {
  try {
    return await get('/api/rover/traverse');
  } catch {
    console.warn('[api] fetchTraverse → using mock data');
    return MOCK_TRAVERSE;
  }
}

/**
 * Fetch the latest MEDA environmental telemetry.
 * @returns {Promise<typeof MOCK_MEDA>}
 */
export async function fetchMedaTelemetry() {
  try {
    return await get('/api/environment/meda');
  } catch {
    console.warn('[api] fetchMedaTelemetry → using mock data');
    return MOCK_MEDA;
  }
}

/**
 * Fetch elevation for a single point.
 * @param {number} lon
 * @param {number} lat
 * @returns {Promise<typeof MOCK_ELEVATION_POINT>}
 */
export async function fetchElevationPoint(lon, lat) {
  try {
    return await get(`/api/elevation/point${buildQuery({ lon, lat })}`);
  } catch {
    console.warn('[api] fetchElevationPoint → using mock data');
    return { ...MOCK_ELEVATION_POINT, lon, lat };
  }
}

/**
 * Fetch an elevation profile for a list of coordinate pairs.
 * @param {[number, number][]} coords  Array of [lon, lat] pairs
 * @returns {Promise<typeof MOCK_ELEVATION_PROFILE>}
 */
export async function fetchElevationProfile(coords) {
  try {
    return await post('/api/elevation/profile', { coordinates: coords });
  } catch {
    console.warn('[api] fetchElevationProfile → using mock data');
    return MOCK_ELEVATION_PROFILE;
  }
}

/**
 * Calculate a single optimal route.
 * @param {Record<string, unknown>} payload  { start, end, waypoints?, strategy? }
 * @returns {Promise<typeof MOCK_ROUTE_RESULT>}
 */
export async function calculateRoute(payload) {
  try {
    return await post('/api/route/calculate', payload);
  } catch {
    console.warn('[api] calculateRoute → using mock data');
    return MOCK_ROUTE_RESULT;
  }
}

/**
 * Fetch a comparison of three route strategies (shortest / safest / balanced).
 * @param {Record<string, unknown>} payload  { start, end, waypoints? }
 * @returns {Promise<typeof MOCK_ROUTE_COMPARISON>}
 */
export async function fetchRouteComparison(payload) {
  try {
    return await post('/api/route/compare', payload);
  } catch {
    console.warn('[api] fetchRouteComparison → using mock data');
    return MOCK_ROUTE_COMPARISON;
  }
}
