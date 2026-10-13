/**
 * CRIMENET-X API Client
 * All calls use synthetic demo data only.
 */
const API_BASE = window.location.origin + '/api';

const api = {
  async request(method, path, body = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res = await fetch(API_BASE + path, opts);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      return await res.json();
    } catch (e) {
      console.error(`API [${method} ${path}]:`, e.message);
      throw e;
    }
  },

  get:    (path)       => api.request('GET',    path),
  post:   (path, body) => api.request('POST',   path, body),
  patch:  (path, body) => api.request('PATCH',  path, body),
  delete: (path)       => api.request('DELETE', path),

  // Health
  health: () => api.get('/health'),

  // Events
  getEvents:       (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return api.get(`/events${q ? '?' + q : ''}`);
  },
  getRecentEvents: (limit = 50) => api.get(`/events/recent?limit=${limit}`),
  postEvent:       (data)        => api.post('/events', data),
  getEventCount:   ()            => api.get('/events/count'),
  searchEvents:    (q)           => api.get(`/events/search?q=${encodeURIComponent(q)}`),

  // Nodes
  getNodes:        ()            => api.get('/nodes'),
  getNode:         (id)          => api.get(`/nodes/${id}`),
  updateNodeStatus:(id, data)    => api.patch(`/nodes/${id}/status`, data),

  // Networks
  getNetworks:     ()            => api.get('/networks'),
  getNetwork:      (id)          => api.get(`/networks/${id}`),
  getNetworkGraph: (id)          => api.get(`/networks/${id}/graph`),
  getFullGraph:    ()            => api.get('/networks/graph/full'),

  // Alerts
  getAlerts:       (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return api.get(`/alerts${q ? '?' + q : ''}`);
  },
  getAlert:        (id)          => api.get(`/alerts/${id}`),
  updateAlert:     (id, data)    => api.patch(`/alerts/${id}/status`, data),
  getAlertCount:   ()            => api.get('/alerts/count'),

  // Analytics
  getAnalytics:    ()            => api.get('/analytics'),
  getTemporal:     ()            => api.get('/analytics/temporal'),
  getPatterns:     ()            => api.get('/analytics/patterns'),
  getNetworkGraph2:()            => api.get('/analytics/network-graph'),

  // Hotspots
  getHotspots:     ()            => api.get('/hotspots'),

  // Demo
  startDemo:       ()            => api.post('/demo/start', {}),
  stopDemo:        ()            => api.post('/demo/stop', {}),
  getDemoStatus:   ()            => api.get('/demo/status'),

  // Data
  getDataStats:    ()            => api.get('/data/stats'),

  // Global search
  search: async (q) => {
    const [events, alerts] = await Promise.allSettled([
      api.searchEvents(q),
      api.get(`/alerts/search/q?q=${encodeURIComponent(q)}`),
    ]);
    return [
      ...(events.status === 'fulfilled' ? events.value : []),
      ...(alerts.status === 'fulfilled' ? alerts.value : []),
    ];
  },

  // CSV upload
  uploadCSV: async (file) => {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(API_BASE + '/data/upload', { method: 'POST', body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail);
    }
    return res.json();
  },
};

window.API = api;
