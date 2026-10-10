# Function Map — Product Catalogue Ranked Search

> Maps every function/method to its file, line number, FR requirement, feature area, and description.
> Agents reference this to understand what each function does and where it's used.

## Functions

| Function | File | Line | FR(s) | Feature | Description |
|----------|------|------|-------|---------|-------------|
| create_app() | app/__init__.py | 10 | — | Bootstrap | Flask app factory; initializes extensions, registers blueprints |
| User.set_password() | app/models.py | 25 | NFR-5.2 | Security | Hashes password using Werkzeug generate_password_hash |
| User.check_password() | app/models.py | 30 | NFR-5.2 | Security | Verifies password against stored hash |
| load_user() | app/models.py | 35 | — | Auth | Flask-Login user loader callback |
| Company.__repr__() | app/models.py | 50 | — | Debug | String representation of Company model |
| Category.__repr__() | app/models.py | 65 | — | Debug | String representation of Category model |
| Attribute.__repr__() | app/models.py | 90 | — | Debug | String representation of Attribute model |
| Product.__repr__() | app/models.py | 115 | — | Debug | String representation of Product model |
| admin_before_request() | app/admin/routes.py | 10 | FR-19 | Tenant Isolation | Sets g.company_id from current user for data isolation |
| company_required() | app/admin/routes.py | 15 | FR-19 | Auth | Decorator to check user is assigned to a company |
| index() | app/admin/routes.py | 35 | FR-20 | Console Routing | Dynamic branching: Superadmin Platform Console vs Company Operations Hub |
| list_companies() | app/admin/routes.py | 95 | FR-20 | Company Management | Lists companies (all companies for Superadmin, isolated for tenant) |
| new_company() | app/admin/routes.py | 103 | FR-20 | Account Provisioning | Creates company and provisions initial manager account credentials |
| edit_company() | app/admin/routes.py | 134 | FR-20 | Company Management | Updates company organization details |
| delete_company() | app/admin/routes.py | 150 | FR-20 | Platform Admin | Cascade deletes company, categories, products, attributes, sponsors, and users |
| inspect_company() | app/admin/routes.py | 179 | FR-20 | Platform Admin | Context switcher: allows Superadmin to inspect and manage a selected tenant |
| exit_inspect() | app/admin/routes.py | 188 | FR-20 | Platform Admin | Clears inspection session and returns Superadmin to platform directory |
| weight_total() | app/api/routes.py | ... | FR-3, NFR-5.1 | Weight Validation | Returns sum of active weights for a category |
| weight_validate() | app/api/routes.py | ... | FR-3 | Weight Validation | Validates projected weight total |
| fetchWeightTotal() | app/static/js/weight_check.js | ... | FR-3 | Weight UI | Fetches weight total from API |
| calculateLocalTotal() | app/static/js/weight_check.js | ... | FR-3 | Weight UI | Client-side weight sum calculation |
| list_products() | app/admin/routes.py | ... | FR-7 | Product CRUD | List all products in a category |
| new_product() | app/admin/routes.py | ... | FR-5, FR-6 | Product CRUD | Add a new product and attributes |
| edit_product() | app/admin/routes.py | ... | FR-7, FR-8 | Product CRUD | Edit an existing product and attributes |
| delete_product() | app/admin/routes.py | ... | FR-7 | Product CRUD | Delete a product and its attributes |
| list_sponsors() | app/admin/routes.py | ... | FR-14 | Sponsorship | List all sponsored placements in a category |
| new_sponsor() | app/admin/routes.py | ... | FR-14 | Sponsorship | Create a new sponsored placement |
| edit_sponsor() | app/admin/routes.py | ... | FR-14 | Sponsorship | Edit an existing sponsored placement |
| delete_sponsor() | app/admin/routes.py | ... | FR-14 | Sponsorship | Delete a sponsored placement |
| insert_sponsored_placements() | app/ranking/helpers.py | ... | FR-15, NFR-5.6 | Sponsorship Logic | Insert sponsored products into organic rankings |
| get_active_sponsored_products() | app/ranking/helpers.py | ... | FR-17 | Sponsorship Logic | Get currently active sponsored products |
| get_sponsor_status() | app/ranking/helpers.py | ... | FR-14, FR-17 | Usability / UI | Computes active/scheduled/expired status, badge class, and message |
| get_category_stats() | app/ranking/helpers.py | ... | FR-20, FR-3 | Category Hub | Aggregates product count, attribute count, weight total, and sponsor metrics |
| category_overview() | app/admin/routes.py | ... | FR-20 | Category Hub | Unified category command center view with metrics and quick shortcuts |
| insights_index() | app/insights/routes.py | 18 | FR-12, FR-19, FR-20 | Insights Engine | Multi-criteria catalog search, search hit telemetry, leaderboard, sponsor ratio checks, and strict multi-tenant isolation |
| normalize_value() | app/ranking/engine.py | 1 | FR-9, FR-4 | Normalization Engine | Min-Max scaling handling continuous numeric attributes and discrete binary (Yes=1.0, No=0.0) criteria with directionality |
| superadmin_required() | app/admin/routes.py | 38 | FR-20 | Access Control | Security decorator ensuring platform-level administrative privileges |
| reset_user_password() | app/admin/routes.py | 170 | FR-20, NFR-5.2 | Account Security | Platform Superadmin route to change any tenant company user's password |
| get_request_company_id() | app/api/routes.py | 10 | FR-19, FR-21 | B2B API Engine | Extracts and validates tenant company ID from query string, headers, or JSON body |
| search_products() | app/api/routes.py | 70 | FR-12, FR-13, FR-15, FR-21 | B2B API Engine | Multi-tenant search and ranking REST endpoint with dynamic weights and sponsor interleaving |
| get_categories() | app/api/routes.py | 290 | FR-2, FR-4, FR-21 | B2B API Engine | Schema endpoint returning categories, attributes, scales, and data types |
| get_product() | app/api/routes.py | 340 | FR-7, FR-10, FR-21 | B2B API Engine | Product detail endpoint returning composite score, attributes, and mathematical breakdown |
| UserPasswordResetForm | app/admin/forms.py | 42 | NFR-5.2 | Forms | Form for platform administrator to securely reset tenant operator passwords |
| test_insights_attribute_range_filter() | tests/test_insights.py | 134 | FR-21 | Automated Testing | Unit test verifying attribute threshold range filtering in insights catalog search |


