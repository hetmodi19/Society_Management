# 🏢 SmartSociety 360 — Next-Gen Housing Society ERP & Gatekeeper System

**SmartSociety 360** is a fullstack, production-grade Housing Society & Residential Community Management System built with Python & Django. It solves everyday residential pain points — from automated carpet-area maintenance billing and instant UPI payments, to 6-digit visitor gate passes, amenity slot bookings, maintenance helpdesk ticketing, and democratic community polls.

---

## 🌟 Key Capabilities & Features

### 1. 🛡️ Digital Gatekeeper & Security Desk
- **6-Digit Pre-Approved OTP Passes:** Residents generate instant entry PINs & QR codes for friends and service providers.
- **Daily Helper Passcodes:** Maids, cooks, and drivers check-in with 4-digit codes.
- **Visitor Logs & Parcel Lockers:** Real-time in-premises visitor tracking and courier locker management.
- **Emergency SOS Alarm:** Broadcast panic alarms (Medical, Fire, Intruder) directly to the gate terminal and admin dashboard.

### 2. 💳 Smart Maintenance Invoicing & Financial Ledger
- **Formula-Driven Billing:** Automated monthly bill calculation based on carpet area (sqft), sinking fund, water charges, and parking slot allocations.
- **Interactive Online Checkout:** Simulated payment options with UPI QR codes, Credit/Debit cards, and NetBanking.
- **Printable Tax Invoices & Receipts:** Downloadable/printable official receipts with unique transaction IDs and digital seals.
- **Society Audited Balance Sheet:** Track income vs operational expenses (power, security agency, lift AMC, repairs) with visual Chart.js analytics.

### 3. 🏊 Clubhouse & Facility Booking System
- **Real-Time Booking Calendar:** Reserve Banquet Halls, Olympic Infinity Pools, Gyms, and Tennis Courts.
- **Conflict Prevention Engine:** Prevents double-booking collisions with automated slot overlap detection.
- **Management Approval Workflow:** Optional committee review for private banquet party bookings.

### 4. 🔧 Maintenance Helpdesk & Complaint Tracking
- **Categorized Ticket Logging:** Plumbing, Electrical, Elevator, Pest Control, Common Area.
- **Technician Queue:** Assign facility staff, record resolution notes, and capture resident 5-star ratings.

### 5. 🗳️ Communications, Notices & Democratic Polls
- **Official Notice Board:** High-priority pinned circulars and AGM meeting notices.
- **1-Member-1-Vote Polls:** Democratic referendums with real-time percentage progress bars.
- **Community Forum:** Social feed and marketplace for neighbor discussions and buy/sell items.

### 6. 📱 Responsive UI/UX Design System
- **Glassmorphism:** Elegant dark & light theme toggle with smooth transitions.
- **Mobile First:** Responsive drawer sidebar and thumb-friendly bottom navigation dock for smartphones.
- **Interactive Data Charts:** Integrated Chart.js for financial health and occupancy trends.

---

## 🚀 Quick Start Guide

### 1. Clone & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/hetmodi19/Society_Management.git
cd Society_Management

# Install Python requirements
pip install -r requirements.txt
```

### 2. Apply Migrations & Seed Sample Data
```bash
# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Seed rich demonstration data (flats, bills, visitors, tickets, polls)
python manage.py seed_demo_data
```

### 3. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## ⚡ Instant Demo Accounts & Role Switcher

You can test any role instantly using the **"⚡ Switch Role"** topbar dropdown, or sign in manually with these pre-configured credentials:

| Role | Username / Email | Password | Access Highlights |
| :--- | :--- | :--- | :--- |
| **👑 Admin / President** | `admin` / `admin@emeraldgreens.residence` | `admin123` | Full analytics, ledger, batch billing, flat directory |
| **📜 Committee Member** | `secretary` / `secretary@emeraldgreens.residence` | `committee123` | Approvals, notices, expenses, directory |
| **🏠 Resident (Owner)** | `john_doe` / `john.doe@example.com` | `resident123` | Pay maintenance, generate visitor pass, book pool |
| **🏡 Resident (Tenant)** | `sarah_smith` / `sarah.smith@example.com` | `resident123` | View invoices, raise complaint, cast poll vote |
| **🛡️ Security Guard** | `guard_raj` / `security.raj@emeraldgreens.residence` | `guard123` | Live gatekeeper terminal, OTP PIN verification |
| **🔧 Facility Staff** | `mike_electrician` / `mike.tech@emeraldgreens.residence` | `staff123` | Maintenance task queue, update work |

---

## 🚢 Deployment Options

### Netlify Deployment
The repository includes `netlify.toml` for static / edge configurations. Run:
```bash
python manage.py collectstatic --noinput
```

### Vercel Serverless
Configured via `vercel.json` and WSGI serverless wrapper in `society_core/wsgi.py`.

### Render / Railway / Heroku
Includes `Procfile`, `render.yaml`, and `requirements.txt`.
```bash
web: gunicorn society_core.wsgi --log-file -
```

---

## 🧪 Running Automated Tests
```bash
python manage.py test
```

---

## 📄 License
This project is open-source under the MIT License.
