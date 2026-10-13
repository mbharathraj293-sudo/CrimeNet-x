/**
 * CRIMENET-X WebSocket Client
 * Manages real-time connection and event dispatching.
 */
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_URL = `${protocol}//${window.location.host}/ws/events`;

const wsClient = {
  socket: null,
  reconnectTimer: null,
  reconnectDelay: 3000,
  maxReconnectDelay: 30000,
  connected: false,
  handlers: {},

  connect() {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) return;

    try {
      this.socket = new WebSocket(WS_URL);

      this.socket.onopen = () => {
        this.connected = true;
        this.reconnectDelay = 3000;
        this._updateIndicators(true);
        console.log('[WS] Connected');
        this._emit('connected', {});
        // Keep-alive ping every 25s
        this._pingInterval = setInterval(() => {
          if (this.socket?.readyState === WebSocket.OPEN) {
            this.socket.send('ping');
          }
        }, 25000);
      };

      this.socket.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          this._emit(msg.type, msg);
          this._emit('*', msg); // Wildcard handler
        } catch (err) {
          console.warn('[WS] Parse error:', err);
        }
      };

      this.socket.onclose = () => {
        this.connected = false;
        clearInterval(this._pingInterval);
        this._updateIndicators(false);
        console.log('[WS] Disconnected. Reconnecting...');
        this._emit('disconnected', {});
        this._scheduleReconnect();
      };

      this.socket.onerror = (e) => {
        console.warn('[WS] Connection unavailable, falling back to REST updates.');
        this.socket.close();
      };

    } catch (e) {
      console.warn('[WS] Cannot connect:', e);
      this._updateIndicators(false);
      this._scheduleReconnect();
    }
  },

  disconnect() {
    clearTimeout(this.reconnectTimer);
    clearInterval(this._pingInterval);
    if (this.socket) {
      this.socket.onclose = null;
      this.socket.close();
      this.socket = null;
    }
    this.connected = false;
    this._updateIndicators(false);
  },

  on(type, handler) {
    if (!this.handlers[type]) this.handlers[type] = [];
    this.handlers[type].push(handler);
  },

  off(type, handler) {
    if (!this.handlers[type]) return;
    this.handlers[type] = this.handlers[type].filter(h => h !== handler);
  },

  _emit(type, data) {
    (this.handlers[type] || []).forEach(h => {
      try { h(data); } catch(e) { console.error('[WS] Handler error:', e); }
    });
  },

  _scheduleReconnect() {
    clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, this.maxReconnectDelay);
      this.connect();
    }, this.reconnectDelay);
  },

  _updateIndicators(connected) {
    // Update all WS indicator elements
    document.querySelectorAll('.ws-indicator').forEach(el => {
      el.classList.toggle('connected', connected);
      el.textContent = connected ? '● Live' : '● Offline';
      el.style.color = connected ? 'var(--color-success)' : 'var(--color-danger)';
    });
    document.querySelectorAll('.ws-dot').forEach(dot => {
      dot.style.background = connected ? 'var(--color-success)' : 'var(--color-danger)';
    });
  },
};

window.wsClient = wsClient;
