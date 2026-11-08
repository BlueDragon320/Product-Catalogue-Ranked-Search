# Master 6-Week Development & Deployment Guide

> **Course**: BCA Mini-Project • Theme 2: Search & Ranking System  
> **Collaborators**: Vaibhav (Dev-1 • `01fe24bca300`) & Shrinivas (Dev-2 • `01fe24bca311`)  
> **Repositories**:  
> 1. `Product-Catalogue-Ranked-Search` (Weighted Ranking Engine Microservice • Port 5000)  
> 2. `e-commerce-website` (Noise Consumer E-Commerce Storefront • Port 8000)  

---

## 1. Master 6-Week Summary Matrix

| Week | Milestone Phase | Dev-1 (Vaibhav) Responsibilities | Dev-2 (Shrinivas) Responsibilities | Architecture & Focus Areas |
| :---: | :--- | :--- | :--- | :--- |
| **W1** | **Foundations & Scaffolding** | Flask app factories, SQLAlchemy models, environment configs, initial READMEs | Base HTML templates, dark-cyan styling, setup guides, initial function mapping | Scaffolding, database schema, CSS design tokens, initial docs |
| **W2** | **Auth & Multi-Tenancy** | Authentication system (login, register, session), HTTP `RankingEngineClient` with resilience | Multi-tenant company CRUD, tenant data isolation, live engine status banner | Auth guards, tenant scoping, REST client, status indicators |
| **W3** | **Criteria & Storefront Catalog** | Category & attribute management CRUD, `/shop` catalog routing, `/api/smart-rank` endpoint | Real-time 100% weight meter, weight API, recommendation tuner modal with sliders | Criteria setup, dynamic weights, live validation, catalog UI |
| **W4** | **Scoring Engine & Cart Workflow** | Min-max normalization, weighted sum scoring, product details & score breakdown | Product CRUD with dynamic attribute values, responsive shopping cart, checkout success UI | Algorithmic scoring math, product attribution, cart session |
| **W5** | **Monetization & B2B REST APIs** | External B2B `/api/v1/search` API, catalog sync endpoints, search insights dashboard | Calendar-bounded sponsored placements, sponsor insertion algorithm, store admin console | Monetization, 1:5 sponsor interleaving, analytics, admin portal |
| **W6** | **Test Hardening & Release v1.0** | Comprehensive integration tests, security audits, realistic multi-device seed data | Edge-case test suites, API reference documentation, production integration guide, v1.0 release tag | 129 test cases, 16+ Noise product catalog, release audit |

---

## 2. Detailed Weekly Breakdown & Push Instructions

---

### Week 1 • Phase 1 — Foundations, Data Models & Base Templates

**Objective**: Scaffold both Flask applications, configure SQLite databases, define SQLAlchemy models, build base layouts, and initialize styling.

#### Deliverables Summary
* **`Product-Catalogue-Ranked-Search`**:
  * `run.py`: Flask entry point (Port 5000)
  * `config.py`: Environment configurations (Development, Testing, Production)
  * `requirements.txt`: Project dependencies (`Flask`, `Flask-SQLAlchemy`, `Flask-Login`, `Flask-WTF`, `pytest`)
  * `app/__init__.py`: App factory with DB extension initialization
  * `app/models.py`: Declarative models (`Company`, `User`, `Category`, `Attribute`, `Product`, `ProductAttrValue`, `SponsoredPlacement`)
  * `app/templates/base.html`: Minimalist base shell
  * `app/templates/index.html`: Landing console
  * `app/static/css/style.css`: Technical dark-cyan theme tokens
  * `docs/setup_guide.md`: Development setup documentation
* **`e-commerce-website`**:
  * `run.py`: Flask entry point (Port 8000)
  * `config.py`: Storefront settings, currency symbol (`₹`), ranking engine integration URL
  * `app/__init__.py`: Storefront app factory
  * `app/models.py`: Storefront models (`Product`, `CartItem`, `Order`, `OrderItem`)
  * `app/templates/base.html`: Customer retail layout
  * `app/templates/storefront/index.html`: Retail home page
  * `app/static/css/style.css`: Noise storefront styling

#### Git Commands

