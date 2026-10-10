# Knowledgebase — Product Catalogue Ranked Search

> Auto-maintained log of every file and code change in the project.
> Agents and developers reference this file to understand what exists and where.

## Log

| Timestamp | Phase | File | Lines | Developer | Description |
|-----------|-------|------|-------|-----------|-------------|
| 2026-09-27 | P1 | run.py | 1-15 | Dev-A | Flask entry point, imports create_app, runs debug server on port 5000 |
| 2026-09-27 | P1 | config.py | 1-35 | Dev-A | App configuration classes (Dev, Test, Prod) with SQLite/PostgreSQL URIs |
| 2026-09-27 | P1 | requirements.txt | 1-15 | Dev-A | Python dependencies: Flask, SQLAlchemy, Flask-Login, Flask-WTF, pytest |
| 2026-09-27 | P1 | app/__init__.py | 1-45 | Dev-A | Flask app factory, extension initialization (db, migrate, login_manager) |
| 2026-09-27 | P1 | app/models.py | 1-160 | Dev-A | SQLAlchemy models: User, Company, Category, Attribute, Product, ProductAttrValue, SponsoredPlacement |
| 2026-09-27 | P1 | README.md | 1-80 | Dev-A | Project overview, setup instructions, structure, credits |
| 2026-09-27 | P1 | app/templates/base.html | 1-90 | Dev-B | Base Jinja2 template with nav, flash messages, content block, footer |
| 2026-09-27 | P1 | app/static/css/style.css | 1-150 | Dev-B | Project styling: variables, layout, nav, forms, tables, cards, responsive |
| 2026-09-27 | P1 | knowledgebase.md | 1-50 | Dev-B | Project knowledge log initialized with all Phase 1 file entries |
| 2026-09-27 | P1 | function_map.md | 1-40 | Dev-B | Function-to-feature mapping initialized with Phase 1 functions |
| 2026-09-27 | P1 | docs/setup_guide.md | 1-60 | Dev-B | Detailed setup guide for development environment |
| 2026-09-27 | P2 | app/admin/__init__.py | 1-5 | Dev-B | Admin blueprint registration |
| 2026-09-27 | P2 | app/admin/routes.py | 1-60 | Dev-B | Company CRUD routes with tenant isolation |
| 2026-09-27 | P2 | app/admin/forms.py | 1-10 | Dev-B | Flask-WTF CompanyForm |
| 2026-09-27 | P2 | app/templates/admin/index.html | 1-25 | Dev-B | Admin dashboard template |
| 2026-09-27 | P2 | app/templates/admin/company_list.html | 1-30 | Dev-B | Company list template |
| 2026-09-27 | P2 | app/templates/admin/company_form.html | 1-25 | Dev-B | Company form template |
| 2026-09-27 | P3 | app/api/__init__.py | 1-3 | Dev-B | API blueprint registration |
| 2026-09-27 | P3 | app/api/routes.py | 1-50 | Dev-B | Weight total check and validation API endpoints |
| 2026-09-27 | P3 | app/static/js/weight_check.js | 1-70 | Dev-B | Live weight total JS indicator |
| 2026-09-27 | P3 | tests/test_models.py | 1-70 | Dev-B | Unit tests for weight validation |
| 2026-09-27 | P4 | app/admin/routes.py | ~100 | Dev-B | Product CRUD routes added |
| 2026-09-27 | P4 | app/templates/admin/product_list.html | 1-52 | Dev-B | Product listing template with score display |
| 2026-09-27 | P4 | app/templates/admin/product_form.html | 1-46 | Dev-B | Product add/edit form with dynamic attributes |
| 2026-09-27 | P5 | app/admin/routes.py | ~80 | Dev-B | Sponsored placement CRUD routes |
| 2026-09-27 | P5 | app/admin/forms.py | ~20 | Dev-B | SponsorForm added |
| 2026-09-27 | P5 | app/templates/admin/sponsor_list.html | 1-45 | Dev-B | Sponsored placement listing template |
| 2026-09-27 | P5 | app/templates/admin/sponsor_form.html | 1-48 | Dev-B | Sponsored placement form template |
| 2026-09-27 | P5 | app/ranking/helpers.py | ~60 | Dev-B | Sponsored product insertion algorithm |
| 2026-09-27 | P5 | tests/test_sponsor.py | 1-105 | Dev-B | Unit tests for sponsored placement algorithms |
| 2026-09-27 | P6 | tests/test_routes.py | 1-204 | Dev-A | Integration tests: auth, admin, storefront login requirements, full workflow |
| 2026-09-27 | P6 | tests/test_edge_cases.py | 1-80 | Dev-B | Edge case tests: empty category, zero weight, boundary values |
| 2026-09-27 | P6 | tests/conftest.py | 1-26 | Dev-A | Shared pytest fixtures (app, client) for all test modules |
| 2026-09-27 | P6 | seed.py | 1-124 | Dev-A | Demo data script: 2 categories, 12 products, 1 sponsor |
| 2026-09-27 | P6 | docs/api_reference.md | 1-100 | Dev-B | Full API endpoint documentation |
| 2026-09-27 | P6 | .gitignore | 1-9 | Dev-B | Git ignore rules for caches, DB, env files |
| 2026-09-27 | P6 | LICENSE | 1-21 | Dev-B | Proprietary commercial license file |
| 2026-09-27 | P7 | app/models.py | 1-151 | Dev-A | Added is_superadmin to User, search_count to Product, and SearchLog analytics model |
| 2026-09-27 | P7 | app/admin/routes.py | 1-490 | Dev-A | Superadmin Platform console, company account provisioning, cascade delete, inspection switcher |
| 2026-09-27 | P7 | app/admin/forms.py | 1-40 | Dev-A | Added CompanyAccountForm with manager username, email, and password fields |
| 2026-09-27 | P7 | app/insights/routes.py | 1-160 | Dev-A | Insights engine: interactive search, hit counters, leaderboards, sensitivity & anti-bias metrics |
| 2026-09-27 | P7 | seed.py | 1-205 | Dev-A | Multi-tenant demo dataset: Superadmin, 2 tenant companies, 3 categories, search logs |
| 2026-09-27 | P7 | tests/test_insights.py | 1-72 | Dev-A | Test suite for search logging, hit incrementing, category filters, and sponsor ratio checks |
| 2026-09-27 | P7 | app/__init__.py | 1-93 | Dev-B | Retired storefront blueprint, registered insights blueprint under /insights |
| 2026-09-27 | P7 | app/templates/base.html | 1-95 | Dev-B | Replaced storefront with Insights nav, dynamic [SUPERADMIN] and [TENANT] role pills |
| 2026-09-27 | P7 | app/templates/admin/platform_dashboard.html | 1-135 | Dev-B | Super Admin Platform Console: global KPIs, company directory, and inspection shortcuts |
| 2026-09-27 | P7 | app/templates/admin/company_form.html | 1-70 | Dev-B | Company provisioning form with initial manager credentials |
| 2026-09-27 | P7 | app/templates/admin/category_header.html | 1-90 | Dev-B | Inspection mode alert banner and link updates to Insights |
| 2026-09-27 | P7 | app/templates/insights/index.html | 1-331 | Dev-B | Full Insights dashboard: search simulator, leaderboard, domain stats, weight sensitivity, sponsor ratio |


