# The 4-Engine System Architecture & Viva Preparation Manual

> **Course**: BCA Mini-Project • Academic Theme 2: Search & Ranking Platform  
> **Project Title**: Multi-Tenant Weighted Ranking Microservice & Noise E-Commerce Storefront  
> **Team Members**:  
> * **Vaibhav Patil** (Roll: `01fe24bca300`) — Primary Engine Lead: **Engine 1 (Data & Integrity)** & **Engine 3 (Logic & Rule / Backend)**  
> * **Shrinivas** (Roll: `01fe24bca311`) — Primary Engine Lead: **Engine 2 (Interface & Access / UI)** & **Engine 4 (Testing & Validation)**  
> **Target Repositories**:  
> 1. `Product-Catalogue-Ranked-Search` (Microservice on Port 5000)  
> 2. `e-commerce-website` (Retail Storefront on Port 8000)  

---

## 1. Executive Summary & 4-Engine Architecture

In compliance with the project directives, the application is strictly partitioned into **Four Specialized Engines**. Every team member maintains cross-functional mastery of all four engines, with dedicated primary ownership assigned for viva examination and daily development tracking.

```
+-----------------------------------------------------------------------------------+
|                        ENGINE 2: INTERFACE & ACCESS / UI                         |
|   - Consumer Storefront (Port 8000)        - B2B Admin Console (Port 5000)       |
|   - Recommendation Tuner (Vanilla JS)     - Real-Time 100% Weight Sum Meter      |
|   - Responsive CSS Theme (Dark-Cyan)      - Shopping Cart & Checkout Views       |
+-----------------------------------------------------------------------------------+
                                         │  ▲
                     HTTP REST / JSON    │  │  Client-Side DOM Events
                                         ▼  │
+-----------------------------------------------------------------------------------+
|                         ENGINE 3: LOGIC & RULE / BACKEND                          |
|   - Deterministic Min-Max Normalization   - Mathematical Multi-Criteria Sum      |
|   - Strict 100% Weight Allocation Guard   - 3-Tier Tie-Breaking System           |
|   - Anti-Bias Sponsored Ads (1:5 Capping) - Multi-Tenant Isolation Middleware    |
|   - External B2B REST API Endpoints       - Search Hit Counter & Analytics       |
+-----------------------------------------------------------------------------------+
                    │                                    │
    SQLAlchemy ORM  │                                    │  Automated Harness
    Transactions    ▼                                    ▼  (61 + 68 = 129 Tests)
+----------------------------------+     +------------------------------------------+
|    ENGINE 1: DATA & INTEGRITY    |     |      ENGINE 4: TESTING & VALIDATION      |
|   - Pure RDBMS (SQLite / PG / SQL)|    |   - Excel Test Matrix (45 Scenarios)     |
|   - 12 Tables Across 2 Databases |     |   - Positive, Negative & Edge Cases      |
|   - Foreign Keys & ON DELETE CAS |     |   - Pytest Fixtures & Mock Clients       |
|   - ANSI SQL Queries Audit File  |     |   - Performance & Boundary Verification  |
+----------------------------------+     +------------------------------------------+
```

---

## 2. Team Engine Allocation & Responsibilities

| Engine Number & Name | Primary Responsible Student | Secondary / Cross-Functional Lead | Core Technologies | Dedicated Git Deliverable File |
| :--- | :--- | :--- | :--- | :--- |
| **Engine 1: Data & Integrity** | **Vaibhav Patil** (`01fe24bca300`) | **Shrinivas** (`01fe24bca311`) | RDBMS, SQLite 3, PostgreSQL dialect, SQLAlchemy ORM, DDL/DML, Constraints | `DATABASE_QUERIES_ENGINE1.sql` |
| **Engine 2: Interface & Access (UI)** | **Shrinivas** (`01fe24bca311`) | **Vaibhav Patil** (`01fe24bca300`) | HTML5, CSS3 Grid/Flexbox, JavaScript (ES6+), Jinja2 Templates, Bootstrap | `app/templates/`, `app/static/` |
| **Engine 3: Logic & Rule (Backend)** | **Vaibhav Patil** (`01fe24bca300`) | **Shrinivas** (`01fe24bca311`) | Python 3.10+, Flask 3.x, REST API, Werkzeug Security, Mathematical Algorithms | `app/ranking/`, `app/api/`, `app/admin/` |
| **Engine 4: Testing & Validation** | **Shrinivas** (`01fe24bca311`) | **Vaibhav Patil** (`01fe24bca300`) | Pytest, Pytest-Flask, OpenPyXL, Unit Tests, Integration Tests, Security Audits | `TEST_CASES_ENGINE4.xlsx` |

