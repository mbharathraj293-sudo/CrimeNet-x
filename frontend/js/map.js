/**
 * CRIMENET-X Map Module
 * Leaflet.js map with event markers, field nodes, hotspot circles.
 */

const MapModule = {
  instances: {},

  /**
   * Initialize a Leaflet map.
   * @param {string} containerId - DOM element ID
   * @param {object} opts - { center, zoom }
   */
  init(containerId, opts = {}) {
    if (this.instances[containerId]) {
      this.instances[containerId].remove();
    }

    const center = opts.center || [12.9716, 77.5946];
    const zoom   = opts.zoom   || 12;

    const map = L.map(containerId, {
      center,
      zoom,
      zoomControl: true,
      attributionControl: false,
    });

    // OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);

    L.control.attribution({ prefix: false }).addTo(map);

    this.instances[containerId] = map;
    this.instances[containerId + '_layers'] = {
      events: L.layerGroup().addTo(map),
      nodes:  L.layerGroup().addTo(map),
      hotspots: L.layerGroup().addTo(map),
    };

    return map;
  },

  getMap(id) {
    return this.instances[id];
  },

  getLayers(id) {
    return this.instances[id + '_layers'];
  },

  clearLayer(mapId, layerName) {
    const layers = this.getLayers(mapId);
    if (layers && layers[layerName]) {
      layers[layerName].clearLayers();
    }
  },

  /**
   * Create a custom circular marker
   */
  _circleMarker(lat, lon, color, radius = 8) {
    return L.circleMarker([lat, lon], {
      radius,
      fillColor: color,
      color: color,
      weight: 2,
      opacity: 0.9,
      fillOpacity: 0.7,
    });
  },

  /**
   * Add event markers to the map
   */
  addEventMarkers(mapId, markers) {
    this.clearLayer(mapId, 'events');
    const layers = this.getLayers(mapId);
    if (!layers) return;

    const colorMap = {
      high:   '#ef4444',
      medium: '#f59e0b',
      low:    '#22c55e',
    };

    markers.forEach(m => {
      if (!m.latitude || !m.longitude) return;
      const color  = colorMap[m.severity] || '#3b82f6';
      const marker = this._circleMarker(m.latitude, m.longitude, color, 7);

      const popupContent = `
        <div class="map-popup-title">${m.event_id}</div>
        <div><b>Type:</b> ${m.event_type}</div>
        <div><b>Zone:</b> ${m.zone_id}</div>
        <div><b>Node:</b> ${m.node_id}</div>
        <div><b>Severity:</b> ${m.severity}</div>
        <div><b>Time:</b> ${m.timestamp ? new Date(m.timestamp).toLocaleString() : '—'}</div>
      `;
      marker.bindPopup(popupContent, { maxWidth: 240 });
      layers.events.addLayer(marker);
    });
  },

  /**
   * Add field node markers
   */
  addNodeMarkers(mapId, nodes) {
    this.clearLayer(mapId, 'nodes');
    const layers = this.getLayers(mapId);
    if (!layers) return;

    nodes.forEach(n => {
      if (!n.latitude || !n.longitude) return;
      const color  = n.status === 'online' ? '#22c55e' : '#ef4444';
      const marker = L.circleMarker([n.latitude, n.longitude], {
        radius: 10,
        fillColor: color,
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9,
      });

      const popupContent = `
        <div class="map-popup-title">${n.node_id} — ${n.name}</div>
        <div><b>Zone:</b> ${n.zone_id}</div>
        <div><b>Status:</b> <span style="color:${color}">${n.status?.toUpperCase()}</span></div>
        <div><b>Battery:</b> ${n.battery}%</div>
        <div><b>Signal:</b> ${n.signal_strength} dBm</div>
      `;
      marker.bindPopup(popupContent, { maxWidth: 220 });
      layers.nodes.addLayer(marker);
    });
  },

  /**
   * Add hotspot circles
   */
  addHotspotCircles(mapId, hotspots) {
    this.clearLayer(mapId, 'hotspots');
    const layers = this.getLayers(mapId);
    if (!layers) return;

    const colorMap = {
      high:   { fill: '#ef4444', stroke: '#ef4444' },
      medium: { fill: '#f59e0b', stroke: '#f59e0b' },
      low:    { fill: '#22c55e', stroke: '#22c55e' },
    };

    hotspots.forEach(h => {
      if (!h.latitude || !h.longitude) return;
      const c = colorMap[h.activity_level] || colorMap.low;

      const circle = L.circle([h.latitude, h.longitude], {
        radius: h.radius || 200,
        fillColor: c.fill,
        color: c.stroke,
        weight: 1,
        fillOpacity: 0.1,
        opacity: 0.5,
      });

      const popup = `
        <div class="map-popup-title">${h.zone_id} — ${h.zone_name}</div>
        <div><b>Observations:</b> ${h.count}</div>
        <div><b>Activity Level:</b> ${h.activity_level?.toUpperCase()}</div>
        <div><b>Pattern Status:</b> ${h.pattern_status}</div>
        <div><b>Time Span:</b> ${h.time_span_hours}h</div>
        <div style="margin-top:6px;font-style:italic;color:var(--color-warning)">${h.recommendation}</div>
      `;
      circle.bindPopup(popup, { maxWidth: 260 });
      layers.hotspots.addLayer(circle);
    });
  },

  /**
   * Add a single new event marker with pulse animation
   */
  addLiveMarker(mapId, event) {
    const layers = this.getLayers(mapId);
    if (!layers || !event.latitude || !event.longitude) return;

    const colorMap = { high: '#ef4444', medium: '#f59e0b', low: '#22c55e' };
    const color = colorMap[event.severity] || '#3b82f6';

    const marker = L.circleMarker([event.latitude, event.longitude], {
      radius: 10,
      fillColor: color,
      color: '#fff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.85,
      className: 'live-marker',
    });

    marker.bindPopup(`
      <div class="map-popup-title">${event.event_id} <span style="color:var(--color-success)">NEW</span></div>
      <div><b>Type:</b> ${event.event_type}</div>
      <div><b>Zone:</b> ${event.zone_id}</div>
      <div><b>Node:</b> ${event.node_id}</div>
    `);

    layers.events.addLayer(marker);

    // Fade out after 8 seconds
    setTimeout(() => {
      try { layers.events.removeLayer(marker); } catch {}
    }, 8000);
  },

  toggleLayer(mapId, layerName, visible) {
    const map    = this.getMap(mapId);
    const layers = this.getLayers(mapId);
    if (!map || !layers || !layers[layerName]) return;

    if (visible) {
      map.addLayer(layers[layerName]);
    } else {
      map.removeLayer(layers[layerName]);
    }
  },

  fitBounds(mapId, markers) {
    const map = this.getMap(mapId);
    if (!map || !markers.length) return;
    const coords = markers
      .filter(m => m.latitude && m.longitude)
      .map(m => [m.latitude, m.longitude]);
    if (coords.length) {
      map.fitBounds(L.latLngBounds(coords).pad(0.1));
    }
  },
};

window.MapModule = MapModule;
