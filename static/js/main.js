/**
 * SmartSociety 360 - Main Javascript Core & Quick Actions
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSidebar();
  initDropdowns();
  initTabs();
  initModals();
  initAlerts();
  initCommandPalette();
  initPasswordToggles();
  initPasswordStrengthMeter();
});

// --- Theme Management ---
function initTheme() {
  const savedTheme = localStorage.getItem('smartsociety_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  const toggleBtn = document.getElementById('themeToggleBtn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('smartsociety_theme', next);
      updateThemeIcon(next);
    });
  }
}

function updateThemeIcon(theme) {
  const icon = document.getElementById('themeToggleIcon');
  if (icon) {
    icon.textContent = theme === 'dark' ? '☀️' : '🌙';
  }
}

// --- Mobile Sidebar Drawer ---
function initSidebar() {
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const sidebar = document.getElementById('appSidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('show');
    });
  }

  if (overlay) {
    overlay.addEventListener('click', () => {
      if (sidebar) sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }
}

// --- Dropdowns (Demo Role Switcher, Profile Menu) ---
function initDropdowns() {
  const demoBtn = document.getElementById('demoSwitcherBtn');
  const demoMenu = document.getElementById('demoSwitcherMenu');

  if (demoBtn && demoMenu) {
    demoBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      demoMenu.classList.toggle('show');
    });

    document.addEventListener('click', () => {
      demoMenu.classList.remove('show');
    });
  }
}

// --- Tabs Navigation ---
function initTabs() {
  const tabContainers = document.querySelectorAll('.tabs-container');
  tabContainers.forEach(container => {
    const buttons = container.querySelectorAll('.tab-btn');
    const panes = container.querySelectorAll('.tab-pane');

    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-tab');

        buttons.forEach(b => b.classList.remove('active'));
        panes.forEach(p => p.style.display = 'none');

        btn.classList.add('active');
        const activePane = container.querySelector(`#${target}`);
        if (activePane) activePane.style.display = 'block';
      });
    });
  });
}

// --- Modals ---
function initModals() {
  const openButtons = document.querySelectorAll('[data-modal-target]');
  const closeButtons = document.querySelectorAll('[data-modal-close]');

  openButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.getAttribute('data-modal-target');
      const modal = document.getElementById(modalId);
      if (modal) modal.classList.add('show');
    });
  });

  closeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-backdrop');
      if (modal) modal.classList.remove('show');
    });
  });

  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('show');
      }
    });
  });
}

// --- Global Command Palette (Ctrl+K / Cmd+K) ---
function initCommandPalette() {
  const modal = document.getElementById('commandPaletteModal');
  const input = document.getElementById('commandSearchInput');
  const items = document.querySelectorAll('.command-item');

  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      if (modal) {
        modal.classList.toggle('show');
        if (modal.classList.contains('show') && input) {
          setTimeout(() => input.focus(), 100);
        }
      }
    }
    if (e.key === 'Escape' && modal && modal.classList.contains('show')) {
      modal.classList.remove('show');
    }
  });

  if (input) {
    input.addEventListener('input', () => {
      const q = input.value.toLowerCase().trim();
      items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(q) ? 'flex' : 'none';
      });
    });
  }
}

// --- Password Visibility Toggles ---
function initPasswordToggles() {
  document.querySelectorAll('.password-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input = targetId ? document.getElementById(targetId) : btn.previousElementSibling;
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          btn.textContent = '👁️';
        } else {
          input.type = 'password';
          btn.textContent = '🔒';
        }
      }
    });
  });
}

// --- Password Strength Meter ---
function initPasswordStrengthMeter() {
  const pwdInput = document.getElementById('registerPasswordInput');
  const seg1 = document.getElementById('pwdSeg1');
  const seg2 = document.getElementById('pwdSeg2');
  const seg3 = document.getElementById('pwdSeg3');
  const textHint = document.getElementById('pwdStrengthText');

  if (pwdInput && seg1 && seg2 && seg3) {
    pwdInput.addEventListener('input', () => {
      const val = pwdInput.value;
      let score = 0;
      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val) && /[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;

      seg1.className = 'strength-segment';
      seg2.className = 'strength-segment';
      seg3.className = 'strength-segment';

      if (val.length === 0) {
        if (textHint) textHint.textContent = 'Enter a strong password';
      } else if (score === 1) {
        seg1.classList.add('active-weak');
        if (textHint) textHint.textContent = 'Weak password';
      } else if (score === 2) {
        seg1.classList.add('active-medium');
        seg2.classList.add('active-medium');
        if (textHint) textHint.textContent = 'Medium password';
      } else {
        seg1.classList.add('active-strong');
        seg2.classList.add('active-strong');
        seg3.classList.add('active-strong');
        if (textHint) textHint.textContent = 'Strong password ✓';
      }
    });
  }
}

// --- Copy to Clipboard with Toast ---
function copyToClipboard(text, label = 'Copied to clipboard!') {
  navigator.clipboard.writeText(text).then(() => {
    showToast(label);
  });
}

function showToast(message) {
  const existing = document.querySelector('.copy-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'copy-toast';
  toast.textContent = `✓ ${message}`;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

// --- Auto-Dismiss Flash Alerts ---
function initAlerts() {
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });
}

// --- Print Utility ---
function printInvoice() {
  window.print();
}
