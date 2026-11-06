# Product Catalogue Ranked Search 🔍⚡

> A high-precision, multi-tenant B2B ranking microservice and catalog intelligence engine. Evaluates products across user-weighted multi-criteria dimensions, normalizes continuous and discrete metrics, enforces mathematical 100% weight allocation rules, and interleaves date-capped sponsored placements under anti-bias policies.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask_3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-D71F00?style=flat-square)](https://www.sqlalchemy.org/)
[![Pytest](https://img.shields.io/badge/Testing-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org/)
[![Architecture](https://img.shields.io/badge/Microservice-Port_5000-059669?style=flat-square)](#architecture--port-mapping)

---

## 🌟 Key Capabilities

* **Dynamic Multi-Criteria Attribute Modeling:**
  * Define category-specific scoring criteria per product domain.
  * Supports continuous numeric metrics (e.g., Battery Life, Price, Rating) and discrete binary metrics (e.g., Active Noise Cancelling on a 0.0/1.0 scale).
  * Flexible metric directionality (`lower_is_better` for cost/latency metrics like Price).

* **Strict 100% Weight Allocation:**
  * Enforces category weights summing strictly to **100.0%**.
  * Real-time validation indicator API with sub-300ms response time and client-side interactive weight sliders.

* **Deterministic Min-Max Normalization & Scoring:**
  * Mathematical Min-Max normalization mapping raw values into a unified $[0.0, 1.0]$ utility space:
    $$\text{Score}_{\text{benefit}} = \frac{x - \min}{\max - \min}, \quad \text{Score}_{\text{cost}} = \frac{\max - x}{\max - \min}$$
  * Multi-tier deterministic tie-breaking for fair, predictable rankings:
    `Composite Score DESC` &rarr; `Creation Date DESC` &rarr; `Product ID ASC`.

* **Anti-Bias Sponsored Placement Override:**
  * Date-scheduled sponsored promotions interleaved at fixed 1:5 intervals (slots 1, 6, 11) with a strict 20% placement cap.
  * Preserves raw organic composite scores without score distortion.

* **Multi-Tenant Architecture & Data Isolation:**
  * Complete data isolation across tenant companies with role-based access control.
  * Superadmin Platform Console for tenant provisioning, manager account creation, cascade deletion, and live inspection auditing.

* **B2B REST API Microservice:**
  * External RESTful JSON API endpoints (`/api/v1/search`, `/api/v1/categories`, `/api/v1/product/<id>`) allowing e-commerce storefronts to execute live ranked queries, dynamically inject customer preference weights, and retrieve full score contribution telemetry.

---

## 🏗️ Architecture & Port Mapping

```
+-------------------------------------------------------------+
|               Noise E-Commerce Storefront                   |
|                   (Client on Port 8000)                     |
+-------------------------------------------------------------+
                              │
                    REST API (JSON over HTTP)
                              ▼
+-------------------------------------------------------------+
|            Product-Catalogue-Ranked-Search Engine           |
|                 (Microservice on Port 5000)                 |
|                                                             |
|  [ Auth & Tenants ]     [ Criteria / Weights ]   [ Math ]   |
|  - Login / Session      - Attribute Modeling     - Min-Max  |
|  - Tenant Isolation     - 100% Weight Sum API    - Ranking  |
|                                                             |
|  [ Sponsored Engine ]   [ Search Analytics ]     [ Admin ]  |
|  - 1:5 Interleaving     - Top Query Counters     - Console  |
|  - 20% Placement Cap    - Sensitivity Analysis   - Auditing |
+-------------------------------------------------------------+
                              │
                              ▼
                SQLite Database (ranking_engine.db)
```

---

## 📁 Repository Structure

```text
Product-Catalogue-Ranked-Search/
├── app/
│   ├── __init__.py            # Flask app factory, extension initialization
│   ├── models.py              # Declarative models: Company, User, Category, Attribute, Product
│   ├── admin/                 # Platform administration blueprint
│   │   ├── forms.py           # Forms for company, category, and attribute management
│   │   └── routes.py          # Category/attribute CRUD, tenant switcher, user admin
│   ├── api/                   # External B2B REST API & Weight Validation
│   │   └── routes.py          # /api/v1/search, /api/category/<id>/weight-total
│   ├── auth/                  # Authentication & session blueprint
│   │   ├── forms.py           # LoginForm & authentication validation
│   │   └── routes.py          # Login, logout, session management
│   ├── ranking/               # Mathematical normalization & ranking engine
│   │   ├── engine.py          # Normalization math, composite scoring, tie-breaking
│   │   └── helpers.py         # Sponsored interleaving, validation helpers
│   ├── insights/              # Search intelligence & analytics dashboard
│   │   └── routes.py          # Query hit counters, distribution, weight sensitivity
│   ├── static/                # CSS design system & JavaScript widgets
│   │   ├── css/style.css      # Dark-cyan technical minimalist design tokens
│   │   └── js/weight_check.js # Real-time 100% weight meter widget
│   └── templates/             # Jinja2 template hierarchy
│       ├── base.html          # Shell layout & top navigation
│       ├── admin/             # Platform admin & category hub views
│       ├── auth/              # Login & registration views
│       └── insights/          # Insights search simulator & analytics views
├── docs/                      # Technical manuals & API specifications
│   ├── api_reference.md       # Full OpenAPI-compliant REST specification
│   └── setup_guide.md         # Comprehensive setup & configuration guide
├── tests/                     # Automated test suites
│   ├── conftest.py            # Pytest test fixtures & mock client
│   ├── test_models.py         # Model & weight sum validation unit tests
│   ├── test_engine.py         # Normalization math & tie-breaking test suite
│   ├── test_routes.py         # Route integration & role authorization tests
│   ├── test_api.py            # REST API search & ranking contract tests
│   ├── test_sponsor.py        # Sponsored placement capping & date tests
│   └── test_edge_cases.py     # Zero weight, empty catalog, and boundary tests
├── config.py                  # Environment configuration classes
├── requirements.txt           # Python package dependencies
├── run.py                     # Entry point (Port 5000)
└── seed.py                    # Multi-tenant demo dataset seeder
```

---

## 🚀 Quick Start & Setup

### 1. Prerequisites
* Python 3.10 or higher
* Git

### 2. Clone & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/BlueDragon320/Product-Catalogue-Ranked-Search.git
cd Product-Catalogue-Ranked-Search

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate       # On Linux / macOS
# .\venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Microservice
```bash
python run.py
```
The service will start at **`http://127.0.0.1:5000/`**.

---

## 🧪 Running Automated Tests

Run the complete test suite with verbose reporting:

```bash
pytest -v
```

To run a specific module:
```bash
pytest tests/test_engine.py -v     # Normalization & scoring math
pytest tests/test_models.py -v     # Weight validation & models
pytest tests/test_api.py -v        # B2B REST Search API endpoints
```

---

## 📡 Key REST API Endpoints

| Method | Endpoint | Description |
| :---: | :--- | :--- |
| `GET` | `/api/v1/categories` | Retrieve all active categories with defined attributes |
| `POST` | `/api/v1/search` | Execute multi-criteria ranked search with dynamic weights |
| `GET` | `/api/v1/product/<id>` | Fetch detailed product metadata and normalized score breakdown |
| `GET` | `/api/category/<id>/weight-total` | Return current sum of active weights for a category |
| `POST` | `/api/category/<id>/weight-validate` | Validate whether proposed weights sum to 100.0% |

---

## 👥 Authors & Collaborators

* **Vaibhav Patil** (`01fe24bca300`) — System Architecture, Scoring Engine, REST APIs & Admin Workflows
* **Shrinivas** (`01fe24bca311`) — Weight Validation, UI Design Tokens, Edge-Case Hardening & Docs
