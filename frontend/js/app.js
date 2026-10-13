/**
 * CRIMENET-X Toast Notification System
 */
const Toast = {
  container: null,

  init() {
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(type, title, message = '', duration = 4000) {
    if (!this.container) this.init();

    const icons = {
      success: 'fa-check-circle',
      error:   'fa-times-circle',
      warning: 'fa-exclamation-triangle',
      info:    'fa-info-circle',
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <i class="fas ${icons[type] || 'fa-info-circle'} toast-icon"></i>
      <div class="toast-body">
        <div class="toast-title">${title}</div>
        ${message ? `<div class="toast-msg">${message}</div>` : ''}
      </div>
      <button class="toast-close" onclick="this.closest('.toast').remove()">
        <i class="fas fa-times"></i>
      </button>
    `;

    this.container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => {
        toast.classList.add('toast-hide');
        toast.addEventListener('animationend', () => toast.remove());
      }, duration);
    }

    return toast;
  },

  success: (title, msg, dur) => Toast.show('success', title, msg, dur),
  error:   (title, msg, dur) => Toast.show('error',   title, msg, dur),
  warning: (title, msg, dur) => Toast.show('warning', title, msg, dur),
  info:    (title, msg, dur) => Toast.show('info',    title, msg, dur),
};

window.Toast = Toast;

/**
 * Global Application Core
 */
const App = {
  currentPage: 'command-center',
  demoRunning: false,

  init() {
    Toast.init();
    this.setupClock();
    this.setupSidebar();
    this.setupSearch();
    this.connectAPI();
    this.initWebSocket();
  },

  setupClock() {
    const updateClock = () => {
      const now = new Date();
      document.querySelectorAll('.topbar-time').forEach(el => {
        el.textContent = now.toLocaleTimeString('en-US', { hour12: false });
      });
    };
    updateClock();
    setInterval(updateClock, 1000);
  },

  setupSidebar() {
    const hamburger = document.getElementById('btn-hamburger');
    const sidebar   = document.getElementById('sidebar');
    const overlay   = document.getElementById('sidebar-overlay');

    if (hamburger) {
      hamburger.addEventListener('click', () => {
        sidebar?.classList.toggle('mobile-open');
        overlay?.classList.toggle('active');
      });
    }

    if (overlay) {
      overlay.addEventListener('click', () => {
        sidebar?.classList.remove('mobile-open');
        overlay.classList.remove('active');
      });
    }

    // Close sidebar when nav item clicked (mobile)
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', () => {
        if (window.innerWidth <= 1024) {
          sidebar?.classList.remove('mobile-open');
          overlay?.classList.remove('active');
        }
      });
    });
  },

  setupSearch() {
    const input   = document.getElementById('global-search');
    const results = document.getElementById('search-results');
    if (!input || !results) return;

    let timer;
    input.addEventListener('input', () => {
      clearTimeout(timer);
      const q = input.value.trim();
      if (q.length < 2) { results.classList.add('hidden'); return; }

      timer = setTimeout(async () => {
        try {
          const items = await API.search(q);
          if (!items.length) { results.classList.add('hidden'); return; }

          results.innerHTML = items.slice(0, 8).map(r => `
            <div class="search-result-item" onclick="App.navigateToResult('${r.type}','${r.id}')">
              <span class="search-result-type">${r.type}</span>
              <div>
                <div style="font-size:var(--text-sm);color:var(--color-text-primary);font-weight:500">${r.title}</div>
                <div style="font-size:var(--text-xs);color:var(--color-text-muted)">${r.subtitle || ''}</div>
              </div>
            </div>
          `).join('');
          results.classList.remove('hidden');
        } catch {
          results.classList.add('hidden');
        }
      }, 300);
    });

    document.addEventListener('click', e => {
      if (!input.contains(e.target) && !results.contains(e.target)) {
        results.classList.add('hidden');
      }
    });
  },

  navigateToResult(type, id) {
    const pageMap = { event: 'live-events', node: 'field-nodes', alert: 'alert-center', network: 'network-intelligence' };
    const page = pageMap[type] || 'command-center';
    window.location.href = `/pages/${page}.html`;
  },

  async connectAPI() {
    const indicator = document.getElementById('api-indicator');
    try {
      await API.health();
      if (indicator) {
        indicator.textContent = '● API Connected';
        indicator.style.color = 'var(--color-success)';
      }
    } catch {
      if (indicator) {
        indicator.textContent = '● API Disconnected';
        indicator.style.color = 'var(--color-danger)';
      }
      Toast.warning('Backend Disconnected', 'Running in offline mode with demo data.', 6000);
    }
  },

  initWebSocket() {
    wsClient.connect();

    wsClient.on('new_event', (msg) => {
      // Update KPI counters if present
      const totalEl = document.getElementById('kpi-total-events');
      if (totalEl) {
        const cur = parseInt(totalEl.textContent) || 0;
        totalEl.textContent = cur + 1;
        // Animate
        totalEl.parentElement?.classList.add('kpi-updated');
        setTimeout(() => totalEl.parentElement?.classList.remove('kpi-updated'), 500);
      }
      // Toast for first few demo events
      if (App.demoRunning) {
        // Only toast occasionally to avoid spam
        if (Math.random() < 0.1) {
          Toast.info('New Event', `${msg.event?.event_type} in ${msg.event?.zone_id}`, 2000);
        }
      }
    });

    wsClient.on('demo_started', () => {
      App.demoRunning = true;
      document.querySelectorAll('.demo-badge').forEach(b => b.classList.add('active'));
      document.getElementById('btn-demo-start')?.classList.add('hidden');
      document.getElementById('btn-demo-stop')?.classList.remove('hidden');
      Toast.success('Demo Mode Active', 'Synthetic events are being generated.', 4000);
    });

    wsClient.on('demo_stopped', (msg) => {
      App.demoRunning = false;
      document.querySelectorAll('.demo-badge').forEach(b => b.classList.remove('active'));
      document.getElementById('btn-demo-start')?.classList.remove('hidden');
      document.getElementById('btn-demo-stop')?.classList.add('hidden');
      Toast.info('Demo Stopped', `${msg.generated || 0} synthetic events generated.`, 4000);
    });

    wsClient.on('alert_update', (msg) => {
      Toast.warning('Alert Updated', `${msg.alert?.title} → ${msg.alert?.status}`, 3000);
    });
  },

  async toggleDemo() {
    try {
      if (App.demoRunning) {
        const res = await API.stopDemo();
        if (!wsClient.connected) {
          App.demoRunning = false;
          document.querySelectorAll('.demo-badge').forEach(b => b.classList.remove('active'));
          document.getElementById('btn-demo-start')?.classList.remove('hidden');
          document.getElementById('btn-demo-stop')?.classList.add('hidden');
          Toast.info('Demo Stopped', `${res?.generated || 0} synthetic events generated.`, 4000);
        }
      } else {
        await API.startDemo();
        if (!wsClient.connected) {
          App.demoRunning = true;
          document.querySelectorAll('.demo-badge').forEach(b => b.classList.add('active'));
          document.getElementById('btn-demo-start')?.classList.add('hidden');
          document.getElementById('btn-demo-stop')?.classList.remove('hidden');
          Toast.success('Demo Mode Active', 'Synthetic events are being generated.', 4000);
        }
      }
    } catch (e) {
      Toast.error('Demo Error', e.message);
    }
  },

  formatTimestamp(ts) {
    if (!ts) return '—';
    const d = new Date(ts + (ts.endsWith('Z') ? '' : 'Z'));
    if (isNaN(d)) return ts;
    return d.toLocaleString('en-US', {
      month: 'short', day: '2-digit',
      hour: '2-digit', minute: '2-digit', hour12: false
    });
  },

  timeAgo(ts) {
    if (!ts) return '—';
    const d = new Date(ts + (ts.endsWith('Z') ? '' : 'Z'));
    const diff = (Date.now() - d.getTime()) / 1000;
    if (diff < 60)   return `${Math.round(diff)}s ago`;
    if (diff < 3600) return `${Math.round(diff/60)}m ago`;
    if (diff < 86400)return `${Math.round(diff/3600)}h ago`;
    return `${Math.round(diff/86400)}d ago`;
  },

  severityBadge(sev) {
    const map = {
      high:   '<span class="badge badge-high">High</span>',
      medium: '<span class="badge badge-medium">Medium</span>',
      low:    '<span class="badge badge-low">Low</span>',
      info:   '<span class="badge badge-info">Info</span>',
    };
    return map[sev?.toLowerCase()] || `<span class="badge">${sev || '—'}</span>`;
  },

  statusBadge(status) {
    const map = {
      new:          '<span class="badge badge-new">New</span>',
      under_review: '<span class="badge badge-review">Under Review</span>',
      resolved:     '<span class="badge badge-resolved">Resolved</span>',
      online:       '<span class="badge badge-online">Online</span>',
      offline:      '<span class="badge badge-offline">Offline</span>',
      processed:    '<span class="badge badge-low">Processed</span>',
    };
    return map[status?.toLowerCase()] || `<span class="badge">${status || '—'}</span>`;
  },
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => App.init());
window.App = App;
