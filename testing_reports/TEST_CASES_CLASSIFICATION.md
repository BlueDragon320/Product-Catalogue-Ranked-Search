# 🧪 Test Cases Classification — Positive, Negative & Edge Cases

This document outlines the test case coverage for the **Noise Dual-Engine Platform** (`Product-Catalogue-Ranked-Search` and `e-commerce-website`), matching the college deliverable **[`TEST_CASES_ENGINE4.xlsx`](file:///home/blue/Collage-Mini-Project/college_engine_deliverables/TEST_CASES_ENGINE4.xlsx)** and our **118 automated Pytest test cases**.

---

## 📊 Summary Dashboard

| Scenario Type | Excel Master Sheet (`TEST_CASES_ENGINE4.xlsx`) | Automated Pytest Suite (`pytest`) | Overall Pass Rate |
| :--- | :--- | :--- | :--- |
| **🟢 Positive Cases** | 21 test cases | 64 test cases | **100% Passed** |
| **🔴 Negative Cases** | 11 test cases | 31 test cases | **100% Passed** |
| **🟡 Edge Cases** | 11 test cases | 23 test cases | **100% Passed** |
| **Total** | **43 Test Cases** | **118 Test Cases** | **100% Passed** |

---

## 1. 🟢 Positive Test Cases (Happy Path)
*Validates that the system functions correctly when provided with expected, valid inputs.*

### In REST API & Logic Engine:
- **`test_api_search_and_ranking`**: GET `/api/v1/search` returns 200 OK with ranked products sorted by composite score descending.
- **`test_api_categories_list`**: GET `/api/v1/categories?company_id=1` returns the 5 Noise categories with metadata.
- **`test_api_product_detail`**: GET `/api/v1/products/<id>` returns product specifications with normalized attributes.
- **`test_api_custom_weights_personalization`**: Re-computes dynamic rankings when valid custom weights (e.g., Battery: 60%, Price: 40%) are submitted.
- **`test_api_sponsor_injection`**: Interleaves sponsored products at slot 1 and slot 6 (strict 1:5 ratio).
- **`TC-DAT-003 (Weight Sum Rule)`**: Validates that weights summing exactly to `100.0%` are accepted and saved.

### In E-Commerce Storefront:
- **`test_storefront_home`**: GET `/` loads lifestyle homepage with Noise banner and featured products.
- **`test_category_page_products`**: GET `/shop?category=Headphones` returns Noise Two Wireless Headphones.
- **`test_admin_login_success`**: POST `/admin/login` with `admin` / `admin123` succeeds and redirects to dashboard.

---

## 2. 🔴 Negative Test Cases (Error & Security Handling)
*Validates that invalid inputs, missing fields, and unauthorized actions are safely rejected.*

### In REST API & Logic Engine:
- **`test_api_missing_company_id`**: GET `/api/v1/search` without `company_id` returns `400 Bad Request` (`MISSING_COMPANY_ID`).
- **`test_api_nonexistent_company_id`**: GET `/api/v1/search?company_id=99999` returns `404 Not Found` (`COMPANY_NOT_FOUND`).
- **`test_api_tenant_isolation`**: User of Tenant A cannot query, update, or view Tenant B's catalog or analytics (`403 Forbidden`).
- **`test_api_cross_company_category_restriction`**: Prevents accessing a category that belongs to another company ID.
- **`test_api_attribute_range_filter_invalid_numeric`**: Gracefully handles non-numeric or malformed query string values (e.g. `?min_price=abc`).
- **`TC-DAT-004 (Weight Sum Rule > 100%)`**: Rejects weight configurations summing to `110.0%` with validation error.
- **`TC-DAT-005 (Weight Sum Rule < 100%)`**: Rejects weight configurations summing to `85.0%` with validation error.

### In E-Commerce Storefront:
- **`test_admin_login_invalid_password`**: POST `/admin/login` with wrong password returns 200 with invalid credentials error.
- **`test_admin_protected_routes_unauthenticated`**: Accessing `/admin` without session cookie redirects to `/admin/login`.
- **`test_engine_client_offline_fallback`**: When ranking engine on port 5000 is intentionally killed, storefront does NOT crash with 500—it falls back to local SQLite rankings.

---

## 3. 🟡 Edge Cases (Boundaries & Anomalies)
*Validates mathematical limits, division-by-zero, extreme inputs, and tie-breaking.*

### In REST API & Logic Engine:
- **`test_normalize_value_same_min_max` (Division-by-Zero Protection)**:
  - When `min_value == max_value` (e.g. `min=40, max=40`), normalizer returns neutral `0.5` instead of raising `ZeroDivisionError`.
- **`test_normalize_value_out_of_range` (Clamping Boundaries)**:
  - Raw value above maximum (`150` on `[0, 100]`) is safely clamped to `1.0`.
  - Raw value below minimum (`-10` on `[0, 100]`) is safely clamped to `0.0`.
- **`test_zero_weight_attributes` (0% Contribution)**:
  - Attributes assigned `0.0%` weight contribute `0.0` to the composite score without corrupting total score math.
- **`test_all_products_same_score` (Deterministic Tie-Breaking)**:
  - When multiple products have identical composite scores and timestamps, tie-break resolves deterministically by `product_id ASC`.
- **`test_empty_category_ranking` (Zero Products)**:
  - Calling ranking engine on a newly created category with 0 products executes cleanly without errors.
- **`test_api_whitespace_and_typo_search`**:
  - Handles leading/trailing whitespace, excess spaces (`"   earbuds   "`), and casing anomalies cleanly.
- **`test_api_include_sponsors_false_strips_sponsors`**:
  - Setting `include_sponsors=false` strips out sponsored items while maintaining exact organic rankings.
- **`TC-LOG-015 (Anti-Bias Sponsored Cap Limit)`**:
  - Enforces maximum 20% cap (never more than 1 sponsored per 5 organic items), preventing ad flooding.

---

## 📁 Where to Find These Files

1. **Excel Viva Deliverable:**
   - 📄 [`/home/blue/Collage-Mini-Project/college_engine_deliverables/TEST_CASES_ENGINE4.xlsx`](file:///home/blue/Collage-Mini-Project/college_engine_deliverables/TEST_CASES_ENGINE4.xlsx)
   *(Sheet: `Master Test Cases` with column `Scenario Type` = `POSITIVE`, `NEGATIVE`, `EDGE CASE`)*
2. **Pytest Code Files:**
   - 📄 [`Product-Catalogue-Ranked-Search/tests/test_api.py`](file:///home/blue/mini-pjct/Product-Catalogue-Ranked-Search/tests/test_api.py)
   - 📄 [`Product-Catalogue-Ranked-Search/tests/test_edge_cases.py`](file:///home/blue/mini-pjct/Product-Catalogue-Ranked-Search/tests/test_edge_cases.py)
   - 📄 [`Product-Catalogue-Ranked-Search/tests/test_engine.py`](file:///home/blue/mini-pjct/Product-Catalogue-Ranked-Search/tests/test_engine.py)
3. **Execution Log File:**
   - 📄 [`/home/blue/Downloads/API_TEST_CASES.log`](file:///home/blue/Downloads/API_TEST_CASES.log)