---

## 3. Deep-Dive Specification of Each Engine

### Engine 1: Data & Integrity (RDBMS)
* **Lead**: Vaibhav Patil  
* **Storage Standard**: Pure Relational Database Management System (RDBMS). Strictly **No NoSQL / MongoDB**.
* **Database 1 (`ranking_engine.db` • Microservice)**:
  1. `companies`: Multi-tenant organization boundaries.
  2. `users`: System users with salted password hashes and role flags (`is_admin`, `is_superadmin`).
  3. `categories`: Classification categories belonging to a tenant company.
  4. `attributes`: Evaluation criteria with constraints: `weight >= 0`, `lower_is_better` boolean, `data_type` in `('numeric', 'binary')`.
  5. `products`: Catalog items with cached `composite_score` and organic `search_count`.
  6. `product_attr_values`: Raw and normalized values per product-attribute pair (unique composite constraint).
  7. `sponsored_placements`: Auction/monetization slot scheduling with date validity checks.
  8. `search_logs`: Search query telemetry recording frequency, category context, and timestamp.
* **Database 2 (`noise_ecommerce.db` • Consumer Storefront)**:
  9. `storefront_products`: Customer-facing retail catalog with retail pricing, original MRP, specifications JSON, and stock status.
  10. `cart_items`: User session-scoped shopping carts.
  11. `orders`: Financial transaction orders with subtotal, 18% GST calculation, shipping rules, and statuses.
  12. `order_items`: Line-item items with price snapshots.
