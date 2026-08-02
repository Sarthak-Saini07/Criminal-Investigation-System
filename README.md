# Criminal Investigation and Case Management System (CICMS)

CICMS is an enterprise-grade desktop software application designed for law enforcement agencies to manage criminal investigations end-to-end—from complaint registration and FIR filing to suspect tracking, evidence chain-of-custody logging, forensic reports, and court verdicts.

---

## 🏛️ System Architecture

```
CICMS Desktop Application (Python 3.12 + Tkinter TTK)
 ├── User Authentication & RBAC (Admin, Officer, Investigator, Supervisor, Analyst)
 ├── FIR & Case Management Engine
 ├── Suspect & Criminal History Registry
 ├── Evidence Vault & Chain of Custody System
 ├── Investigation & Forensic Module
 ├── Court Proceedings & Chargesheet Registry
 ├── Analytics Engine (Pandas + NumPy OLS Linear Regression Model)
 ├── Matplotlib Visualization Dashboard
 ├── Report Exporter (OpenPyXL Excel, CSV, ReportLab PDF)
 └── Database Manager (MySQL 8.0+ with Automatic SQLite Fallback)
```

---

## 🗄️ Database Requirements & Features

The system relies on a fully normalized relational database (18+ tables):

- **Core Tables**: `police_stations`, `departments`, `officers`, `user_logins`, `crime_categories`, `complaints`, `firs`, `cases`, `case_assignments`, `case_status_history`, `suspects`, `criminal_histories`, `victims`, `witnesses`, `evidence`, `evidence_chains`, `forensic_reports`, `interrogations`, `arrests`, `judges`, `lawyers`, `chargesheets`, `court_cases`, `hearings`, `audit_logs`.
- **Advanced Features**:
  - Primary & Foreign Keys with CASCADE/SET NULL constraints.
  - CHECK constraints for status validation.
  - SQL Views (`vw_case_summary`, `vw_officer_workload`, `vw_crime_analytics_summary`).
  - SQL Stored Procedures (`sp_register_fir`, `sp_transfer_case`).
  - SQL Triggers (`trg_after_case_status_update`, `trg_after_evidence_insert`).
  - CTEs, Window Functions (`RANK() OVER (...)`), Correlated Subqueries, `GROUP BY ... HAVING`.

---

## 📊 Analytics & Crime Prediction Model

- **NumPy Statistical Engine**: Mean, Median, Variance, Standard Deviation, 25th/75th Percentiles, Normalization, Moving Averages.
- **Pure NumPy OLS Linear Regression ($Y = X\beta$)**:
  - Closed-form solution: $\beta = (X^T X)^{-1} X^T y$
  - Forecasts future quarterly crime trends without relying on any machine learning frameworks (e.g. Scikit-learn).

---

## 🔐 Role-Based Access Control (RBAC) & Accounts

| Username | Password | Role | Permissions |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | **Admin** | Full system access, User management, Backup trigger |
| `officer` | `officer123` | **Police Officer** | Register FIRs, Deposit evidence, Add suspects |
| `investigator`| `investigator123`| **Investigation Officer**| Update case status, Reassign lead officer, Notes |
| `supervisor` | `supervisor123` | **Supervisor** | Approve case transfers, High-level analytics |
| `analyst` | `analyst123` | **Read-only Analyst**| View dashboard, Export Excel/PDF reports |

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.12+
- MySQL Server 8.0+ (Optional: System includes SQLite auto-fallback)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python main.py
```
*(On initial launch, `sql/seed_data.py` auto-populates the database with 2,000+ realistic records).*

---

## 📁 Project Directory Structure

```
project/
├── config/
│   └── config.ini
├── database/
│   ├── connection.py
│   ├── queries.py
│   └── models.py
├── analytics/
│   ├── cleaning.py
│   ├── preprocessing.py
│   ├── kpi.py
│   └── statistics.py
├── dashboard/
│   ├── dashboard.py
│   └── charts.py
├── reports/
│   ├── excel_report.py
│   ├── csv_report.py
│   └── pdf_summary.py
├── utils/
│   ├── logger.py
│   ├── helpers.py
│   └── validation.py
├── ui/
│   ├── login_frame.py
│   ├── main_window.py
│   ├── fir_view.py
│   ├── case_view.py
│   ├── suspect_view.py
│   ├── victim_view.py
│   ├── witness_view.py
│   ├── evidence_view.py
│   ├── investigation_view.py
│   ├── court_view.py
│   ├── analytics_view.py
│   ├── reports_view.py
│   └── audit_view.py
├── logs/
├── sql/
│   ├── schema.sql
│   ├── views.sql
│   ├── procedures.sql
│   ├── triggers.sql
│   └── seed_data.py
├── main.py
├── requirements.txt
└── README.md
```
# Criminal-Investigation-System
