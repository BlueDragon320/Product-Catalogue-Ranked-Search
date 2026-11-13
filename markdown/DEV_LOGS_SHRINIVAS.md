# Developer Issue & Resolution Log — Shrinivas (Dev-2 / Dev-B)

> **Course**: BCA Mini-Project • Theme 2: Search & Ranking System  
> **Student Name**: Shrinivas (Roll: `01fe24bca311`)  
> **Assigned Engines**: Engine 2 (Interface & Access / UI) & Engine 4 (Testing & Validation)  
> **Target Repositories**: `Product-Catalogue-Ranked-Search` & `e-commerce-website`  

---

## Log Summary
This log records technical issues, layout challenges, JavaScript DOM calculation anomalies, test framework harness errors, and user interface refinements encountered during frontend development and test automation.

---

### Entry 1 • Phase 1: CSS Grid Card Alignment & Overflow on Viewport Resize
* **Date**: 2026-09-28
* **Component / File**: `app/static/css/style.css` (`e-commerce-website`)
* **Error / Issue Description**:
  Product cards in the storefront catalog had unequal heights when product titles spanned two lines, causing uneven button alignment (`Add to Cart`) and visual layout breaks on mobile screens (< 768px).
* **Root Cause**:
  The `.product-grid` CSS used `display: flex` without `flex-grow` on card bodies, causing containers to size strictly based on dynamic text content rather than row height.
* **Resolution & Applied Fix**:
  Converted product catalog container to CSS Grid with `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`. Applied `display: flex; flex-direction: column; justify-content: space-between;` to `.product-card`, ensuring all action buttons lock to the bottom edge uniformly across all breakpoints.

---

### Entry 2 • Phase 2: Missing CSRF Token in Dynamic REST Calls
* **Date**: 2026-10-04
* **Component / File**: `app/static/js/storefront.js` (`e-commerce-website`)
* **Error / Issue Description**:
  ```text
  HTTP 400 Bad Request
  {"error": "CSRF token missing or invalid"}
  ```
* **Root Cause**:
  When calling `fetch('/cart/add')` asynchronously from vanilla JavaScript, the request failed because Flask-WTF CSRF protection was enabled globally, and the AJAX fetch payload did not include the `X-CSRFToken` request header.
* **Resolution & Applied Fix**:
  Embedded the CSRF token into a meta tag inside `app/templates/base.html`:
  `<meta name="csrf-token" content="{{ csrf_token() }}">`.
  Updated all client-side `fetch()` wrappers in `storefront.js` to automatically extract the meta tag content and inject `'X-CSRFToken': token` into the HTTP headers.

---

### Entry 3 • Phase 3: Floating-Point Rounding Error in 100% Weight Indicator
* **Date**: 2026-10-18
* **Component / File**: `app/static/js/weight_check.js` (`Product-Catalogue-Ranked-Search`)
* **Error / Issue Description**:
  ```text
  UI Glitch: Weight slider showed 99.99% and rendered badge in red (Invalid), even when individual attribute inputs were 33.33%, 33.33%, and 33.34%.
  ```
* **Root Cause**:
  Standard JavaScript IEEE 754 floating-point arithmetic produced precision artifacts (e.g. `0.1 + 0.2 = 0.30000000000000004`), causing strict equality `sum === 100.0` to evaluate to `false`.
* **Resolution & Applied Fix**:
  Implemented epsilon tolerance check in both client-side JavaScript (`weight_check.js`) and backend API (`app/api/routes.py`):
  ```javascript
  const isValid = Math.abs(totalWeight - 100.0) < 0.05;
  ```
  Updated UI indicator to round displayed sums to 1 decimal place (`totalWeight.toFixed(1) + '%'`) and dynamically switch badge styles between `.badge-success` (cyan) and `.badge-danger` (crimson).

---

### Entry 4 • Phase 4: Missing Pytest Fixture 'app' During Test Execution
* **Date**: 2026-10-24
* **Component / File**: `tests/test_engine.py` & `tests/test_models.py`
* **Error / Issue Description**:
  ```text
  pytest.FixtureLookupError: 'app' not found
  available fixtures: cache, capfd, caplog, monkeypatch, tmp_path...
  ```
* **Root Cause**:
  The shared fixture file `tests/conftest.py` was omitted during a manual Git commit, causing pytest to run unit tests that expected an application context fixture without finding its definition.
* **Resolution & Applied Fix**:
  Authored and placed `tests/conftest.py` defining an `@pytest.fixture` named `app` configuring Flask in `'testing'` mode with an in-memory SQLite database (`sqlite:///:memory:`). Added automatic table creation (`_db.create_all()`) and cleanup teardown (`_db.drop_all()`). Verified that running `python3 -m pytest` executes with all tests passing.

---

### Entry 5 • Phase 5: Sponsored Interleaving List Index Out-of-Bounds
* **Date**: 2026-10-28
* **Component / File**: `app/ranking/helpers.py` (`Product-Catalogue-Ranked-Search`)
* **Error / Issue Description**:
  ```text
  IndexError: list index out of range
  File "app/ranking/helpers.py", line 78, in interleave_sponsored_products
      ranked_list.insert(slot - 1, sponsored_item)
  ```
* **Root Cause**:
  When a search query returned only 2 organic products, attempting to insert a sponsored product into `slot_position = 6` threw an index error or created unexpected null padding in the results array.
* **Resolution & Applied Fix**:
  Updated `interleave_sponsored_products()` to validate catalog depth and slot boundaries:
  ```python
  if len(organic_list) >= (target_slot - 1):
      organic_list.insert(target_slot - 1, sponsored_item)
  else:
      organic_list.append(sponsored_item)
  ```
  Enforced anti-bias policy: maximum 1 sponsored product per 5 organic items (capped at 20% total ratio). Authored unit test `test_sponsor_capping_and_interleaving()` in `tests/test_sponsor.py`.

---

### Entry 6 • Phase 6: Edge Case — Zero Active Attributes in Category
* **Date**: 2026-11-02
* **Component / File**: `app/ranking/engine.py` & `tests/test_edge_cases.py`
* **Error / Issue Description**:
  ```text
  AttributeError: 'NoneType' object has no attribute 'weight'
  Category page crashed when all attributes were marked inactive by admin.
  ```
* **Root Cause**:
  When an administrator deactivated all attributes in a category, the scoring loop received an empty criteria list, causing the composite score aggregator to evaluate an uninitialized generator expression.
* **Resolution & Applied Fix**:
  Added defensive check at the start of `recompute_category_scores()`: if active attributes count is 0, assign a baseline default score (`0.0`) to all products in that category, log a warning, and gracefully return without raising unhandled exceptions. Authored automated edge-case test `test_category_with_no_active_attributes()` in `tests/test_edge_cases.py`.

---
