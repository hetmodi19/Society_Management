/**
 * Emerald Greens Residences & Towers - Luxury Building Website Interactive Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  initMaintenanceEstimator();
  initResidenceTabs();
  initAmenityFilters();
  initFAQAccordion();
  initMobileNav();
  initNoticeModal();
  initInquiryModal();
  initQuickPassSimulator();
});

// --- 1. Maintenance Dues & Living Cost Estimator ---
function initMaintenanceEstimator() {
  const slider = document.getElementById('calcCarpetSlider');
  const sliderDisplay = document.getElementById('calcCarpetDisplay');
  const towerSelect = document.getElementById('calcTowerSelect');
  const parkingCheck = document.getElementById('calcParkingCheck');
  const evCheck = document.getElementById('calcEvCheck');
  const clubCheck = document.getElementById('calcClubCheck');

  const totalDisplay = document.getElementById('calcTotalOutput');
  const baseDisplay = document.getElementById('calcBaseOutput');
  const sinkingDisplay = document.getElementById('calcSinkingOutput');
  const addOnsDisplay = document.getElementById('calcAddonsOutput');

  if (!slider || !totalDisplay) return;

  function calculateDues() {
    const area = parseInt(slider.value, 10) || 1500;
    if (sliderDisplay) sliderDisplay.textContent = `${area.toLocaleString()} sq.ft`;

    // Base rate per sq ft (Tower A Sky Villa = 5.2, Tower B = 4.5)
    let ratePerSqFt = 4.8;
    if (towerSelect && towerSelect.value === 'tower_a') {
      ratePerSqFt = 5.5;
    } else if (towerSelect && towerSelect.value === 'penthouse') {
      ratePerSqFt = 6.2;
    }

    const baseAmount = Math.round(area * ratePerSqFt);
    const sinkingFund = Math.round(baseAmount * 0.10); // 10% reserve

    let addOns = 0;
    if (parkingCheck && parkingCheck.checked) addOns += 1200;
    if (evCheck && evCheck.checked) addOns += 1800;
    if (clubCheck && clubCheck.checked) addOns += 1500;

    const grandTotal = baseAmount + sinkingFund + addOns;

    totalDisplay.textContent = `₹${grandTotal.toLocaleString()}`;
    if (baseDisplay) baseDisplay.textContent = `₹${baseAmount.toLocaleString()}`;
    if (sinkingDisplay) sinkingDisplay.textContent = `₹${sinkingFund.toLocaleString()}`;
    if (addOnsDisplay) addOnsDisplay.textContent = `₹${addOns.toLocaleString()}`;
  }

  slider.addEventListener('input', calculateDues);
  if (towerSelect) towerSelect.addEventListener('change', calculateDues);
  if (parkingCheck) parkingCheck.addEventListener('change', calculateDues);
  if (evCheck) evCheck.addEventListener('change', calculateDues);
  if (clubCheck) clubCheck.addEventListener('change', calculateDues);

  // Initial calculation
  calculateDues();
}

// --- 2. Residence Showcase Filter Tabs ---
function initResidenceTabs() {
  const tabs = document.querySelectorAll('.residence-tab-btn');
  const cards = document.querySelectorAll('.residence-card');

  if (!tabs.length || !cards.length) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const category = tab.getAttribute('data-residence-filter');

      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      cards.forEach(card => {
        const type = card.getAttribute('data-type');
        if (category === 'all' || type === category) {
          card.style.display = 'flex';
          card.style.animation = 'fadeInCard 0.4s ease forwards';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

// --- 3. Amenity Filter Pills ---
function initAmenityFilters() {
  const pills = document.querySelectorAll('.amenity-filter-pill');
  const cards = document.querySelectorAll('.amenity-lux-card');

  if (!pills.length || !cards.length) return;

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      const cat = pill.getAttribute('data-amenity-cat');

      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');

      cards.forEach(card => {
        const cardCat = card.getAttribute('data-category');
        if (cat === 'all' || cardCat === cat) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

// --- 4. Interactive FAQ Accordion ---
function initFAQAccordion() {
  const items = document.querySelectorAll('.faq-accordion-item');

  items.forEach(item => {
    const header = item.querySelector('.faq-accordion-header');
    if (header) {
      header.addEventListener('click', () => {
        const isOpen = item.classList.contains('open');

        // Close all others
        items.forEach(i => i.classList.remove('open'));

        if (!isOpen) {
          item.classList.add('open');
        }
      });
    }
  });
}

// --- 5. Mobile Navbar Drawer ---
function initMobileNav() {
  const toggleBtn = document.getElementById('luxMobileNavToggle');
  const drawer = document.getElementById('luxMobileDrawer');
  const closeBtn = document.getElementById('luxMobileDrawerClose');

  if (toggleBtn && drawer) {
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      drawer.classList.add('show');
      document.body.style.overflow = 'hidden'; // Prevent background scrolling
    });
  }

  function closeDrawer() {
    if (drawer) {
      drawer.classList.remove('show');
      document.body.style.overflow = '';
    }
  }

  if (closeBtn && drawer) {
    closeBtn.addEventListener('click', closeDrawer);
  }

  if (drawer) {
    drawer.addEventListener('click', (e) => {
      if (e.target === drawer) {
        closeDrawer();
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawer && drawer.classList.contains('show')) {
      closeDrawer();
    }
  });
}

// --- 6. Notice Details Modal ---
function initNoticeModal() {
  const openBtns = document.querySelectorAll('[data-notice-modal]');
  const modal = document.getElementById('luxNoticeModal');
  const titleEl = document.getElementById('noticeModalTitle');
  const bodyEl = document.getElementById('noticeModalBody');
  const dateEl = document.getElementById('noticeModalDate');

  if (!modal) return;

  openBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const title = btn.getAttribute('data-notice-title') || 'Society Notice';
      const body = btn.getAttribute('data-notice-body') || 'No description provided.';
      const date = btn.getAttribute('data-notice-date') || '';

      if (titleEl) titleEl.textContent = title;
      if (bodyEl) bodyEl.textContent = body;
      if (dateEl) dateEl.textContent = date;

      modal.classList.add('show');
    });
  });
}

// --- 7. Tour / Inquire Modal ---
function initInquiryModal() {
  const tourForm = document.getElementById('luxTourForm');
  if (tourForm) {
    tourForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const modal = document.getElementById('tourModal');
      if (modal) modal.classList.remove('show');

      if (typeof showToast === 'function') {
        showToast('Thank you! Our Resident Relations & Concierge desk will contact you shortly.');
      } else {
        alert('Thank you! Our Resident Relations & Concierge desk will contact you shortly.');
      }
      tourForm.reset();
    });
  }
}

// --- 8. Quick Visitor Pass Simulator & QR Generator ---
function initQuickPassSimulator() {
  const triggerBtn = document.getElementById('triggerPassSimulator');
  const modal = document.getElementById('passSimulatorModal');
  const codeDisplay = document.getElementById('simulatedPassCode');
  const copyBtn = document.getElementById('copySimulatedPass');

  if (triggerBtn && modal) {
    triggerBtn.addEventListener('click', () => {
      const randomCode = Math.floor(100000 + Math.random() * 900000);
      if (codeDisplay) codeDisplay.textContent = randomCode;
      modal.classList.add('show');
    });
  }

  if (copyBtn && codeDisplay) {
    copyBtn.addEventListener('click', () => {
      const code = codeDisplay.textContent;
      const shareText = `*Emerald Greens CHS Ltd. - Gate Access Pass*\nFlat: A-1204 (Tower A • Horizon Wing)\nOTP Passcode: ${code}\nValid: 4 Hours\nPresent this OTP at Gate 1 / Gate 2 terminal for swift boom barrier clearance.`;
      if (typeof copyToClipboard === 'function') {
        copyToClipboard(shareText, 'Guest Pass copied to clipboard! Share on WhatsApp.');
      } else {
        navigator.clipboard.writeText(shareText);
        alert('Guest Pass copied to clipboard! Share on WhatsApp.');
      }
    });
  }
}
