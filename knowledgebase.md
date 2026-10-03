# Product Catalogue Ranked Search & Sponsored Placement Engine: Knowledge Base

**System Architecture Document**  
**Classification:** Theme 2 — Search and Ranking System  
**System Status:** Phase 1 Foundation Active  
**Runtime:** Python 3.10+, Flask, SQLAlchemy, SQLite/PostgreSQL  

---

## 1. Executive Summary & Architectural Overview

The **Product Catalogue Ranked Search & Sponsored Placement Engine** is a high-precision, multi-tenant ranking microservice and catalog intelligence engine. Designed to solve common weaknesses in multi-attribute e-commerce and B2B search, the system:

1. **De-silos catalog dimensions**: Normalizes disparate continuous numeric metrics (price, latency, weight) and discrete binary flags (in-stock, certified) onto a uniform \([0.0, 1.0]\) mathematical domain.
2. **Enforces mathematical rigor**: Mandates a strict 100.0% weight budget across active category attributes before ranking calculations can execute.
3. **Applies anti-bias sponsored placement**: Interleaves active date-bounded sponsored listings at deterministic 1:5 intervals (slots 1, 6, 11) up to a 20.0% placement cap, completely preserving the integrity and auditability of underlying organic ranking scores.
4. **Isolates multi-tenant datasets**: Restricts all entities, attributes, and user activities behind tenant company boundaries.
5. **Provides dual access models**: Delivers a Technical Minimalist web interface for operators alongside high-throughput RESTful JSON endpoints for external consumer storefronts.

---

## 2. The Four Core Engines

The system architecture is organized into four decoupled, cooperatively orchestrated engines:

```
+-----------------------------------------------------------------------------------+
|                           THE 4 ARCHITECTURAL ENGINES                             |
+-------------------------+---------------------------------------------------------+
| ENGINE 1: DATA &        | Multi-tenant schema, SQLAlchemy ORM models, relational  |
| INTEGRITY               | foreign keys, cascade controls, unique attribute values |
+-------------------------+---------------------------------------------------------+
| ENGINE 2: CORE LOGIC &  | Min-Max normalization, directional polarity, composite  |
| ALGORITHM               | weighted sum, 3-tier tie-breaking, 1:5 interleaving     |
+-------------------------+---------------------------------------------------------+
| ENGINE 3: INTERFACE &   | Jinja2 templates, Technical Minimalist CSS system,      |
| ACCESS                  | real-time validation bars, B2B REST microservice API    |
+-------------------------+---------------------------------------------------------+
| ENGINE 4: VALIDATION &  | Strict 100% weight validation, Pytest automated suite,  |
| TESTING                 | zero-variance guardrails, query audit logging           |
+-------------------------+---------------------------------------------------------+
```

---

### 2.1 Engine 1: Data & Integrity (Persistence & Tenant Isolation)

Engine 1 encapsulates the relational database schema, ORM entity definitions, constraint enforcement, and cross-tenant segregation.

#### 2.1.1 Entity-Relationship Overview

| Model | Table Name | Key Purpose | Primary / Foreign Keys |
| :--- | :--- | :--- | :--- |
| `Company` | `companies` | Tenant partition container | `company_id` (PK) |
| `User` | `users` | Authenticated operators & admins | `id` (PK), `company_id` (FK &rarr; `companies`) |
| `Category` | `categories` | Product classification taxonomy | `category_id` (PK), `company_id` (FK &rarr; `companies`) |
| `Attribute` | `attributes` | Scoring dimensions per category | `attribute_id` (PK), `category_id` (FK &rarr; `categories`) |
| `Product` | `products` | Core catalog inventory item | `product_id` (PK), `category_id` (FK &rarr; `categories`) |
| `ProductAttrValue`| `product_attr_values`| EAV raw & normalized attribute values| `pav_id` (PK), `product_id` (FK), `attribute_id` (FK) |
| `SponsoredPlacement`| `sponsored_placements`| Date-scheduled placement overrides | `placement_id` (PK), `product_id` (FK &rarr; `products`) |
| `SearchLog` | `search_logs`| Audit search queries and telemetry | `log_id` (PK), `category_id` (FK &rarr; `categories`) |

#### 2.1.2 Integrity Constraints & Safeguards

