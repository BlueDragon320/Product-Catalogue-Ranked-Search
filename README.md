# Product Catalogue Ranked Search

A multi-tenant, high-precision ranking microservice and catalog intelligence engine. Evaluates products across user-weighted multi-criteria dimensions, normalizes continuous numeric and discrete binary metrics, enforces mathematical 100% weight allocation rules, and interleaves date-capped sponsored placements under anti-bias policies.

---

## Key Capabilities

- **Dynamic Multi-Criteria Attribute Modeling (FR-1, FR-2)**: Define custom attributes per domain category. Supports continuous `numeric` ranges and discrete `binary` criteria (Yes/No boolean evaluated on a 0.0/1.0 scale). Configurable metric directionality (`lower_is_better` for metrics like Price and Latency).
- **Strict 100% Weight Allocation (FR-3, NFR-5.1)**: Enforces category weights summing strictly to 100.0%. Provides real-time AJAX validation indicator with sub-300ms response time.
- **Deterministic Weighted Scoring & Tie-Breaking (FR-9, FR-10, FR-13)**: Min-Max normalization maps disparate attribute measurements to a unified [0.0, 1.0] scale. Three-tier deterministic tie-breaking resolves identical scores: `Composite Score DESC` &rarr; `Creation Date DESC` &rarr; `Product ID ASC`.
- **Anti-Bias Sponsored Placement Override (FR-14 – FR-17, NFR-5.6)**: Date-scheduled sponsored promotions interleaved at fixed 1:5 intervals (slots 1, 6, 11) with a strict 20.0% placement cap. Preserves raw organic composite scores without score distortion.
- **Attribute Range Filtering (FR-21)**: Pre-ranking filtering allowing users and client applications to specify attribute threshold bounds (`filter_attr_id`, `filter_min`, `filter_max`) to filter products before score computation and ranking.
- **Multi-Tenant Architecture & Platform Administration (FR-18, FR-19, FR-20)**: Complete data isolation across tenant companies. Platform Superadmin console enables company provisioning, cascade deletion, tenant inspection auditing, and direct tenant user password resets.
- **B2B REST API Microservice (FR-12, FR-19, FR-21)**: External RESTful JSON API (`/api/v1/search`, `/api/v1/categories`, `/api/v1/product/<id>`) allowing e-commerce storefronts and external platforms to execute searches, apply dynamic personalization weights, and retrieve full score contribution telemetry.
- **Catalog Intelligence & Search Analytics (FR-12, FR-20)**: Interactive query simulation, search frequency hit counters, category popularity distribution, attribute sensitivity analysis, and anti-bias compliance auditing.

---

## Tech Stack

- **Backend:** Python 3.10+, Flask
- **Database / ORM:** SQLAlchemy ORM with SQLite (Development/Test) and PostgreSQL compatibility
- **Authentication & Security:** Flask-Login, Werkzeug (salted password hashing, role-based access control)
- **Frontend / UI:** Technical Minimalist design system (Space Grotesk, General Sans, JetBrains Mono, crisp 1px borders, zero box-shadows)
- **Testing:** Pytest, coverage test suite

---

## Quick Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd weighted-ranking-engine
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database & seed demo dataset:**
   ```bash
   python seed.py
   ```
   *Seeds platform superadmin, tenant organizations, categories, attributes, products, and query analytics.*

5. **Run development server:**
   ```bash
   python run.py
   ```
   *The application starts at `http://127.0.0.1:5000/`.*

---

## Automated Test Suite

Run the full pytest suite:
```bash
pytest -v
```

---

## B2B REST API Overview

External client applications interact with the ranking microservice using standard HTTP requests:

- `GET /api/v1/search?company_id=<id>&q=<query>`: Free-text search and weighted product ranking.
- `POST /api/v1/search`: Query ranking with dynamic personalization weights payload and attribute range filters (`filter_attr_id`, `filter_min`, `filter_max`).
- `GET /api/v1/categories?company_id=<id>`: Retrieve tenant categories, active attributes, scales, and data types.
- `GET /api/v1/product/<product_id>?company_id=<id>`: Detailed product metrics and full score mathematical breakdown.
- `GET /api/weight-total/<category_id>`: Check active attribute weight summation for category calibration.

For complete API documentation, request parameters, and response schemas, see [docs/api_reference.md](docs/api_reference.md).

---

## Project Structure

```
weighted-ranking-engine/
├── app/
│   ├── admin/           # Platform superadmin & company hub blueprint
│   ├── api/             # B2B search REST API & weight validation endpoints
│   ├── auth/            # Authentication & role authorization blueprint
│   ├── insights/        # Catalog intelligence, analytics & search simulation
│   ├── ranking/         # Core engine: normalization, scoring & tie-break logic
│   ├── static/          # CSS design system (Technical Minimalist) & client JS
│   ├── templates/       # Jinja2 presentation templates
│   ├── models.py        # SQLAlchemy entities: Company, Category, Attribute, Product, User, SearchLog
│   └── __init__.py      # Flask application factory
├── docs/                # Setup and API reference documentation
├── tests/               # Pytest automated test suite
├── config.py            # Environment configuration (Dev, Test, Prod)
├── run.py               # Application entry point
├── seed.py              # Multi-tenant demo dataset generator
└── requirements.txt     # Python dependencies
```

---

## Development Team

- **Vaibhav** (Dev-A) — Backend, Ranking Engine, REST API & Data Modeling
- **Shrinivas** (Dev-B) — Frontend, UI/UX Design System, Documentation & SRS Lead

---

## License

**Proprietary & Commercial Software License — All Rights Reserved.**  
Copyright © 2026 Vaibhav (01fe24bca300) & Shrinivas (01fe24bca311).  
See [LICENSE](LICENSE) for details.