##### Dev-1 (Vaibhav)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add run.py config.py requirements.txt app/__init__.py app/models.py README.md
git commit -m "Scaffold Flask application factory, database models, and config"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add run.py config.py requirements.txt app/__init__.py app/models.py README.md
git commit -m "Scaffold storefront application, models, and configuration"
git push origin main
```

##### Dev-2 (Shrinivas)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add app/templates/base.html app/templates/index.html app/static/css/style.css function_map.md docs/setup_guide.md
git commit -m "Add base layout template, CSS styling, function map, and setup guide"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add app/templates/base.html app/templates/storefront/index.html app/static/css/style.css function_map.md docs/setup_guide.md
git commit -m "Create storefront base layout, retail CSS theme, and documentation"
git push origin main
```

---

### Week 2 • Phase 2 — Authentication, Multi-Tenancy & Engine REST Client

**Objective**: Implement authentication, session cookies, multi-tenant company data isolation, HTTP `RankingEngineClient` with resilience, and live status banners.

#### Deliverables Summary
* **`Product-Catalogue-Ranked-Search`**:
  * `app/auth/__init__.py` & `routes.py`: Login, session management, logout
  * `app/auth/forms.py`: LoginForm and validation
  * `app/templates/auth/login.html` & `register.html`: Clean auth views
  * `app/admin/__init__.py` & `routes.py`: Company CRUD operations with tenant scoping
  * `app/admin/forms.py`: CompanyAccountForm
  * `app/templates/admin/company_list.html`, `company_form.html`, `platform_dashboard.html`: Multi-tenant dashboard
* **`e-commerce-website`**:
  * `app/engine_client.py`: HTTP client connecting Port 8000 to Port 5000 with offline fallback
  * `tests/test_engine_client.py`: Unit tests for connection retry and fallback
  * `app/storefront/__init__.py`: Storefront blueprint setup
  * Engine health indicator banner on storefront navbar

#### Git Commands

##### Dev-1 (Vaibhav)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add app/auth/__init__.py app/auth/routes.py app/auth/forms.py app/templates/auth/login.html app/templates/auth/register.html
git commit -m "Add authentication system with login, session handling, and validation"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add app/engine_client.py tests/test_engine_client.py
git commit -m "Implement RankingEngineClient with REST calls and offline fallback"
git push origin main
```

##### Dev-2 (Shrinivas)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add app/admin/__init__.py app/admin/forms.py app/templates/admin/company_list.html app/templates/admin/company_form.html app/templates/admin/platform_dashboard.html function_map.md
git commit -m "Add company CRUD and tenant data isolation"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add app/storefront/__init__.py function_map.md
git commit -m "Add live ranking engine status banner and connection indicators"
git push origin main
```

---

### Week 3 • Phase 3 — Criteria Management, Weight Validation & Storefront Catalog

**Objective**: Build category and attribute configuration, real-time 100% weight sum validation indicator, storefront catalog routes, and recommendation tuner.

#### Deliverables Summary
* **`Product-Catalogue-Ranked-Search`**:
  * `app/admin/routes.py`: Category and Attribute CRUD routes (`new_category`, `edit_category`, `new_attribute`, `edit_attribute`)
  * `app/admin/forms.py`: CategoryForm, AttributeForm with numeric and binary data types
  * `app/templates/admin/category_list.html`, `category_form.html`, `attribute_list.html`, `attribute_form.html`, `category_header.html`, `category_overview.html`: Category management UI
  * `app/api/__init__.py` & `routes.py`: Real-time weight total validation endpoints (`/api/category/<id>/weight-total`, `/api/category/<id>/weight-validate`)
  * `app/static/js/weight_check.js`: Live 100% weight meter widget
  * `tests/test_models.py`: Model and weight validation tests
* **`e-commerce-website`**:
  * `app/storefront/routes.py`: Catalog browse routes (`/shop`), search filter logic, `/api/smart-rank` dynamic reranking endpoint
  * `app/templates/storefront/shop.html`: Category browsing view with product cards
  * `app/static/js/storefront.js`: Recommendation tuner modal with dynamic sliders and presets
  * `app/static/css/style.css`: Tuner modal and slider styling

#### Git Commands