- **Multi-Tenant Isolation**: `User` and `Category` maintain explicit foreign key references to `Company.company_id`. Queries must scope by `company_id` to guarantee zero data leakage between tenants.
- **Product-Attribute Uniqueness**: The `ProductAttrValue` entity enforces a composite unique constraint:
  ```python
  __table_args__ = (db.UniqueConstraint('product_id', 'attribute_id', name='_product_attr_uc'),)
  ```
  This prevents duplicate dimension values for any single product.
- **Directional Polarity Flag**: The `Attribute.lower_is_better` boolean flag determines whether lower numeric quantities (e.g. price, shipping delay, power consumption) represent higher ranking utility.
- **Security & Password Hashing**: `User` leverages Werkzeug salted password hashing (`generate_password_hash` with PBKDF2/SHA256) and implements Flask-Login `UserMixin`.
- **Eager & Dynamic Loading**: Relationships utilize `lazy='dynamic'` to facilitate filtered queries and pagination across large product catalogs.

---

### 2.2 Engine 2: Core Logic & Algorithm (Mathematical Kernel)

Engine 2 is responsible for evaluating, transforming, ranking, and interleaving catalog items with zero bias.

#### 2.2.1 Directional Min-Max Normalization

Disparate units (currency, grams, gigabytes, percentage, customer ratings) are mapped onto a standard dimensionless range \([0.0, 1.0]\).

Given attribute \(A\) over category items with observed minimum \(\min(A)\) and maximum \(\max(A)\):

1. **Higher-is-Better (Standard Polarity)**:
   Used for dimensions like battery life, memory, warranty duration, and user rating:
   $$\text{Norm}(x) = \begin{cases} \frac{x - \min(A)}{\max(A) - \min(A)}, & \text{if } \max(A) > \min(A) \\ 1.0, & \text{if } \max(A) = \min(A) \end{cases}$$

2. **Lower-is-Better (Inverted Polarity)**:
   Used for cost, latency, error rates, and dimensions where lower measurements represent superior desirability:
   $$\text{Norm}(x) = \begin{cases} \frac{\max(A) - x}{\max(A) - \min(A)}, & \text{if } \max(A) > \min(A) \\ 1.0, & \text{if } \max(A) = \min(A) \end{cases}$$

3. **Discrete Binary Metrics**:
   Attributes of type `binary` (e.g., Bluetooth 5.0 present, Free Shipping, Organic Certification) evaluate directly to:
   $$\text{Norm}(x) = \begin{cases} 1.0, & \text{if } x = \text{True / 1} \\ 0.0, & \text{if } x = \text{False / 0} \end{cases}$$

#### 2.2.2 Multi-Criteria Composite Scoring

Each product receives a composite score \(S \in [0.0, 1.0]\) computed as the weighted sum of its normalized attribute values:

$$S(p) = \sum_{i=1}^{k} \left( \frac{w_i}{100.0} \times \text{Norm}(x_{p, i}) \right)$$

Where:
- \(k\) is the count of active attributes configured for the target category.
- \(w_i\) is the percentage weight assigned to attribute \(i\).
- Invariant: \(\sum_{i=1}^{k} w_i = 100.0\%\).

#### 2.2.3 Three-Tier Deterministic Tie-Breaking

To avoid non-deterministic result ordering across distributed nodes or database updates, identical composite scores are resolved using a 3-tier sort predicate:

1. **Tier 1:** `composite_score DESC` (Primary ranking utility)
2. **Tier 2:** `created_at DESC` (Recency bias for tied products)
3. **Tier 3:** `product_id ASC` (Deterministic surrogate key tie-breaker)

#### 2.2.4 Anti-Bias Sponsored Interleaving Policy

To balance monetization requirements with algorithmic transparency:
- **Placement Cadence**: Sponsored items are placed exclusively at 1:5 intervals (Position 1, Position 6, Position 11, etc.).
- **Volume Cap**: Maximum 20.0% of total displayed positions may be occupied by sponsored products.
- **Date Capping**: A sponsored placement is active if and only if:
  $$\text{start\_date} \le \text{current\_date} \le \text{end\_date} \quad \land \quad \text{is\_active} = \text{True}$$
- **Score Integrity**: Sponsored listings receive a visible `[SPONSORED]` badge and retain their organic composite scores without artificial score inflation.

---

### 2.3 Engine 3: Interface & Access (Web Tech & REST API)

Engine 3 provides user interaction through a web interface and external programmatic access via a REST microservice.

#### 2.3.1 Technical Minimalist Design System

