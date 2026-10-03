# Product Catalogue Ranked Search

A multi-tenant, high-precision ranking microservice and catalog intelligence engine. Evaluates products across user-weighted multi-criteria dimensions, normalizes continuous numeric and discrete binary metrics, enforces mathematical 100% weight allocation rules, and interleaves date-capped sponsored placements under anti-bias policies.

---

## Key Capabilities

- **Dynamic Multi-Criteria Attribute Modeling (FR-1, FR-2)**: Define custom attributes per domain category. Supports continuous `numeric` ranges and discrete `binary` criteria (Yes/No boolean evaluated on a 0.0/1.0 scale). Configurable metric directionality (`lower_is_better` for metrics like Price and Latency).
- **Strict 100% Weight Allocation (FR-3, NFR-5.1)**: Enforces category weights summing strictly to 100.0%. Provides real-time validation indicator with sub-300ms response time.
- **Deterministic Weighted Scoring & Tie-Breaking (FR-9, FR-10, FR-13)**: Min-Max normalization maps disparate attribute measurements to a unified [0.0, 1.0] scale. Three-tier deterministic tie-breaking resolves identical scores: `Composite Score DESC` &rarr; `Creation Date DESC` &rarr; `Product ID ASC`.
- **Anti-Bias Sponsored Placement Override (FR-14 – FR-17, NFR-5.6)**: Date-scheduled sponsored promotions interleaved at fixed 1:5 intervals (slots 1, 6, 11) with a strict 20.0% placement cap. Preserves raw organic composite scores without score distortion.
- **Attribute Range Filtering (FR-21)**: Pre-ranking filtering allowing users and client applications to specify attribute threshold bounds (`filter_attr_id`, `filter_min`, `filter_max`) to filter products before score computation and ranking.
- **Multi-Tenant Architecture & Platform Administration (FR-18, FR-19, FR-20)**: Complete data isolation across tenant companies. Platform Superadmin console enables company provisioning, cascade deletion, tenant inspection auditing, and direct tenant user password resets.
- **B2B REST API Microservice (FR-12, FR-19, FR-21)**: External RESTful JSON API (`/api/v1/search`, `/api/v1/categories`, `/api/v1/product/<id>`) allowing e-commerce storefronts and external platforms to execute searches, apply dynamic personalization weights, and retrieve full score contribution telemetry.

---

## Tech Stack

- **Backend:** Python 3.10+, Flask
- **Database / ORM:** SQLAlchemy ORM with SQLite (Development/Test) and PostgreSQL compatibility
- **Authentication & Security:** Flask-Login, Werkzeug (salted password hashing, role-based access control)
- **Frontend / UI:** Technical Minimalist design system (Space Grotesk, General Sans, JetBrains Mono, crisp 1px borders)
- **Testing:** Pytest, pytest-flask

---

## Quick Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Product-Catalogue-Ranked-Search
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

4. **Run development server:**
   ```bash
   python run.py
   ```
   *The application starts at `http://127.0.0.1:5000/`.*