##### Dev-1 (Vaibhav)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add app/admin/routes.py app/admin/forms.py app/templates/admin/category_list.html app/templates/admin/category_form.html app/templates/admin/attribute_list.html app/templates/admin/attribute_form.html app/templates/admin/category_header.html app/templates/admin/category_overview.html
git commit -m "Add category CRUD routes, forms, templates and attribute CRUD"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add app/storefront/routes.py app/templates/storefront/index.html app/templates/storefront/shop.html
git commit -m "Implement shop catalog routes and smart-rank dynamic endpoint"
git push origin main
```

##### Dev-2 (Shrinivas)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add app/api/__init__.py app/api/routes.py app/static/js/weight_check.js tests/test_models.py function_map.md
git commit -m "Add weight validation API, live JS indicator, and model tests"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add app/static/js/storefront.js app/static/css/style.css function_map.md
git commit -m "Build recommendation tuner modal, weight sliders JS, and presets"
git push origin main
```

---

### Week 4 • Phase 4 — Mathematical Scoring Engine, Product Attribution & Cart Workflow

**Objective**: Implement deterministic min-max normalization, weighted sum composite calculation, score breakdown transparency, and shopping cart operations.

#### Deliverables Summary
* **`Product-Catalogue-Ranked-Search`**:
  * `app/ranking/__init__.py`: Ranking blueprint registration
  * `app/ranking/engine.py`: Normalization formulas (`benefit` vs `cost`), weighted sum calculation, tie-breaking logic
  * `app/ranking/helpers.py`: Multi-criteria normalization helpers
  * `tests/test_engine.py`: Unit tests for mathematical scoring, min-max bounds, and ranking correctness
  * `app/templates/admin/product_list.html` & `product_form.html`: Product CRUD with dynamic attribute fields
* **`e-commerce-website`**:
  * `app/storefront/routes.py`: Product detail route (`/product/<slug>`), cart operations (add, update, remove), checkout route
  * `app/templates/storefront/product_detail.html`: Product detail page
  * `app/templates/storefront/cart.html`: Responsive cart view with quantity controls and order summary
  * `app/templates/storefront/order_success.html`: Order confirmation screen

#### Git Commands

##### Dev-1 (Vaibhav)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add app/ranking/__init__.py app/ranking/engine.py app/ranking/helpers.py tests/test_engine.py
git commit -m "Add ranking engine with normalization, scoring, ranking, and test suite"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add app/storefront/routes.py app/templates/storefront/product_detail.html
git commit -m "Implement cart operations, checkout logic, and product detail route"
git push origin main
```

##### Dev-2 (Shrinivas)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add app/templates/admin/product_list.html app/templates/admin/product_form.html function_map.md
git commit -m "Add product CRUD templates with dynamic attribute input fields"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add app/templates/storefront/cart.html app/templates/storefront/order_success.html function_map.md
git commit -m "Build responsive cart and order confirmation templates"
git push origin main
```

---

### Week 5 • Phase 5 — Sponsored Placement Monetization, Store Admin & B2B REST Search API

**Objective**: Build calendar-bounded sponsored placement algorithm, B2B REST Search & Ranking APIs, store admin catalog inventory, and embedded console.

#### Deliverables Summary
* **`Product-Catalogue-Ranked-Search`**:
  * `app/api/routes.py`: External B2B REST endpoints (`GET/POST /api/v1/search`, `/api/v1/categories`, `/api/v1/product/<id>`)
  * `app/insights/__init__.py` & `routes.py`: Search intelligence engine, top-searched leaderboard, query analytics
  * `app/templates/insights/index.html`: Insights search simulator, distribution chart, sensitivity analysis
  * `tests/test_api.py`: Comprehensive REST API test coverage
  * `app/templates/admin/sponsor_list.html` & `sponsor_form.html`: Sponsored placement scheduling UI
  * `tests/test_sponsor.py`: Automated tests for 1:5 placement capping and date filtering
* **`e-commerce-website`**:
  * `app/admin/__init__.py` & `routes.py`: Storefront admin blueprint, inventory dashboard, product management
  * `app/templates/admin/base.html`, `dashboard.html`, `products.html`, `product_form.html`, `login.html`: Store admin UI
  * `app/templates/admin/ranking_engine.html`: Embedded ranking engine configuration hub

