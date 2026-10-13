/**
 * CRIMENET-X Charts Module
 * Chart.js chart initializations and updates.
 */

// Global Chart.js defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#64748b';
  Chart.defaults.borderColor = '#1f2d3d';
  Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
  Chart.defaults.font.size = 11;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.padding = 16;
  Chart.defaults.plugins.tooltip.backgroundColor = '#1a2230';
  Chart.defaults.plugins.tooltip.borderColor = '#1f2d3d';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.titleColor = '#f1f5f9';
  Chart.defaults.plugins.tooltip.bodyColor = '#94a3b8';
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.padding = 10;
}

const Charts = {
  instances: {},

  destroy(id) {
    if (this.instances[id]) {
      this.instances[id].destroy();
      delete this.instances[id];
    }
  },

  /**
   * Activity Overview - Line chart (events + alerts over time)
   */
  createActivityChart(canvasId, data) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels || [],
        datasets: [
          {
            label: 'Events',
            data: data.events || [],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59,130,246,0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 6,
            borderWidth: 2,
          },
          {
            label: 'Alerts',
            data: data.alerts || [],
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239,68,68,0.05)',
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 6,
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { display: true } },
        scales: {
          x: {
            grid: { color: '#1f2d3d' },
            ticks: { maxTicksLimit: 8 },
          },
          y: {
            grid: { color: '#1f2d3d' },
            beginAtZero: true,
            ticks: { stepSize: 1 },
          },
        },
      },
    });
    return this.instances[canvasId];
  },

  /**
   * Hourly Distribution Bar Chart
   */
  createHourlyChart(canvasId, data) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels || [],
        datasets: [{
          label: 'Events',
          data: data.data || [],
          backgroundColor: (ctx) => {
            const val = ctx.parsed.y;
            const max = Math.max(...(data.data || [1]));
            const ratio = val / max;
            return `rgba(59,130,246,${0.3 + ratio * 0.6})`;
          },
          borderColor: '#3b82f6',
          borderWidth: 0,
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: '#1f2d3d' }, beginAtZero: true },
        },
      },
    });
    return this.instances[canvasId];
  },

  /**
   * Event Type Donut Chart
   */
  createEventTypeChart(canvasId, data) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const palette = ['#3b82f6','#22c55e','#f59e0b','#ef4444','#a78bfa','#14b8a6','#f97316','#ec4899'];

    this.instances[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.labels || [],
        datasets: [{
          data: data.data || [],
          backgroundColor: palette.slice(0, (data.labels || []).length),
          borderColor: '#0f1318',
          borderWidth: 3,
          hoverOffset: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: { position: 'right', labels: { padding: 12 } },
          tooltip: { callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw} events`,
          }},
        },
      },
    });
    return this.instances[canvasId];
  },

  /**
   * Zone Timeline Area Chart (multiple zones over time)
   */
  createZoneTimelineChart(canvasId, data) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels || [],
        datasets: data.datasets || [],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { display: true } },
        scales: {
          x: { grid: { color: '#1f2d3d' }, stacked: false },
          y: { grid: { color: '#1f2d3d' }, beginAtZero: true, stacked: false },
        },
      },
    });
    return this.instances[canvasId];
  },

  /**
   * Daily Distribution Line Chart
   */
  createDailyChart(canvasId, data) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels || [],
        datasets: [{
          label: 'Events per Day',
          data: data.data || [],
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34,197,94,0.08)',
          fill: true,
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#1f2d3d' } },
          y: { grid: { color: '#1f2d3d' }, beginAtZero: true },
        },
      },
    });
    return this.instances[canvasId];
  },

  /**
   * Network Evolution Cumulative Chart
   */
  createNetworkEvolutionChart(canvasId, data) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels || [],
        datasets: [{
          label: 'Network Relationships',
          data: data.data || [],
          borderColor: '#a78bfa',
          backgroundColor: 'rgba(167,139,250,0.08)',
          fill: true,
          tension: 0.4,
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#1f2d3d' } },
          y: { grid: { color: '#1f2d3d' }, beginAtZero: true },
        },
      },
    });
    return this.instances[canvasId];
  },

  /**
   * Update a chart's data without destroying it
   */
  update(id, labels, datasets) {
    const chart = this.instances[id];
    if (!chart) return;
    chart.data.labels = labels;
    if (Array.isArray(datasets)) {
      datasets.forEach((d, i) => {
        if (chart.data.datasets[i]) {
          chart.data.datasets[i].data = d.data || d;
        }
      });
    }
    chart.update('none');
  },
};

window.Charts = Charts;
