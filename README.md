# **Welcome to my multi-tier Expense Tracker repository!**

This project showcases my journey from building low-level system tools to engineering production-ready, decoupled full-stack cloud applications.

## **Project 1: 💸 TallyDan — Full-Stack Expense Tracker**

> A robust, production-ready full-stack expense tracking and financial management web application built for seamless budgeting, data persistence, and secure user authentication.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://tallydan-expense-tracker.vercel.app)
[![Backend Status](<https://img.shields.io/badge/backend-django%20rest-blue>)](https://expense-tracker-api-n5s7.onrender.com)
[![Frontend Status](<https://img.shields.io/badge/frontend-vite%20%2B%20react-orange>)](https://vercel.com)

---

## 🚀 Live Demo

* **Frontend Application:** [https://tallydan-expense-tracker.vercel.app](https://tallydan-expense-tracker.vercel.app)
* **Backend API Documentation / Health:** [https://expense-tracker-api-n5s7.onrender.com](https://expense-tracker-api-n5s7.onrender.com)

---

## 🏛️ System Architecture

TallyDan follows a **decoupled client-server architecture**:

* **Frontend:** A single-page application (SPA) built with **React and Vite**, styled for responsive mobile and desktop use, deployed globally via **Vercel**.
* **Backend:** A RESTful API built with **Django REST Framework (DRF)** handling business logic, user sessions, and database operations, hosted on **Render**.
* **Database & Security:** Relational data management secured with environment-driven CORS policies and token-based authentication.

```text
+-------------+      HTTPS / REST API       +------------------------+
|   React     |  -------------------------> |      Django DRF        |
|  (Vite SPA) | <-------------------------  |     (Render Server)    |
|   Vercel    |      JSON Payloads          +------------------------+
+-------------+                                          |
+------------------------+
| Relational DB / SQLite |
+------------------------+
```

## 🧰 Tech Stack

### **Frontend**

* **React / Vite** – Fast component-based UI development and lightning-fast bundling.
* **Tailwind CSS / Modern CSS** – Clean, modern, and responsive interface design.
* **Vercel CLI** – Serverless frontend deployment pipeline.

### **Backend**

* **Python / Django** – Secure and scalable high-level Python web framework.
* **Django REST Framework (DRF)** – Powerful toolkit for building robust Web APIs.
* **Django CORS Headers** – Secure cross-origin resource sharing configuration between Vercel and Render.
* **Render** – Cloud platform for scalable web services and backend hosting.

---

## ✨ Core Features

* **User Authentication:** Secure user registration, login, and session persistence.
* **Expense Management:** Add, categorize, edit, and delete daily personal expenses.
* **Financial Insights:** Track spending metrics and budgets dynamically.
* **Responsive Design:** Optimized for seamless usage across mobile, tablet, and desktop viewports.

---

## 🛠️ Local Development Setup

To run TallyDan locally on your machine:

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/expense_tracker.git](https://github.com/your-username/expense_tracker.git)
cd expense_tracker
```

#### 2. Set Up the Backend

```Shell
cd backend
python -m venv .venv
# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### 3. Set Up the Frontend

   Open a separate terminal window:

```Shell
cd frontend
npm install
npm run dev
```

## **Project 2: Expense Tracker CLI**

A local command-line expense tracker built with Python. The project is the
stabilized foundation of Roadmap Phase 1: business rules are separated from
terminal presentation and JSON persistence so later Django work can reuse the
domain behavior instead of rewriting it.

## Current capabilities

* Add, edit, duplicate, inspect, search, filter, sort, and delete expenses.
* Set category budgets and view monthly budget status.
* Generate monthly, statistical, category, and top-category reports.
* Import and export currency-aware CSV data.
* Configure one application currency; the initial default is `USD`.
* Store exact two-decimal monetary values, stable expense UUIDs, occurrence
  dates, and UTC creation timestamps in versioned JSON documents.
* Protect local data with validation, atomic replacement, backups, and recovery.
* Run through explicit application composition and repository contracts.

## Requirements

* Python 3.11, 3.12, 3.13, or 3.14
* A terminal such as PowerShell

The Phase 1 CLI uses only the Python standard library at runtime. Test,
coverage, and formatting tools are installed separately from
`requirements-dev.txt`.

## Quick start

```powershell
git clone <repository-url>
cd expense_tracker
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.main
```

The default data and export directories are `data/` and `exports/`. Runtime
JSON, backup, CSV, environment, coverage, and cache files are ignored by Git.

For an isolated manual run:

```powershell
$env:EXPENSE_TRACKER_DATA_DIR = "tmp/manual-data"
$env:EXPENSE_TRACKER_EXPORT_DIR = "tmp/manual-exports"
$env:EXPENSE_TRACKER_DEFAULT_CURRENCY = "KMF"
python -m src.main
```

The default currency is used only when settings do not yet exist. After the
first run, the persisted setting is authoritative. Currency can be changed in
the CLI only while no expenses or budgets exist.

See [QUICK_START.md](QUICK_START.md) for the complete setup and verification
workflow.

## Main menu

```text
1. Expense Management
2. Budget Management
3. Reports
4. Export
5. Settings (Currency: USD)
0. Exit
```

The Export section contains both expense import and export workflows. The
detailed menu map is maintained in [PROJECT_INDEX.md](PROJECT_INDEX.md).

## Development checks

Install the development dependencies, then run the same gates used by CI:

```powershell
python -m pip install -r requirements-dev.txt
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m compileall -q src tests
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=85 -q
```

GitHub Actions runs static checks on Python 3.14 and the test suite on every
supported Python version. Details are in
[docs/QUALITY_AUTOMATION.md](docs/QUALITY_AUTOMATION.md).

## Architecture

The dependency direction is:

```text
CLI -> application services -> repository protocols <- JSON storage
                    |
                    v
             domain validation
```

`src/application.py` is the composition root. Services do not construct JSON
storage, and `src/main.py` remains a thin executable entry point. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[STRUCTURE.md](STRUCTURE.md).

## Data safety

Version 2 JSON uses decimal strings rather than binary floats. Existing valid
documents are backed up before replacement, and corrupt primary documents are
restored only from backups that pass the same validation. Never edit or delete
the primary and `.bak` files without first making an external copy.

See [docs/DATA_SCHEMA.md](docs/DATA_SCHEMA.md) and
[docs/PERSISTENCE_RELIABILITY.md](docs/PERSISTENCE_RELIABILITY.md).

## Roadmap status

Roadmap Phase 1 is complete and published as `v1.0.0`. All seven stabilization
milestones passed their release gates. No HTTP API, Django application,
database, authentication, multi-user system, or AI/ML feature is implemented
in this release.

The authoritative status is
[docs/PHASE_1_UPGRADE_ROADMAP.md](docs/PHASE_1_UPGRADE_ROADMAP.md). The future
Django mapping is design guidance, not implemented code:
[docs/DJANGO_MIGRATION_READINESS.md](docs/DJANGO_MIGRATION_READINESS.md).

## Documentation

Use [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) as the canonical document
map. Historical completion reports that contradicted the current roadmap were
removed; Git history remains the source for those past snapshots.

## License

See [LICENSE](LICENSE).