#### Git Commands

##### Dev-1 (Vaibhav)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add app/api/routes.py app/insights/__init__.py app/insights/routes.py app/templates/insights/index.html tests/test_api.py
git commit -m "Add external B2B search API, query sync, and insights analytics"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add app/admin/__init__.py app/admin/routes.py app/templates/admin/product_form.html
git commit -m "Create storefront admin blueprint, product CRUD, and inventory management"
git push origin main
```

##### Dev-2 (Shrinivas)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add app/templates/admin/sponsor_list.html app/templates/admin/sponsor_form.html tests/test_sponsor.py function_map.md
git commit -m "Add sponsored placement CRUD, interleaving logic, and test suite"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add app/templates/admin/base.html app/templates/admin/dashboard.html app/templates/admin/products.html app/templates/admin/ranking_engine.html app/templates/admin/login.html function_map.md
git commit -m "Create admin dashboard layout, KPI metrics, and ranking engine hub"
git push origin main
```

---

### Week 6 • Phase 6 — Comprehensive Test Suites, Seeding, Edge-Cases & Release v1.0

**Objective**: Complete automated test suites (129 total tests), seed realistic multi-tenant data, finalize API references and integration guides, and tag v1.0.

#### Deliverables Summary
* **`Product-Catalogue-Ranked-Search`**:
  * `seed.py`: Superadmin account (`admin` / `admin123`), 2 tenant companies, 3 categories, products, search logs
  * `tests/test_routes.py`, `test_insights.py`, `test_edge_cases.py`: Zero weights, empty categories, boundary values
  * `docs/api_reference.md`: Complete OpenAPI-compliant REST specification
  * `README.md`: Polished architectural documentation
  * Tag: `v1.0-release`
* **`e-commerce-website`**:
  * `seed.py`: 16+ Noise devices across 5 categories with real-world specs, pricing, and ratings
  * `scripts/sync_engine_catalog.py`: Full catalog synchronization script bridging the website to the ranking microservice
  * `tests/test_storefront.py`, `tests/test_admin.py`: Storefront catalog, cart, and admin test suite
  * `docs/api_reference.md` & `docs/integration_guide.md`: Storefront architecture and REST integration manuals
  * Tag: `v1.0-release`

#### Git Commands

##### Dev-1 (Vaibhav)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add seed.py tests/test_routes.py tests/test_insights.py README.md
git commit -m "Add integration test suite, security hardening, seed data, and documentation polish"
git push origin main

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add seed.py scripts/sync_engine_catalog.py tests/test_storefront.py tests/test_admin.py README.md
git commit -m "Add seed catalog with 16 Noise products, sync script, and integration tests"
git push origin main
```

##### Dev-2 (Shrinivas)
```bash
# Repo 1: Product-Catalogue-Ranked-Search
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
git pull origin main
git add tests/test_edge_cases.py docs/api_reference.md function_map.md .gitignore LICENSE
git commit -m "Add edge-case test suite, API reference documentation, and release licensing"
git tag -a v1.0 -m "Release v1.0: Product Catalogue Ranked Search Microservice"
git push origin main --tags

# Repo 2: e-commerce-website
cd /home/blue/Collage-Mini-Project/e-commerce-website
git pull origin main
git add docs/api_reference.md docs/integration_guide.md function_map.md .gitignore LICENSE
git commit -m "Author API reference, system integration guide, and release tags"
git tag -a v1.0 -m "Release v1.0: Noise E-Commerce Storefront"
git push origin main --tags
```

---

## 3. How to Launch and Test Both Systems Concurrently

Both microservices should run concurrently on separate terminal tabs:

```bash
# Terminal 1: Weighted Ranking Engine (Port 5000)
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
source venv/bin/activate
python run.py

# Terminal 2: Noise Storefront (Port 8000)
cd /home/blue/Collage-Mini-Project/e-commerce-website
source venv/bin/activate
python run.py
```

### Running the Complete Automated Test Suites

```bash
# Run ranking engine tests (61 tests)
cd /home/blue/Collage-Mini-Project/Product-Catalogue-Ranked-Search
pytest -v

# Run storefront tests (68 tests)
cd /home/blue/Collage-Mini-Project/e-commerce-website
pytest -v
```
