/**
 * SmartSociety 360 - Chart.js Visualizations
 */

function initFinanceChart(canvasId, incomeData, expenseData, labels) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels || ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
      datasets: [
        {
          label: 'Maintenance Collected (₹)',
          data: incomeData || [145000, 162000, 158000, 175000, 182000, 195000],
          backgroundColor: 'rgba(16, 185, 129, 0.8)',
          borderRadius: 6,
        },
        {
          label: 'Society Operating Expenses (₹)',
          data: expenseData || [110000, 125000, 140000, 130000, 150000, 142000],
          backgroundColor: 'rgba(244, 63, 94, 0.8)',
          borderRadius: 6,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#9ca3af' }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#9ca3af' }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#9ca3af' }
        }
      }
    }
  });
}

function initOccupancyChart(canvasId, occupiedCount, vacantCount, tenantCount) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Owner Occupied', 'Tenant Occupied', 'Vacant'],
      datasets: [{
        data: [occupiedCount || 18, tenantCount || 8, vacantCount || 4],
        backgroundColor: [
          '#6366f1',
          '#06b6d4',
          '#374151'
        ],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            color: '#9ca3af'
          }
        }
      },
      cutout: '70%'
    }
  });
}