## UI Fix Log

| Timestamp | File | Developer | Problem | Solution |
|-----------|------|-----------|---------|----------|
| 2026-09-27 | app/templates/admin/index.html | Dev-A | Dashboard cards had dead links (href="#") | Replaced with proper url_for() links to categories, products, sponsors |
| 2026-09-27 | app/templates/admin/category_list.html | Dev-A | Missing Products and Sponsors action buttons | Added Products and Sponsors buttons with proper routing |
| 2026-09-27 | app/templates/admin/company_list.html | Dev-A | Used company.id instead of company.company_id | Fixed FK reference to use company_id (PK column name) |
| 2026-09-27 | app/templates/admin/product_list.html | Dev-A | Missing CSRF token on delete form, no back navigation | Added CSRF token and back-to-categories link |
| 2026-09-27 | app/templates/admin/sponsor_list.html | Dev-A | No back navigation, unclear active/expired status | Added back link, improved status display |
| 2026-09-27 | app/templates/admin/attribute_list.html | Dev-A | Weight total JS IDs didn't match weight_check.js | Updated to use category-id, weight-total-value, weight-total-status IDs |
| 2026-09-27 | All admin form templates | Dev-A | No cancel/back buttons on form pages | Added consistent back navigation and cancel buttons |
| 2026-09-27 | app/static/css/style.css | Dev-B | Missing btn-sm, btn-info, btn-warning, d-inline, d-flex, form-control, form-container classes | Complete CSS rewrite with all utility classes |
| 2026-09-27 | app/static/css/style.css | Dev-B | Duplicate .badge-sponsored rules | Consolidated into single clean rule |
| 2026-09-27 | app/templates/storefront/categories.html | Dev-B | Poor card layout, no grid | Replaced with responsive .category-grid layout |
| 2026-09-27 | app/templates/storefront/results.html | Dev-B | Inconsistent result display, poor filter bar | Rewrote with .result-card, .filter-bar, sponsored highlighting |
| 2026-09-27 | app/templates/storefront/product_detail.html | Dev-B | No back navigation, score not formatted as percentage | Added back link, multiplied score by 100 for display |

