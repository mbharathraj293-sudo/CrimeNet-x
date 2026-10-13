/**
 * CRIMENET-X Network Graph Module
 * Cytoscape.js network visualization.
 */

const NetworkGraph = {
  cy: null,

  /**
   * Initialize Cytoscape instance
   * @param {string} containerId
   * @param {Array} elements - Cytoscape elements array
   */
  init(containerId, elements = []) {
    if (this.cy) {
      this.cy.destroy();
      this.cy = null;
    }

    const container = document.getElementById(containerId);
    if (!container) return;

    const colorMap = {
      zone:        '#4f8ef7',
      field_node:  '#22c55e',
      event_type:  '#f59e0b',
      entity:      '#a78bfa',
      default:     '#64748b',
    };

    this.cy = cytoscape({
      container,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color':     (ele) => colorMap[ele.data('type')] || colorMap.default,
            'label':                'data(label)',
            'color':                '#f1f5f9',
            'font-size':            '10px',
            'font-family':          'Inter, sans-serif',
            'text-valign':          'bottom',
            'text-margin-y':        '6px',
            'text-wrap':            'ellipsis',
            'text-max-width':       '80px',
            'width':                (ele) => 20 + (ele.data('centrality') || 0) * 30,
            'height':               (ele) => 20 + (ele.data('centrality') || 0) * 30,
            'border-width':         1.5,
            'border-color':         'rgba(255,255,255,0.1)',
            'transition-property':  'background-color, border-color, width, height',
            'transition-duration':  '0.2s',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#ffffff',
            'border-width':  3,
            'overlay-color':'#3b82f6',
            'overlay-padding':'4px',
            'overlay-opacity': 0.2,
          },
        },
        {
          selector: 'edge',
          style: {
            'width':            (ele) => 1 + Math.min((ele.data('weight') || 1) * 0.4, 4),
            'line-color':       '#263346',
            'curve-style':      'bezier',
            'target-arrow-shape':'triangle',
            'target-arrow-color':'#263346',
            'arrow-scale':      0.6,
            'opacity':          0.7,
            'transition-property':'opacity, line-color',
            'transition-duration':'0.2s',
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color':         '#3b82f6',
            'target-arrow-color':'#3b82f6',
            'opacity':            1,
          },
        },
        {
          selector: '.highlighted',
          style: {
            'background-color': '#3b82f6',
            'line-color':       '#3b82f6',
            'opacity':          1,
          },
        },
        {
          selector: '.faded',
          style: {
            'opacity': 0.15,
          },
        },
      ],
      layout: {
        name:     'cose',
        animate:  true,
        animationDuration: 600,
        randomize: false,
        nodeOverlap: 20,
        refresh: 20,
        fit: true,
        padding: 30,
        idealEdgeLength: 80,
        nodeRepulsion: 4500,
        edgeElasticity: 120,
        gravity: 0.25,
      },
      minZoom:  0.2,
      maxZoom:  4.0,
      wheelSensitivity: 0.2,
    });

    this._bindEvents();
    return this.cy;
  },

  _bindEvents() {
    if (!this.cy) return;

    this.cy.on('tap', 'node', (e) => {
      const node = e.target;
      this._highlightNeighbors(node);
      this._showNodeDetails(node.data());
    });

    this.cy.on('tap', (e) => {
      if (e.target === this.cy) {
        this._clearHighlight();
        this._hideDetails();
      }
    });

    this.cy.on('mouseover', 'node', (e) => {
      e.target.style('cursor', 'pointer');
    });
  },

  _highlightNeighbors(node) {
    const neighborhood = node.neighborhood().add(node);
    this.cy.elements().addClass('faded');
    neighborhood.removeClass('faded').addClass('highlighted');
  },

  _clearHighlight() {
    this.cy.elements().removeClass('faded highlighted');
  },

  _showNodeDetails(data) {
    const panel = document.getElementById('node-detail-panel');
    if (!panel) return;

    panel.innerHTML = `
      <div class="detail-row">
        <span class="detail-key">Node ID</span>
        <span class="detail-value mono" style="font-size:12px">${data.id}</span>
      </div>
      <div class="detail-row">
        <span class="detail-key">Type</span>
        <span class="detail-value">${data.type || '—'}</span>
      </div>
      <div class="detail-row">
        <span class="detail-key">Community</span>
        <span class="detail-value">${data.community || '—'}</span>
      </div>
      <div class="detail-row">
        <span class="detail-key">Degree Centrality</span>
        <span class="detail-value">${data.centrality || '—'}</span>
      </div>
      <div class="detail-row">
        <span class="detail-key">Betweenness</span>
        <span class="detail-value">${data.betweenness || '—'}</span>
      </div>
    `;
    panel.style.display = 'block';
  },

  _hideDetails() {
    const panel = document.getElementById('node-detail-panel');
    if (panel) panel.style.display = 'none';
  },

  /**
   * Load new elements into graph
   */
  loadElements(elements) {
    if (!this.cy) return;
    this.cy.elements().remove();
    this.cy.add(elements);
    this.runLayout();
  },

  runLayout(layoutName = 'cose') {
    if (!this.cy) return;
    const layout = this.cy.layout({
      name: layoutName,
      animate: true,
      animationDuration: 500,
      randomize: false,
      fit: true,
      padding: 30,
      nodeRepulsion: 4500,
    });
    layout.run();
  },

  fit()   { this.cy?.fit(undefined, 30); },
  reset() { this.fit(); this._clearHighlight(); },

  zoomIn()  { this.cy?.zoom(this.cy.zoom() * 1.3); },
  zoomOut() { this.cy?.zoom(this.cy.zoom() * 0.77); },

  /**
   * Add a single new node/edge (real-time)
   */
  addElement(ele) {
    if (!this.cy) return;
    this.cy.add(ele);
    this.runLayout();
  },

  destroy() {
    if (this.cy) {
      this.cy.destroy();
      this.cy = null;
    }
  },
};

window.NetworkGraph = NetworkGraph;