* **Data Integrity Mechanisms**:
  - **Foreign Key Constraints**: `ON DELETE CASCADE` ensures deleting a company cleans up categories, attributes, and products without leaving orphaned records.
  - **Unique Constraints**: Unique product slug index; unique category name per tenant; unique `(product_id, attribute_id)` pair in utility matrix.
  - **Dedicated Audit File**: [`DATABASE_QUERIES_ENGINE1.sql`](file:///home/blue/Collage-Mini-Project/college_engine_deliverables/DATABASE_QUERIES_ENGINE1.sql) contains all CREATE, ALTER, INSERT, UPDATE, DELETE, and analytical SQL queries.

---

### Engine 2: Interface & Access / UI / FrontEnd
* **Lead**: Shrinivas  
* **Architecture**: Responsive, technical-minimalist frontend communicating with backend services via Jinja2 server-rendered templates and asynchronous JSON `fetch()` calls.
* **Key Components**:
  1. **Clean Customer Storefront (Port 8000)**: Customer-facing retail experience. Adheres strictly to **Information Hiding**: internal algorithm weights, composite mathematical decimals, and ranking engine telemetry are never displayed to shoppers. Shoppers see clean retail badges (`★ 4.8 Rating`, `45h Battery`, `ANC: Yes`).
  2. **Recommendation Tuner Modal (`storefront.js`)**: An interactive sliding drawer on `/shop` allowing shoppers to customize attribute priorities (e.g. 70% Battery Life, 30% Price) with instant client-side DOM re-ranking.
  3. **Live 100% Weight Meter (`weight_check.js`)**: Real-time administrative indicator that validates criteria weights as the administrator types or drags sliders, dynamically toggling between green `[VALID: 100.0%]` and crimson `[INVALID: Imbalance]` badges.
  4. **Engine Status Health Banner**: Navbar status pill rendering green `[ENGINE: CONNECTED (PORT 5000)]` when the ranking service is live, and transitioning to amber `[ENGINE: OFFLINE (FALLBACK MODE)]` if the microservice is unreachable.
  5. **B2B Management Dashboard (Port 5000)**: Technical-minimalist dark-cyan design system using JetBrains Mono, crisp 1px borders, and responsive grid layouts for multi-tenant administration.

---

### Engine 3: Logic & Rule / Backend
* **Lead**: Vaibhav Patil  
* **Architecture**: Decoupled Python/Flask microservice communicating via HTTP REST APIs with strict mathematical guarantees.
* **Core Algorithms**:
  1. **Min-Max Normalization Algorithm**:
     Maps disparate dimensions (e.g. Battery Life 0–100 hours vs Price ₹500–₹15,000) into a normalized utility space $[0.0, 1.0]$:
     * Benefit Metric (Higher is better, e.g. Battery):  
       $$\text{Norm}(x) = \frac{x - \min}{\max - \min}$$
     * Cost Metric (Lower is better, e.g. Price):  
       $$\text{Norm}(x) = \frac{\max - x}{\max - \min}$$
     * Binary Metric (e.g. ANC Yes/No): Evaluated directly as $1.0$ (True) or $0.0$ (False).
     * Zero-Division Guard: If $\max = \min$, returns $1.0$ safely.
  2. **Mathematical Composite Scoring**:
     $$\text{Composite Score} = \sum_{i=1}^{n} \left(\text{Normalized Utility}_i \times \frac{\text{Weight}_i}{100}\right)$$
  3. **Deterministic 3-Tier Tie Breaking**:
     Resolves identical scores deterministically without relying on database random row order:
     `Composite Score DESC` $\rightarrow$ `Creation Date DESC` $\rightarrow$ `Product ID ASC`.
  4. **Anti-Bias Sponsored Interleaving (Monetization Engine)**:
     - Promoted products are inserted into fixed premium positions (Slot 1, Slot 6, Slot 11).
     - Strict 1:5 ratio cap: A maximum of 1 sponsored product is permitted per 5 organic products (20.0% cap), preserving organic ranking trust.
     - The organic composite score is preserved and displayed alongside the sponsored badge.
  5. **Multi-Tenant Scoping Middleware**:
     Enforces tenant isolation using Flask's `g.company_id` and custom decorators `@superadmin_required` and `@company_required`.

---

### Engine 4: Testing & Validation
* **Lead**: Shrinivas  
* **Architecture**: Multi-layered testing strategy combining automated `pytest` test suites and a formal Test Case Excel Sheet.
* **Test Case Classification**:
  1. **Positive Scenarios (20 Cases)**: Verifies normal operational workflows (valid weight allocation of 100%, successful Min-Max normalization, dynamic search API with valid payloads, successful checkout, order generation).
  2. **Negative Scenarios (14 Cases)**: Verifies system error handling and security guards (rejecting weights $\ne 100\%$, rejecting negative prices or weights, blocking unauthenticated admin access, SQL injection sanitization, XSS escaping).
  3. **Edge Cases (11 Cases)**: Verifies extreme conditions (uniform values where $\min = \max$, empty categories with 0 products, categories with 0 active attributes, floating-point precision bounds, offline microservice fallback).
* **Automated Pytest Harness**:
  - `Product-Catalogue-Ranked-Search`: 61 automated tests (`test_models.py`, `test_engine.py`, `test_api.py`, `test_sponsor.py`, `test_routes.py`, `test_edge_cases.py`, `test_insights.py`).
  - `e-commerce-website`: 68 automated tests (`test_storefront.py`, `test_admin.py`, `test_engine_client.py`).
  - **Total**: 129 Automated Tests passing with 100% pass rate.
* **Dedicated Excel Deliverable**: [`TEST_CASES_ENGINE4.xlsx`](file:///home/blue/Collage-Mini-Project/college_engine_deliverables/TEST_CASES_ENGINE4.xlsx) formatted with summary metrics and color-coded scenario tags.

---

## 4. Comprehensive College Viva & Oral Exam Q&A

### Questions on Engine 1: Data & Integrity (RDBMS)

#### Q1.1: Why did your team choose SQLite/RDBMS instead of NoSQL like MongoDB?
> **Answer**:  
> "Our application fundamentally requires strict relational integrity, ACID transactional compliance, and multi-table constraints. For instance, an attribute cannot exist without a parent category, and attribute values cannot exist without both a product and an attribute. An RDBMS enforces this through foreign keys with `ON DELETE CASCADE`. Furthermore, NoSQL lacks built-in schema constraints to enforce mathematical invariants like ensuring category weights sum strictly to 100% across multiple rows."

#### Q1.2: What foreign key constraints and cascade rules did you implement?
> **Answer**:  
> "We implemented `ON DELETE CASCADE` across the entire multi-tenant hierarchy:  
> `Company` $\rightarrow$ `Category` $\rightarrow$ `Attribute` $\rightarrow$ `ProductAttrValue`.  
> If an administrator deletes a category, all associated criteria, product attribute measurements, and search logs are automatically and cleanly purged by the relational database engine, preventing orphaned records and database corruption."

#### Q1.3: How do you prevent duplicate attributes within the same category?
> **Answer**:  
> "We enforce a composite unique constraint at the database table level:  
> `CONSTRAINT uq_category_attribute UNIQUE (category_id, name)`.  
> This ensures that even under concurrent administrative requests, the database guarantees that no category can ever possess two criteria with the same name."

#### Q1.4: How are passwords stored in the database?
> **Answer**:  
> "Passwords are never stored in plaintext. We utilize Werkzeug's cryptographic salted hash function (`scrypt` / `pbkdf2:sha256`) generating a 256-character hash string stored in the `password_hash` column. During authentication, `check_password_hash()` compares the computed hash against the stored hash in constant time to prevent timing attacks."

#### Q1.5: How did you design the schema to support discrete binary attributes alongside continuous numeric ones?
> **Answer**:  
> "In the `attributes` table, we have a `data_type` column constrained to `('numeric', 'binary')`. For continuous numeric attributes (like Battery Life: 0–100 hours), `min_value` and `max_value` store the scale boundaries. For binary attributes (like Active Noise Cancelling), the database defaults `min_value = 0.0` and `max_value = 1.0`, storing `1.0` for Yes and `0.0` for No in the `product_attr_values` table, allowing both to be evaluated uniformly by the same linear normalization formula."

---

### Questions on Engine 2: Interface & Access (UI / FrontEnd)

#### Q2.1: What is the core UX philosophy of the customer-facing storefront?
> **Answer**:  
> "The core philosophy is **Storefront Cleanliness and Information Hiding**. Retail shoppers should never see internal B2B algorithmic machinery—such as raw composite decimals (e.g. `0.8425`), algorithmic weights, or diagnostic rankings. Instead, shoppers experience an intuitive, clutter-free e-commerce store with familiar retail indicators: star ratings, review counts, battery hours, and stock availability."

#### Q2.2: How does the Recommendation Tuner modal work on the frontend?
> **Answer**:  
> "When a shopper opens the Tuner on `/shop`, vanilla JavaScript reads the current attribute configuration for that category and renders interactive range sliders (0% to 100%). As the user moves the slider, an input event listener dynamically recalculates a local weighted score for each rendered product card in the DOM and re-orders the product card grid in real-time without requiring a full page refresh."

#### Q2.3: How does the real-time 100% weight sum meter work in the administrative UI?
> **Answer**:  
> "In `weight_check.js`, an event listener attaches to all attribute weight input fields. On every `input` event, it sums the current values across all active criteria. It applies a floating-point tolerance check `Math.abs(sum - 100.0) < 0.05`. If valid, the badge immediately updates to cyan/green with `[VALID: 100.0%]`, and enables the save button. If invalid, it turns crimson with `[INVALID: Current Sum %]` and disables the save action."

#### Q2.4: How does the UI handle ranking engine downtime?
> **Answer**:  
> "The base navigation layout contains an asynchronous health check script that queries `/api/v1/health` on Port 5000. If the microservice is responding, it renders a green indicator: `[ENGINE: CONNECTED]`. If the microservice is down, it gracefully renders an amber banner: `[ENGINE: OFFLINE (FALLBACK ACTIVE)]` without crashing the page or showing raw server errors to the user."

#### Q2.5: What CSS architecture did you use for responsive design?
> **Answer**:  
> "We utilized CSS Grid with `repeat(auto-fill, minmax(280px, 1fr))` for catalog layouts, combined with Flexbox for internal card component alignment. This ensures that cards automatically collapse from 4 columns on desktop monitors to 2 columns on tablets and a single column on mobile viewports (< 480px) without horizontal scrollbar overflow."

---

### Questions on Engine 3: Logic & Rule (Backend)

#### Q3.1: Explain the Min-Max Normalization formula used in your ranking engine.
> **Answer**:  
> "Different attributes use completely different units (hours vs rupees vs star counts). To combine them mathematically, we normalize them to a dimensionless scale of $[0.0, 1.0]$.  
> For benefit criteria where higher is better (e.g. Battery Life), we use:  
> $$\text{Norm}(x) = \frac{x - \min}{\max - \min}$$  
> For cost criteria where lower is better (e.g. Price), we invert the formula so lower prices receive higher utility:  
> $$\text{Norm}(x) = \frac{\max - x}{\max - \min}$$"

#### Q3.2: How does the system prevent a division by zero error if all products in a category have the exact same price or battery life?
> **Answer**:  
> "If all products have the exact same value, $\max = \min$, which causes the denominator $(\max - \min)$ to evaluate to zero. In `app/ranking/engine.py`, we implement a defensive guard clause:  
> `if max_val == min_val: return 1.0`  
> This assigns full normalized utility ($1.0$) to all products equally and prevents runtime `ZeroDivisionError` exceptions."

#### Q3.3: How does your deterministic tie-breaking algorithm work?
> **Answer**:  
> "When two or more products achieve the exact same composite score (e.g. both calculate to `0.7850`), relying on standard database ordering produces non-deterministic, flickering ranks. We engineered a strict 3-tier tie-breaking comparator:  
> 1. Primary Sort: `composite_score DESC`  
> 2. Secondary Sort: `created_at DESC` (newer releases win ties)  
> 3. Tertiary Sort: `product_id ASC` (guaranteed unique tie-breaker)  
> This ensures 100% reproducible and fair rankings across all API queries."

#### Q3.4: Explain your anti-bias sponsored placement rule and how it balances monetization with ranking integrity.
> **Answer**:  
> "Commercial ranking platforms often suffer from bias when sponsored items distort algorithmic scores. We engineered an Anti-Bias Override Policy:  
> 1. Promoted products are interleaved into fixed predefined slots (Slot 1, Slot 6, Slot 11).  
> 2. We enforce a strict 1:5 ratio cap (maximum 20% sponsored products in any result set).  
> 3. The raw organic composite score is preserved and displayed with a clear 'Sponsored' disclosure badge.  
> 4. Expired placements are automatically filtered out using SQL date constraints."

#### Q3.5: How is multi-tenant isolation enforced in the backend?
> **Answer**:  
> "Every category, attribute, product, and search log is scoped by `company_id`. During request processing, our Flask before-request handler validates the user's session and binds their authenticated `company_id` to Flask's global request context (`g.company_id`). All ORM queries automatically filter by this tenant ID, strictly preventing Company A from viewing, editing, or deleting Company B's catalog."

---

### Questions on Engine 4: Testing & Validation

#### Q4.1: How did you categorize test scenarios in your test matrix?
> **Answer**:  
> "We structured all 45 test cases into three distinct categories:  
> 1. **Positive Scenarios (20 cases)**: Verifying expected operational flows under valid inputs.  
> 2. **Negative Scenarios (14 cases)**: Verifying security barriers, validation rejections (weights $\ne 100\%$, unauthorized access, invalid quantities).  
> 3. **Edge Cases (11 cases)**: Verifying boundary and stress limits (uniform attributes $\min = \max$, 0 products, 0 active attributes, extreme float limits, offline microservice resilience)."

#### Q4.2: How do your automated pytest tests connect with the Excel test sheet?
> **Answer**:  
> "Every single test case entry in the Excel sheet contains a dedicated column titled `Automated Pytest Reference` specifying the exact test file and function (for example, `TC-LOG-001` maps to `tests/test_engine.py::test_normalize_value_benefit`). Running `python3 -m pytest` executes these automated assertions, ensuring that the software behaves exactly as documented in the Excel matrix."

#### Q4.3: How do you test the offline fallback resilience between the two services?
> **Answer**:  
> "In `tests/test_engine_client.py`, we test this using a mock network timeout. When `requests.get()` throws a `ConnectionError` or `Timeout`, the `RankingEngineClient` catches the exception, switches to offline fallback mode, retrieves cached local products sorted by rating, and attaches an `'engine_offline': True` flag to ensure the consumer storefront continues functioning without crashing."

#### Q4.4: How did you verify security against SQL Injection and XSS attacks?
> **Answer**:  
> "In `TC-TST-004`, we executed test payloads containing SQL injection patterns (`' OR 1=1; DROP TABLE products; --`). Because our Data Engine uses SQLAlchemy parameterized queries, the input was safely treated as a literal search string with zero schema alteration. In `TC-TST-005`, we verified that HTML tags like `<script>alert('XSS')</script>` submitted in forms are escaped by Jinja2's auto-escaping engine as `&lt;script&gt;`, neutralizing script execution."

---

## 5. File & Deliverables Quick Reference

All college-required deliverables have been created and placed in the project directory:

```text
/home/blue/Collage-Mini-Project/college_engine_deliverables/
├── DATABASE_QUERIES_ENGINE1.sql          # Engine 1: Pure RDBMS DDL, ALTER, DML & audit queries
├── DEV_LOGS_VAIBHAV.md                   # Engine 1 & 3: Vaibhav's error log & technical resolutions
├── DEV_LOGS_SHRINIVAS.md                 # Engine 2 & 4: Shrinivas's error log & technical resolutions
├── TEAM_DEVELOPER_ISSUE_RESOLUTION_LOGS.md # Combined developer issues & fixes document
├── TEST_CASES_ENGINE4.xlsx               # Engine 4: Excel sheet (Positive, Negative, Edge Cases)
└── FOUR_ENGINES_PROJECT_MANUAL_AND_VIVA_GUIDE.md # Master 4-Engine Guide & Viva Preparation
```

### Git Push Command for Deliverables
To push these new files to your GitHub repository:

```bash
# Push to Product-Catalogue-Ranked-Search repository
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git add DATABASE_QUERIES_ENGINE1.sql DEV_LOGS_VAIBHAV.md TEST_CASES_ENGINE4.xlsx
git commit -m "docs: add Engine 1 SQL queries, Engine 4 test cases, and developer issue resolution logs"
git push origin main

# Push to e-commerce-website repository
cd /home/blue/Collage-Mini-Project/e-commerce-website
git add DATABASE_QUERIES_ENGINE1.sql DEV_LOGS_SHRINIVAS.md TEST_CASES_ENGINE4.xlsx
git commit -m "docs: add Engine 1 SQL queries, Engine 4 test cases, and developer issue resolution logs"
git push origin main
```
