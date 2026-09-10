/**
 * SmartSociety 360 - Chart.js Visualizations & Dashboard Analytics
 * Fully data-driven and reactive to theme mode changes.
 */

function formatIndianRupee(num) {
  if (num === null || num === undefined || isNaN(num)) return '₹0.00';
  const val = Number(num);
  return '₹' + val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function initFinanceChart(canvasId, incomeData, expenseData, labels) {
  const canvas = typeof canvasId === 'string' ? document.getElementById(canvasId) : canvasId;
  if (!canvas) return;

  // Safe cleanup of previous chart instance
  if (canvas._chartInstance) {
    canvas._chartInstance.destroy();
  }

  // Detect dark vs light theme
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#94a3b8' : '#64748b';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(0, 0, 0, 0.06)';

  const parsedLabels = (labels && labels.length > 0) ? labels : ['No Data'];
  const parsedIncome = (incomeData && incomeData.length > 0) ? incomeData : [0];
  const parsedExpense = (expenseData && expenseData.length > 0) ? expenseData : [0];

  canvas._chartInstance = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: parsedLabels,
      datasets: [
        {
          label: 'Total Revenue (₹)',
          data: parsedIncome,
          backgroundColor: 'rgba(16, 185, 129, 0.85)',
          hoverBackgroundColor: 'rgba(16, 185, 129, 1)',
          borderRadius: 6,
          borderSkipped: false,
          maxBarThickness: 38,
        },
        {
          label: 'Society Operating Expenses (₹)',
          data: parsedExpense,
          backgroundColor: 'rgba(244, 63, 94, 0.85)',
          hoverBackgroundColor: 'rgba(244, 63, 94, 1)',
          borderRadius: 6,
          borderSkipped: false,
          maxBarThickness: 38,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            color: textColor,
            font: {
              family: "'Inter', -apple-system, sans-serif",
              size: 12,
              weight: '600'
            },
            usePointStyle: true,
            boxWidth: 8,
            padding: 16
          }
        },
        tooltip: {
          backgroundColor: isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.96)',
          titleColor: isDark ? '#f8fafc' : '#0f172a',
          bodyColor: isDark ? '#cbd5e1' : '#334155',
          borderColor: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          callbacks: {
            label: function(context) {
              const label = context.dataset.label || '';
              const val = context.parsed.y !== null ? context.parsed.y : 0;
              return ` ${label}: ${formatIndianRupee(val)}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: textColor,
            font: {
              family: "'Inter', -apple-system, sans-serif",
              size: 11
            }
          }
        },
        y: {
          beginAtZero: true,
          grid: { color: gridColor },
          ticks: {
            color: textColor,
            font: {
              family: "'Inter', -apple-system, sans-serif",
              size: 11
            },
            callback: function(value) {
              if (value >= 10000000) {
                return '₹' + (value / 10000000).toFixed(1) + 'Cr';
              } else if (value >= 100000) {
                return '₹' + (value / 100000).toFixed(1) + 'L';
              } else if (value >= 1000) {
                return '₹' + (value / 1000).toFixed(0) + 'k';
              }
              return '₹' + value;
            }
          }
        }
      }
    }
  });
}

function initOccupancyChart(canvasId, ownerCount, tenantCount, vacantCount) {
  const canvas = typeof canvasId === 'string' ? document.getElementById(canvasId) : canvasId;
  if (!canvas) return;

  if (canvas._chartInstance) {
    canvas._chartInstance.destroy();
  }

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#94a3b8' : '#64748b';

  const o = parseInt(ownerCount !== undefined ? ownerCount : canvas.getAttribute('data-owner'), 10) || 0;
  const t = parseInt(tenantCount !== undefined ? tenantCount : (canvas.getAttribute('data-tenant') || canvas.getAttribute('data-rented')), 10) || 0;
  const v = parseInt(vacantCount !== undefined ? vacantCount : canvas.getAttribute('data-vacant'), 10) || 0;
  const total = o + t + v;

  const dataValues = total > 0 ? [o, t, v] : [0, 0, 1];
  const bgColors = total > 0 
    ? ['#10b981', '#6366f1', '#64748b'] 
    : ['#e2e8f0', '#e2e8f0', '#cbd5e1'];

  canvas._chartInstance = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: ['Owner Occupied', 'Tenant Leased', 'Vacant'],
      datasets: [{
        data: dataValues,
        backgroundColor: bgColors,
        borderWidth: 2,
        borderColor: isDark ? '#1e293b' : '#ffffff',
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.96)',
          titleColor: isDark ? '#f8fafc' : '#0f172a',
          bodyColor: isDark ? '#cbd5e1' : '#334155',
          borderColor: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: function(context) {
              if (total === 0) return ' No flats registered in society';
              const val = context.parsed;
              const pct = ((val / total) * 100).toFixed(1);
              return ` ${context.label}: ${val} Flats (${pct}%)`;
            }
          }
        }
      },
      cutout: '72%'
    }
  });
}

// Auto-initialize charts on DOM load if present
document.addEventListener('DOMContentLoaded', () => {
  const occCanvas = document.getElementById('occupancyChart');
  if (occCanvas) {
    initOccupancyChart(occCanvas);
  }

  // Re-render charts on theme toggle to match dark/light theme palette
  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      setTimeout(() => {
        if (occCanvas) initOccupancyChart(occCanvas);
        const cashCanvas = document.getElementById('cashflowChart');
        if (cashCanvas && window._lastCashflowData) {
          initFinanceChart(
            cashCanvas,
            window._lastCashflowData.revenue,
            window._lastCashflowData.expenses,
            window._lastCashflowData.labels
          );
        }
      }, 50);
    });
  }
});