## Usability & Placement Overhaul Log

| Timestamp | Component / File | Developer | Problem Faced | Solution Applied |
|-----------|------------------|-----------|---------------|------------------|
| 2026-09-27 | `app/ranking/helpers.py` | Dev-A (Vaibhav) | Lack of structured backend category stats and sponsor status for cohesive hub navigation | Added `get_category_stats()`, `get_sponsor_status()`, and normalized percentage metrics in `get_score_breakdown()` |
| 2026-09-27 | `app/admin/routes.py` | Dev-A (Vaibhav) | Disjointed navigation between category attributes, products, and sponsors requiring constant back-and-forth | Created `@admin.route('/category/<id>/overview')` command center; injected category stats into all category sub-routes |
| 2026-09-27 | `app/templates/admin/category_header.html` | Dev-A (Vaibhav) | Inconsistent sub-page headers and lack of contextual category navigation tabs | Built shared Category Hub header with unified breadcrumbs, KPI health pills, and sub-nav tabs (`Overview`, `Attributes`, `Products`, `Sponsors`, `Settings`) |
| 2026-09-27 | `app/templates/admin/category_overview.html` | Dev-A (Vaibhav) | Admins had no quick way to assess category health, top products, or weight validation | Designed category command center template featuring KPI cards, top-ranked products preview, and criteria weight health meter |
| 2026-09-27 | `config.py` | Dev-A (Vaibhav) | Form submissions in integration test suite blocked by missing CSRF tokens in testing mode | Added `WTF_CSRF_ENABLED = False` to `TestingConfig` per Flask best practices |
| 2026-09-27 | `tests/test_routes.py` | Dev-A (Vaibhav) | Category Hub Overview route lacked automated test coverage | Implemented `test_category_overview_route` integration test |
| 2026-09-27 | `app/static/css/style.css` | Dev-B (Shrinivas) | Clunky, unpolished UI with misaligned buttons, poor spacing, and lack of visual hierarchy | Complete CSS design system overhaul: Inter typography, Category Hub tabs, KPI cards, rank medals (Gold/Silver/Bronze), clean tables, and responsive grids |
| 2026-09-27 | `app/templates/base.html` | Dev-B (Shrinivas) | Dated navbar without clear active user identification or modern SaaS branding | Upgraded navbar with `RankEngine PRO` logo, active user pill, clean alert icons, and professional footer |
| 2026-09-27 | `app/templates/admin/index.html` | Dev-B (Shrinivas) | Dashboard displayed dead links and lacked high-level operational metrics | Transformed into executive dashboard with live KPI metric cards (Total Products, Categories, Weights, Sponsors) and direct category cards |
| 2026-09-27 | `app/templates/admin/category_list.html` | Dev-B (Shrinivas) | 5 action buttons jammed into a single table cell causing cluttered visual layout and misclicks | Redesigned with inventory badges, weight health indicators, primary `Manage Hub` action, and clean button groups |
| 2026-09-27 | `app/templates/admin/attribute_list.html` | Dev-B (Shrinivas) | Static numeric weight sum lacked intuitive visual feedback on the 100% allocation rule | Integrated visual progress meter (`valid`/`invalid`/`danger`), range tags, and lower-is-better indicator pills |
| 2026-09-27 | `app/templates/admin/product_list.html` | Dev-B (Shrinivas) | Product list lacked rank indicators, score progress bars, and visible attribute measurements | Integrated rank pills (#1, #2...), mini score bars, attribute value tags, and Category Hub tabs |
| 2026-09-27 | `app/templates/admin/sponsor_list.html` | Dev-B (Shrinivas) | Ambiguous active/scheduled/expired status and lack of slot placement policy clarity | Added status badges (Active Now / Scheduled / Expired) with remaining days, policy callout, and Category Hub tabs |
| 2026-09-27 | `app/templates/admin/product_form.html` & forms | Dev-B (Shrinivas) | Admin forms had poor element placement without allowable range guidelines | Redesigned with breadcrumbs, sectioned form cards, inline range pills, and lower-is-better explanation callouts |
| 2026-09-27 | `app/templates/storefront/categories.html` | Dev-B (Shrinivas) | Storefront categories had empty whitespace and plain floating cards | Redesigned with hero banner, feature badges, interactive store cards, and ranking algorithm explainer widget |
| 2026-09-27 | `app/templates/storefront/results.html` | Dev-B (Shrinivas) | Misaligned filter bar and uninspired product ranking cards | Redesigned with horizontal filter card, Gold/Silver/Bronze medals, prominent ⭐ SPONSORED badges, and direct breakdown links |
| 2026-09-27 | `app/templates/storefront/product_detail.html` | Dev-B (Shrinivas) | Unformatted table without visual representation of attribute contribution to composite score | Redesigned with score hero gauge, normalization progress bars, percentage contribution bars, and transparent formula card |
| 2026-09-27 | `app/static/js/weight_check.js` | Dev-B (Shrinivas) | JavaScript weight check only updated raw text without visual progress bar animation | Enhanced script to dynamically update progress bar fill width and color class (success/warning/danger) in real-time |

## Technical Minimalist Design System Log

| Timestamp | Component / File | Developer | Problem Faced | Solution Applied |
|-----------|------------------|-----------|---------------|------------------|
| 2026-09-27 | `app/templates/base.html` | Dev-A (Vaibhav) | Fonts did not match the Technical Minimalist specification (lacked Space Grotesk, General Sans, JetBrains Mono) | Loaded Space Grotesk (Google Fonts), General Sans (Fontshare CDN), and JetBrains Mono; updated brand header to `[R//E] RANK_ENGINE v1.0` |
| 2026-09-27 | `app/templates/index.html` | Dev-A (Vaibhav) | Landing page lacked technical minimalist typography hierarchy and system specifications bar | Redesigned with Space Grotesk tight tracking headers (line-height 0.95), JetBrains Mono module tags (`[MODULE_01 // CRITERIA]`), and flat specification callouts |
| 2026-09-27 | `app/templates/storefront/categories.html` | Dev-A (Vaibhav) | Storefront categories had generic badges and non-technical card layout | Applied `[CAT_XX]` system labels, JetBrains Mono metadata chips, and flat 1px hairline border cards |
| 2026-09-27 | `app/templates/storefront/results.html` | Dev-A (Vaibhav) | Results displayed emojis instead of technical minimalist rank glyphs | Switched to flat monospaced rank markers (`[#01]`, `[#02]`, `[#03]`) and `[SPONSORED]` badges without emoji characters |
| 2026-09-27 | `app/templates/admin/category_header.html` | Dev-A (Vaibhav) | Category Hub tabs had rounded badges and emojis incompatible with technical minimalist guidelines | Updated tabs to flat monospaced labels (`[OVERVIEW]`, `[ATTRIBUTES]`, `[PRODUCTS]`, `[SPONSORS]`, `[SETTINGS]`) |
| 2026-09-27 | `app/templates/admin/index.html` | Dev-A (Vaibhav) | Dashboard cards lacked monospaced technical metadata indexes | Updated KPI cards with `[01]` through `[04]` indexes, Space Grotesk values, and technical shortcut brackets (`[HUB]`, `[WEIGHTS]`) |
| 2026-09-27 | `app/static/css/style.css` | Dev-B (Shrinivas) | Previous stylesheet had depth effects (box-shadows, gradients, large border-radii) violating Technical Minimalist spec | Rebuilt entire design system with Paper (`#F7F7F5`), Forest (`#1A3C2B`), Grid 1px hairlines (`#3A3A38` at 20% opacity), Coral (`#FF8C69`), Mint (`#9EFFBF`), and Gold (`#F4D35E`) |
| 2026-09-27 | `app/static/css/style.css` | Dev-B (Shrinivas) | Components had rounded border radii (4px-8px) and box shadows | Enforced strict `border-radius: 2px !important;` and `box-shadow: none !important;` across all elements |
| 2026-09-27 | `app/static/css/style.css` | Dev-B (Shrinivas) | Micro-interactions had standard slow transitions | Enforced snappy linear micro-interactions (`0.12s linear`) and image `mix-blend-luminosity` (90% opacity shifting to full on hover) |

## Access Control & Security Hardening Log

| Timestamp | Component / File | Developer | Problem Faced | Solution Applied |
|-----------|------------------|-----------|---------------|------------------|
| 2026-09-27 | `app/storefront/routes.py` | Dev-A (Vaibhav) | Unauthenticated visitors could access `GET /storefront/category/<id>` and `/storefront/product/<id>`, exposing proprietary calculated scores and competitor rankings without logging in | Decorated both `category_results` and `product_detail` route handlers with Flask-Login `@login_required`, triggering automated HTTP 302 redirection to `/auth/login?next=...` |
| 2026-09-27 | `tests/test_routes.py` | Dev-A (Vaibhav) | No automated test coverage validating route-level authentication guards on storefront ranking endpoints | Added `test_storefront_category_requires_login`, `test_storefront_product_detail_requires_login`, and `test_storefront_authenticated_access` tests to verify 302 redirects and 200 responses |
| 2026-09-27 | `knowledgebase.md` & `function_map.md` | Dev-B (Shrinivas) | Audit trail and function registry lacked documentation of access control rules on storefront routes | Updated documentation logs and function specifications documenting `@login_required` enforcement on ranking views |

## Platform Superadmin, Multi-Tenancy & Insights Engine Log

| Timestamp | Component / File | Developer | Problem Faced | Solution Applied |
|-----------|------------------|-----------|---------------|------------------|
| 2026-09-27 | `app/models.py` | Dev-A (Vaibhav) | Lack of platform superadmin role, missing product search metrics, and no tracking model for search query intelligence | Added `is_superadmin` flag to `User`, `search_count` counter to `Product`, and created `SearchLog` model (`query_text`, `category_id`, `results_count`, `searched_at`) |
| 2026-09-27 | `app/admin/routes.py` | Dev-A (Vaibhav) | Admin console was restricted to a single hardcoded company view without tenant management, account provisioning, or tenant inspection capabilities | Rebuilt `/admin/` with dynamic branching: Superadmins receive the multi-tenant console (`platform_dashboard.html`); added company creation with manager account provisioning (`/company/new`), cascade deletion (`/company/<id>/delete`), and tenant inspection context switcher (`/company/<id>/inspect` & `exit-inspect`) |
| 2026-09-27 | `app/admin/forms.py` | Dev-A (Vaibhav) | Company creation form only took company name, leaving company manager user accounts unprovisioned | Created `CompanyAccountForm` adding `admin_username`, `admin_email`, and `admin_password` fields |
| 2026-09-27 | `app/insights/routes.py` | Dev-A (Vaibhav) | Legacy storefront lacked search intelligence, query tracking, and cross-category multi-criteria analytics | Built Insights Engine with real-time multi-criteria search (`apply_tiebreak_sort`), search hit counters, top-searched leaderboard, category engagement distribution, criteria weight sensitivity analysis, and anti-bias sponsor ratio calculations |
| 2026-09-27 | `seed.py` | Dev-A (Vaibhav) | Seed script only populated 1 company and lacked superadmin credentials or search log records | Updated seed script to generate Root Superadmin (`admin` / `admin123`), 2 tenant companies (TechMart Electronics & Apex Audio Labs), managers, 3 distinct domain categories, and realistic search query logs |
| 2026-09-27 | `tests/test_insights.py` & `test_routes.py` | Dev-A (Vaibhav) | No automated test coverage for superadmin company management, tenant isolation, or insights engine | Authored 9 new automated tests covering platform dashboard, company provisioning, cascade deletion, inspection mode, tenant isolation, search query execution, and sponsor compliance |
| 2026-09-27 | `app/__init__.py` | Dev-B (Shrinivas) | Legacy storefront blueprint was registered while new insights blueprint was inactive | Retired storefront blueprint registration and registered `insights` blueprint under `/insights` |
| 2026-09-27 | `app/templates/base.html` | Dev-B (Shrinivas) | Top navigation still pointed to legacy storefront and lacked visual indication of platform superadmin vs tenant roles | Replaced Storefront nav link with Insights (`/insights/`), added dynamic role pills (`[ROOT: admin]` vs `[TENANT: name]`), and integrated top inspection mode status indicator |
| 2026-09-27 | `app/templates/admin/platform_dashboard.html` | Dev-B (Shrinivas) | Superadmins had no centralized matrix to view all tenant organizations, provision accounts, or inspect tenant data | Designed Platform Admin Console with global KPIs (Total Tenants, Domains, Products, Placements), comprehensive tenant directory table, and quick actions (`[INSPECT DATA]`, `[EDIT]`, `[DELETE]`) |
| 2026-09-27 | `app/templates/admin/company_form.html` | Dev-B (Shrinivas) | Form styling was basic and lacked manager account credentials section | Redesigned with Technical Minimalist aesthetics, organizational specification section, and initial manager account credentials card |
| 2026-09-27 | `app/templates/admin/category_header.html` & `index.html` | Dev-B (Shrinivas) | Admins lacked persistent visual feedback when inspecting tenant companies and links still pointed to old storefront | Added prominent `[SUPERADMIN INSPECTION ACTIVE]` top alert bar with one-click `[EXIT INSPECTION ×]` action and updated storefront links to Insights |
| 2026-09-27 | `app/templates/insights/index.html` | Dev-B (Shrinivas) | No user interface existed for search analytics, product popularity, or sensitivity exploration | Designed full Technical Minimalist Insights Dashboard featuring interactive catalog search bar, dynamic results matrix, popularity leaderboard, domain engagement meters, criteria distribution table, and anti-bias sponsor compliance gauge |

## Bug Fixes & Refinements: Smooth Tab Transitions, Universal Tables & Route Repair Log

| Timestamp | Component / File | Developer | Problem Faced | Solution Applied |
|-----------|------------------|-----------|---------------|------------------|
| 2026-09-27 | `app/templates/admin/category_overview.html` & `product_list.html` | Dev-A (Vaibhav) | Clicking domain sub-categories in Company Hub crashed with `BuildError: Could not build url for endpoint 'storefront.product_detail'` | Replaced deprecated `storefront.product_detail` and `storefront.category_results` links with active `insights.index` links; removed deleted blueprint references |
| 2026-09-27 | `app/templates/admin/platform_dashboard.html` | Dev-A (Vaibhav) | Redundant `SYSTEM INSIGHTS ↗` button on Platform Admin page cluttered the tenant header when the navbar already provides an Insights link | Removed redundant button from platform header, maintaining single clean entry point in top navigation bar |
| 2026-09-27 | `app/static/css/style.css` | Dev-B (Shrinivas) | Tab switching animation was annoying, jarring, and stuttered due to `transition: all` triggering layout reflows on render and hover | Refined `.hub-tab`, `.nav-link`, and `.btn` transitions to target explicit properties (`background-color`, `color`, `border-color`, `opacity`) with smooth cubic-bezier easing (`0.15s ease-out` / `0.2s cubic-bezier(0.16, 1, 0.3, 1)`) |
| 2026-09-27 | `app/static/css/style.css` | Dev-B (Shrinivas) | Universal reset `* { margin: 0; padding: 0; }` combined with unstyled `.table` caused text to collide (e.g. `Wireless Earbuds546 HITS`) with 0 cell padding across all pages | Defined universal styling for `table`, `.table`, and `.table-clean` with generous cell padding (`0.85rem 1.15rem`), crisp 1px hairline dividers, subtle row hover highlight, and added `.text-end`, `.text-start`, `.w-100`, and `.meta-tag` utility classes |
| 2026-09-27 | `app/templates/insights/index.html` & `admin/company_list.html` | Dev-B (Shrinivas) | Text blocks and category domain hits lacked table organization, leading to squished, unreadable statistics | Refactored domain search distribution and sponsor ratio statistics into clean, spacious tables; modernized `company_list.html` to match the Technical Minimalist specification |

## Tenant-Scoped Insights, Binary (Yes/No) Attributes & Credentials Removal Log

| Timestamp | Component / File | Developer | Problem Faced | Solution Applied |
|-----------|------------------|-----------|---------------|------------------|
| 2026-09-27 | `app/templates/index.html` | Dev-B (Shrinivas) | Hardcoded `OPERATOR CREDENTIALS` and `CATALOG PRESETS` banner cluttered the bottom of the public landing page | Removed lines 69-77 from `app/templates/index.html`, keeping the landing page clean and professional |
| 2026-09-27 | `app/insights/routes.py` | Dev-A (Vaibhav) | When `apex_admin` deleted all categories/products, visiting `/insights/` exposed other tenant companies' categories and products due to unscoped queries | Scoped all category, product, attribute, search log, and sponsor queries to `current_user.company_id` (or `inspect_company_id` for superadmin); returns empty collections when tenant catalog is deleted |
| 2026-09-27 | `app/templates/insights/index.html` | Dev-B (Shrinivas) | Insights dashboard lacked visual tenant identity context and failed to inform users when their tenant catalog was completely empty | Added `[TENANT: <Name>]` status badge in header and built a dedicated Technical Minimalist empty state card (`NO CATALOG DATA FOUND`) with a direct action link to `[+ CREATE FIRST CATEGORY]` |
| 2026-09-27 | `app/admin/forms.py` | Dev-A (Vaibhav) | `AttributeForm` only provided a single `numeric` choice and strictly required `min_value` and `max_value` fields | Added `('binary', 'Binary (Yes / No)')` choice to `data_type` select field and made `min_value` / `max_value` validators use `Optional()` |
| 2026-09-27 | `app/admin/routes.py` | Dev-A (Vaibhav) | Backend routes did not automatically handle scale boundaries or input validation for binary attributes | Updated `new_attribute` and `edit_attribute` to automatically set `min_value = 0.0` and `max_value = 1.0` when `data_type == 'binary'`, and validated product binary inputs (`1.0` for Yes, `0.0` for No) |
| 2026-09-27 | `app/templates/admin/attribute_form.html` | Dev-B (Shrinivas) | Admin attribute creation form displayed irrelevant numeric min/max inputs when configuring a binary attribute | Added dynamic JavaScript toggle to hide min/max range fields when `Binary` is selected, showing a dedicated informational helper callout |
| 2026-09-27 | `app/templates/admin/attribute_list.html` & `category_overview.html` | Dev-B (Shrinivas) | Attributes list showed generic `0.0 – 1.0` range for binary attributes instead of intuitive Yes/No labels | Updated tables to display `Binary (Yes/No)` badge and `Yes / No` scale tags |
| 2026-09-27 | `app/templates/admin/product_form.html` & `product_list.html` | Dev-B (Shrinivas) | Product creation required entering raw numbers (`1` or `0`) for binary criteria, and product lists displayed raw float values | Rendered dedicated `[YES]` / `[NO]` radio selector cards in `product_form.html`, and rendered styled `YES` (mint) / `NO` (neutral) badges in `product_list.html` |
| 2026-09-27 | `tests/` | Dev-A (Vaibhav) | No automated test coverage for tenant-scoped insights or binary attribute normalization | Authored unit and integration tests (`test_tenant_insights_isolation`, `test_tenant_insights_empty_catalog`, `test_binary_attribute_normalization`, `test_binary_attribute_weighted_sum`, `test_binary_attribute_creation_and_product_ranking`) bringing test suite to 50/50 passing |

## Superadmin Password Management, Company Administration Hardening & B2B Search API Engine Log

| Timestamp | Component / File | Developer | Problem Faced | Solution Applied |
|-----------|------------------|-----------|---------------|------------------|
| 2026-09-27 | `app/auth/routes.py` | Dev-A (Vaibhav) | Public registration allowed arbitrary users to register and create companies, violating tenant provisioning security | Disabled `/auth/register` for GET and POST; redirects to `/auth/login` with warning indicating tenant accounts are provisioned exclusively by platform administrators |
| 2026-09-27 | `app/admin/routes.py` | Dev-A (Vaibhav) | Standard tenant managers could access company editing and creation routes, and admins had no mechanism to reset tenant user passwords | Gated `new_company`, `edit_company`, `delete_company`, and `list_companies` strictly with `@superadmin_required`; created `reset_user_password(company_id, user_id)` allowing root admins to change tenant user credentials |
| 2026-09-27 | `app/admin/forms.py` | Dev-A (Vaibhav) | Missing administrative form for direct user password updates | Created `UserPasswordResetForm` with `new_password` and `confirm_password` fields using `EqualTo` validator and minimum length constraints |
| 2026-09-27 | `app/ranking/engine.py` & `helpers.py` | Dev-A (Vaibhav) | Unchecked null values for `composite_score`, `raw_value`, or timestamps could cause unhandled `TypeError` exceptions during tie-breaking | Added defensive fallback guards in `normalize_value`, `rank_products`, and `apply_tiebreak_sort` ensuring complete mathematical stability |
| 2026-09-27 | `app/admin/routes.py` | Dev-A (Vaibhav) | Deleting a product or category with active/expired sponsored placements or search logs triggered foreign key integrity errors | Added explicit cleanup of `SponsoredPlacement`, `ProductAttrValue`, child products, and disassociated `SearchLog` references before deletion |
| 2026-09-27 | `app/api/routes.py` | Dev-A (Vaibhav) | The platform lacked an external REST API allowing third-party client companies to utilize our engine for their search and ranking operations | Engineered multi-tenant REST API (`GET/POST /api/v1/search`, `GET /api/v1/categories`, `GET /api/v1/product/<id>`) supporting free-text search, dynamic customer preference weights, deterministic tie-breaking, and 1:5 capped sponsor placement interleaving |
| 2026-09-27 | `tests/test_api.py` & `test_routes.py` | Dev-A (Vaibhav) | No automated tests existed for the new external B2B search API or superadmin password reset workflows | Authored `tests/test_api.py` (9 tests) and updated `tests/test_routes.py` covering disabled registration, duplicate provisioning rejection, password reset, and access restrictions; all 61 tests passing |
| 2026-09-27 | `app/templates/auth/login.html` | Dev-B (Shrinivas) | Login page displayed a public "Click to Register!" link contrary to administrator-provisioned tenant policy | Removed registration link and added Technical Minimalist access notice explaining administrator account provisioning |
| 2026-09-27 | `app/templates/admin/user_password_reset.html` | Dev-B (Shrinivas) | Superadmins had no user interface to reset credentials for tenant managers | Designed dedicated Technical Minimalist password reset page featuring target operator metrics matrix, password confirmation inputs, and clean action buttons |
| 2026-09-27 | `app/templates/admin/platform_dashboard.html` | Dev-B (Shrinivas) | Platform Superadmin Tenant Directory displayed user names as static badges without quick administrative actions | Added `[RESET PWD]` button next to each manager account badge with direct linkage to the password reset view |
| 2026-09-27 | `app/templates/admin/company_form.html` | Dev-B (Shrinivas) | Superadmins editing an organization had no visibility into assigned user accounts or password management | Added assigned operator accounts summary card with direct `[RESET PWD →]` action buttons when editing a company |
| 2026-09-27 | `app/templates/admin/index.html` | Dev-B (Shrinivas) | Company Console header displayed a "TENANT SETTINGS" button that confused tenant operators who are not authorized to edit companies | Removed "TENANT SETTINGS" link, keeping company operators focused exclusively on their domain categories, attributes, and products |
| 2026-09-27 | `docs/api_reference.md` | Dev-B (Shrinivas) | External companies integrating with our engine had no documentation for querying search and ranking endpoints | Wrote complete API reference guide including endpoint specifications, request parameters, JSON response schemas, dynamic preference overrides, error codes, and curl/Python integration examples |
| 2026-09-27 | `function_map.md` & `knowledgebase.md` | Dev-B (Shrinivas) | Newly implemented functions and security decorators were not documented in the project maps | Updated function map with `superadmin_required`, `reset_user_password`, `search_products`, `get_categories`, `get_product`, and documented 50/50 developer task audit |

## Title Alignment, FR-21 Attribute Range Filtering & SRS Audit Log

| Timestamp | Component / File | Developer | Problem Faced | Solution Applied |
|-----------|------------------|-----------|---------------|------------------|
| 2026-10-03 | `app/templates/` (`base.html`, `index.html`, `admin/*.html`, `insights/index.html`) | Dev-B (Shrinivas) | Title and branding across templates inconsistently used "Weighted Ranking Engine" instead of standardized "Weighted Ranking Engine For Products" | Updated `<title>` tags and header typography across all Jinja2 templates to "Weighted Ranking Engine For Products" |
| 2026-10-03 | `app/templates/insights/index.html` | Dev-B (Shrinivas) | Insights interactive search form lacked user-facing controls for pre-ranking attribute range filtering (FR-21) | Integrated Technical Minimalist attribute range filter controls (attribute selector dropdown, min number input, max number input) with 1px hairline styling and active filter indicators |
| 2026-10-03 | `tests/test_insights.py` | Dev-B (Shrinivas) | No explicit automated test verified the FR-21 attribute range filter within the catalog insights simulation | Authored `test_insights_attribute_range_filter` verifying threshold filtering before ranking; verified full test suite passes |
| 2026-10-03 | `README.md`, `docs/setup_guide.md`, `docs/api_reference.md`, `planning.md` | Dev-B (Shrinivas) | Project documentation needed alignment with finalized project title and new system capabilities | Synchronized title to "Weighted Ranking Engine For Products", documented FR-21 attribute range filtering, binary boolean attributes (0.0/1.0 scale), and Platform Superadmin password reset |
| 2026-10-03 | `SRS_Weighted_Ranking_Engine.odt` | Dev-B (Shrinivas) | SRS document required alignment with built application (title, Binary criteria, Platform Superadmin password reset, B2B REST API, updated data model, FR-21, zero credentials) | Updated document title in `content.xml`, `styles.xml`, and Appendix A; updated Sections 1.2, 2.3, 3.1, 3.5, 4.4, and 6.2 Data Model; repackaged cleanly without XML corruption |
| 2026-10-03 | Full Project Title Standardization | Dev-B (Shrinivas) | System title unified across all templates, documentation, API references, and SRS specifications to "Product Catalogue Ranked Search" | Updated `<title>` tags, headers, footers in templates, documentation titles in `README.md`, `setup_guide.md`, `api_reference.md`, `planning.md`, `function_map.md`, and SRS ODT (`content.xml`, `styles.xml`, Appendix A) |