The visual design system embodies high-density technical aesthetics:
- **Typography**:
  - Headings / Brand: `Space Grotesk` (Geometric, crisp letterforms)
  - Monospace Accents: `JetBrains Mono` (Scores, IDs, formulas, code tags)
  - Prose / Body: `General Sans` (High legibility, clean neutral geometry)
- **Palette**: Dark slate backgrounds (`#07090e`, `#0d121c`, `#131b29`), 1px structural dividing lines (`#1c2738`, `#2a3b54`), and functional semantic accents (`#06b6d4` Cyan for telemetry, `#10b981` Emerald for online status, `#f59e0b` Amber for sponsored items).
- **Template Architecture**:
  - `app/templates/base.html`: HTML5 frame, header with `[R//E] RANK_ENGINE v1.0` branding, navigation with safe dynamic fallback macro, flash message container, and operational status footer.
  - `app/templates/index.html`: Architectural showcase, metric strip, 4-engine breakdown cards, live algorithm mathematical preview, and quick navigation actions.

#### 2.3.2 B2B REST Microservice API

External systems query the engine via JSON endpoints:

- `GET /api/v1/categories`: Retrieve categories and defined attributes for the active tenant.
- `POST /api/v1/search`: Execute a multi-criteria ranked search.
  - **Payload**:
    ```json
    {
      "category_id": 1,
      "query": "laptop",
      "custom_weights": {"price": 40.0, "ram": 30.0, "weight": 30.0},
      "filters": {"filter_attr_id": 2, "filter_min": 16.0, "filter_max": 64.0},
      "page": 1,
      "per_page": 20
    }
    ```
  - **Response**: Array of ranked products with composite score, normalized component contributions, sponsored flags, and execution latency.
- `GET /api/v1/product/<id>`: Retrieve specific product data, raw attribute values, and score breakdown.

---

### 2.4 Engine 4: Validation, Security & Reporting

Engine 4 provides quality assurance, validation gates, security controls, and query auditing.

#### 2.4.1 Strict 100% Weight Sum Validation

Before computing rankings or persisting category attribute weights:
$$\left| \sum_{i=1}^{k} w_i - 100.0 \right| < 10^{-4}$$
If the sum deviates from 100.0%, the engine rejects the configuration with a `422 Unprocessable Entity` or form validation error, preventing corrupted ranking calculations.

#### 2.4.2 Zero-Variance Division Guardrail

When all products in a category possess identical values for an attribute (\(\max(A) = \min(A)\)):
- Traditional Min-Max normalization fails due to division by zero.
- Engine 4 detects \(\max(A) = \min(A)\) and gracefully assigns a normalized score of \(1.0\) to all items, ensuring the attribute does not artificially penalize products.

#### 2.4.3 Security & Role-Based Access Control (RBAC)

1. **Superadmin**: Full access across all tenant companies, user provisioning, global system telemetry, and company cascade deletion.
2. **Company Admin**: Manage categories, define attributes, upload catalog products, configure attribute weights, and schedule sponsored placements for their assigned company.
3. **Standard User / API Client**: Execute searches, submit dynamic weight vectors, and view rankings.

#### 2.4.4 Query Audit & Telemetry Logging

Every search executed via the UI or REST API records an immutable `SearchLog` record capturing:
- `query_text`: Search query term.
- `category_id`: Target category inspected.
- `results_count`: Number of qualifying items.
- `searched_at`: UTC timestamp.

This telemetry powers search demand insights, zero-result discovery, and catalog demand tracking.

#### 2.4.5 Automated Testing Suite

Comprehensive Pytest suite validating:
- Model relationships and integrity constraints.
- Min-Max normalization math with continuous and discrete values.
- Zero-variance handling.
- Anti-bias 1:5 interleaving and 20% cap rules.
- 100% weight validation failure and success branches.
- Multi-tenant query isolation.

---

## 3. Phase 1 Foundation Log

- **Milestone:** Phase 1 Foundation Initialized
- **Components Established:**
  - Flask Application Factory (`app/__init__.py`) with dynamic blueprint registration.
  - SQLAlchemy multi-tenant schema models (`Company`, `User`, `Category`, `Attribute`, `Product`, `ProductAttrValue`, `SponsoredPlacement`, `SearchLog`).
  - Configuration profiles (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`).
  - Technical Minimalist design system (`app/static/css/style.css`).
  - Base semantic HTML5 layout (`app/templates/base.html`) with safe endpoint fallback routing.
  - Architectural dashboard and landing view (`app/templates/index.html`).
  - Comprehensive documentation: Knowledge Base, Function Map, and Setup Guide.
