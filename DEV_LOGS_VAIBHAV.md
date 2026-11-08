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
