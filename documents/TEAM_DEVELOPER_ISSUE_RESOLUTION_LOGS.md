# Developer Issue & Resolution Log — Vaibhav (Dev-1 / Dev-A)

> **Course**: BCA Mini-Project • Theme 2: Search & Ranking System  
> **Student Name**: Vaibhav Patil (Roll: `01fe24bca300`)  
> **Assigned Engines**: Engine 3 (Logic & Rule / Backend) & Engine 1 (Data & Integrity)  
> **Target Repositories**: `Product-Catalogue-Ranked-Search` & `e-commerce-website`  

---

## Log Summary
This log records technical roadblocks, runtime exceptions, algorithmic edge cases, and Git synchronization hurdles encountered during the development of the microservice backend and data layer, along with the technical root cause and applied fix.

---

### Entry 1 • Phase 1: Database Scaffolding & Foreign Key Constraints
* **Date**: 2026-09-27
* **Component / File**: `app/models.py` (`Product-Catalogue-Ranked-Search`)
* **Error / Issue Description**:
  ```text
  sqlite3.IntegrityError: NOT NULL constraint failed: categories.company_id
  sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) FOREIGN KEY constraint failed
  ```
* **Root Cause**:
  When seeding test categories, the `company_id` foreign key was passed as `None` or omitted because the default factory function did not automatically resolve the parent tenant company ID before committing child entities.
* **Resolution & Applied Fix**:
  Added an explicit relationship validation check in `app/models.py` ensuring that `company_id` is mandatory and non-nullable on the `Category` model. Updated `seed.py` to first retrieve or insert the baseline company (`Company.query.get(1)` or create `'Noise Official'`) and explicitly assign `company_id=1` to all category records prior to calling `db.session.commit()`.

---

### Entry 2 • Phase 2: Engine REST Client Offline Resilience
* **Date**: 2026-10-02
* **Component / File**: `app/engine_client.py` (`e-commerce-website`)
* **Error / Issue Description**:
  ```text
  requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): 
  Max retries exceeded with url: /api/v1/search (Caused by NewConnectionError: Connection refused)
  ```
* **Root Cause**:
  When the storefront was started without the Ranking Engine running on port 5000 (or if the engine restarted), the storefront crashed with an unhandled `500 Internal Server Error` on the `/shop` route because `engine_client.py` made synchronous network calls without fallback handling.
* **Resolution & Applied Fix**:
  Refactored `RankingEngineClient.search()` in `app/engine_client.py` with defensive exception handling (`try-except requests.RequestException`). Implemented a graceful offline fallback mechanism: if the microservice is unreachable, the client catches the error, sets `'engine_offline': True`, queries local storefront database products sorted by rating/created_at, and returns a valid payload with a clean offline indicator banner. Added automated test `test_engine_offline_fallback()` in `tests/test_engine_client.py`.

---

### Entry 3 • Phase 3: Git Branch Divergence & Non-Fast-Forward Push Rejection
* **Date**: 2026-10-20
* **Component / File**: Git Repository (`Product-Catalogue-Ranked-Search`)
* **Error / Issue Description**:
  ```text
  ! [rejected]        main -> main (non-fast-forward)
  error: failed to push some refs to 'https://github.com/BlueDragon320/Product-Catalogue-Ranked-Search.git'
  hint: Updates were rejected because the tip of your current branch is behind its remote counterpart.
  ```
* **Root Cause**:
  Partner developer pushed commit `8918820` (company CRUD) to GitHub while local changes were committed onto a disconnected root tree from an unzipped package, causing divergent commit histories between local and remote.
* **Resolution & Applied Fix**:
  Used `git fetch origin main` to pull remote history without touching uncommitted changes, aligned the local branch pointer using `git reset --soft origin/main`, re-committed the staged files on top of the true remote history, and performed a clean fast-forward push (`git push origin main`). Documented this workflow in the developer execution guide.

---

### Entry 4 • Phase 4: Division by Zero in Min-Max Normalization
* **Date**: 2026-10-22
* **Component / File**: `app/ranking/engine.py` (`Product-Catalogue-Ranked-Search`)
* **Error / Issue Description**:
  ```text
  ZeroDivisionError: float division by zero
  File "app/ranking/engine.py", line 45, in normalize_value
      return (val - min_val) / (max_val - min_val)
  ```
* **Root Cause**:
  When all products in a newly created category had identical attribute values (e.g., all smartwatches had 168 hours battery life, meaning `min_val == max_val`), the denominator `(max_val - min_val)` evaluated to `0.0`.
* **Resolution & Applied Fix**:
  Added guard clause in `normalize_value()`:
  ```python
  if max_val == min_val:
      return 1.0 if not lower_is_better else 1.0
  ```
  Also handled boundary checks where `val < min_val` or `val > max_val` by clamping the result within `[0.0, 1.0]`. Added automated test cases in `tests/test_engine.py` verifying uniform attribute values.

---

### Entry 5 • Phase 4: Non-Deterministic Tie-Breaking in Search Results
* **Date**: 2026-10-23
* **Component / File**: `app/ranking/engine.py` (`Product-Catalogue-Ranked-Search`)
* **Error / Issue Description**:
  ```text
  AssertionError: assert [product_2, product_1] == [product_1, product_2]
  Flaky test failure in test_rank_products_tie_breaking
  ```
* **Root Cause**:
  When two products achieved the exact same composite score (e.g., `0.8500`), standard Python `sort(key=...)` maintained arbitrary insertion order, causing intermittent test failures depending on database retrieval sequence.
* **Resolution & Applied Fix**:
  Implemented strict three-tier deterministic tie-breaking logic in `apply_tiebreak_sort()`:
  1. Primary: `composite_score DESC`
  2. Secondary: `created_at DESC` (newer products win ties)
  3. Tertiary: `product_id ASC` (deterministic system identifier)
  This guarantees 100% reproducible ranking order across all environments.

---

### Entry 6 • Phase 5: Multi-Tenant Data Leak in Analytics Engine
* **Date**: 2026-10-26
* **Component / File**: `app/insights/routes.py` (`Product-Catalogue-Ranked-Search`)
* **Error / Issue Description**:
  ```text
  Security / Integrity Issue: Tenant B manager logged into /insights could view search query logs and products belonging to Tenant A.
  ```
* **Root Cause**:
  The ORM query `SearchLog.query.all()` in the insights controller was not scoped by `company_id`, allowing any authenticated tenant user to inspect search trends from other organizations.
* **Resolution & Applied Fix**:
  Updated the controller query to join `Category` and strictly filter by `Category.company_id == current_user.company_id` (or active `inspect_company_id` when Superadmin is impersonating a tenant). Authored unit test `test_tenant_insights_isolation()` in `tests/test_insights.py` to ensure complete multi-tenant boundaries.

---
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
