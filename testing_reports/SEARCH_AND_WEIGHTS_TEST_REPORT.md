# 🔍 Search & Dynamic Weights Input Testing Report

**Project:** Noise E-Commerce Storefront & Weighted Multi-Tenant B2B Ranking Engine  
**Focus Area:** Parametric Search, Query Normalization, Fuzzy Typos, Attribute Range Filters, and Dynamic Custom Weights Input Testing  
**Test Framework:** Pytest 9.2.0 | Python 3.14.10 | Linux  
**Status:** ✅ **23 / 23 Search & Weights Test Cases Passed (100% Success Rate)**  

---

## Executive Summary

This report documents the verification of the two most critical algorithmic subsystems of the platform:
1. **Dynamic Custom Weights Personalization & Validation Engine:** Testing real-time slider input payloads, mathematical 100% weight sum rules, rejection of unbalanced weights, 0% weight tolerance, and client-side AJAX re-ranking.
2. **Parametric Search & Natural Language Query Processor:** Testing whitespace collapsing, punctuation stripping, phonetic Levenshtein typo corrections, category intent mapping, parametric range bounds (`min`, `max`, `between`), and zero-downtime offline fallback.

---

## 1. Dynamic Weights Input Testing (11 Tests)

| Test ID | Module | Test Function | Test Input / Weights Payload | Expected Behavior / Mathematical Rule | Actual Result | Status |
|:---|:---|:---|:---|:---|:---|:---:|
| `TC-WT-01` | `test_models.py` | `test_attribute_weight_sum_valid` | `Battery: 35.0%`, `Price: 35.0%`, `Rating: 15.0%`, `ANC: 15.0%` (Sum = 100.0%) | Validates that weights summing exactly to 100.0% are accepted and category is marked `VALID` | Successfully saved; sum confirmed at 100.0% | ✅ PASSED |
| `TC-WT-02` | `test_models.py` | `test_attribute_weight_sum_invalid` | `Battery: 40.0%`, `Price: 40.0%`, `Rating: 15.0%`, `ANC: 15.0%` (Sum = 110.0%) | Rejects weight sum $> 100.0\%$ with validation error; prevents unbalanced score calculation | Error raised; category activation blocked | ✅ PASSED |
| `TC-WT-03` | `test_models.py` | `test_attribute_weight_sum_invalid` | `Battery: 30.0%`, `Price: 30.0%`, `Rating: 15.0%`, `ANC: 10.0%` (Sum = 85.0%) | Rejects weight sum $< 100.0\%$ with validation error; ensures mathematical completeness | Error raised; category activation blocked | ✅ PASSED |
| `TC-WT-04` | `test_models.py` | `test_deactivated_attribute_excluded_from_weight` | 4 active attributes (sum=100.0%) + 1 inactive attribute (`is_active=False`, weight=25.0%) | Deactivated attributes are excluded from 100% sum calculation, allowing archiving | Inactive attribute excluded; active sum evaluates to 100.0% | ✅ PASSED |
| `TC-WT-05` | `test_edge_cases.py` | `test_zero_weight_attributes` | Attribute assigned `0.0%` weight | Attribute contributes $0.0$ to composite score without raising division-by-zero fatal errors | Safe calculation; total score unaffected by 0% metric | ✅ PASSED |
| `TC-WT-06` | `test_api.py` | `test_api_custom_weights_personalization` | POST `/api/v1/search` with `custom_weights={"Battery Life (hours)": 80.0, "Price (INR)": 20.0}` | Engine overrides default category weights and dynamically re-ranks catalog based on caller preference | High-battery products promoted to top; response confirmed | ✅ PASSED |
| `TC-WT-07` | `test_engine_client.py` | `test_search_with_custom_weights` | Client calls `search(category_id=1, custom_weights={"Battery Life": 50.0, "Price": 30.0, ...})` | Client serializes weights into JSON payload and dispatches HTTP POST to ranking engine | Verified POST call with matching JSON structure | ✅ PASSED |
| `TC-WT-08` | `test_storefront.py` | `test_smart_rank_api` | POST `/api/smart-rank` with slider weights: `{Battery: 40, Price: 30, Rating: 15, ANC: 15}` | AJAX endpoint returns updated product rankings with new composite scores without reloading page | HTTP 200 JSON with re-ranked product array | ✅ PASSED |
| `TC-WT-09` | `test_routes.py` | `test_update_rating_weight_and_range` | Update Rating attribute weight to 25.0% and scale min=1.0, max=5.0 | Dynamic update persisted to DB; catalog recomputed with updated weight distribution | Database record updated and category re-scored | ✅ PASSED |
| `TC-WT-10` | `test_routes.py` | `test_weight_api_requires_login` | Unauthenticated POST `/admin/category/<id>/weights` | Blocks unauthenticated callers from modifying tenant ranking weights | HTTP 302 redirect to login; weights preserved | ✅ PASSED |
| `TC-WT-11` | `test_storefront.py` | `test_storefront_hides_dynamic_weights` | Customer GET `/shop` storefront HTML | Shields internal B2B slider mechanisms (`slider_battery`, `slider_price`) from retail shoppers | Technical slider inputs completely absent from retail HTML | ✅ PASSED |

---

## 2. Search & Query Input Testing (12 Tests)

| Test ID | Module | Test Function | Test Input / Search Query | Expected Behavior / Parsing Pipeline | Actual Result | Status |
|:---|:---|:---|:---|:---|:---|:---:|
| `TC-SR-01` | `test_api.py` | `test_api_whitespace_and_typo_search` | `q="vs 102"`, `q="combatt"`, `q="neck band"` | Sanitizes punctuation, collapses whitespace, matches catalog products | Products returned for all variations; zero empty results | ✅ PASSED |
| `TC-SR-02` | `test_api.py` | `test_api_attribute_range_filter_min` | `category_id=4&attr_min_Battery+Life+(hours)=40` | Filters candidate pool to products with Battery Life $\ge 40.0$ hours | All returned products have Battery $\ge 40$ | ✅ PASSED |
| `TC-SR-03` | `test_api.py` | `test_api_attribute_range_filter_between` | `attr_min_Price=1000&attr_max_Price=3000` | Limits candidates to bounded interval $[1000, 3000]$ price window | All products strictly within $[1000, 3000]$ range | ✅ PASSED |
| `TC-SR-04` | `test_api.py` | `test_api_attribute_range_filter_excludes_unmatched` | Range filter on feature not present on all products | Safely filters out products missing the attribute without raising null pointer exceptions | Non-matching products excluded cleanly | ✅ PASSED |
| `TC-SR-05` | `test_api.py` | `test_api_attribute_range_filter_with_sponsored` | Range filter that excludes sponsored item (e.g. `attr_max_Price=2000` when sponsor is 5000) | Hard filters strictly take precedence over sponsored placement; non-matching sponsor is dropped | Sponsored item excluded when failing filter | ✅ PASSED |
| `TC-SR-06` | `test_api.py` | `test_api_attribute_range_filter_invalid_numeric` | `attr_min_Price=abc&attr_max_Price=xyz` | Gracefully ignores malformed non-numeric values; executes standard search without HTTP 500 | Malformed query ignored; search succeeds cleanly | ✅ PASSED |
| `TC-SR-07` | `test_api.py` | `test_api_include_sponsors_false_strips_sponsors` | GET `/api/v1/search?include_sponsors=false` | Strips all sponsored placements; delivers pure organic rankings | 0 sponsored items returned; 100% organic | ✅ PASSED |
| `TC-SR-08` | `test_engine_client.py` | `test_search_offline_fallback` | Engine socket connection refused; Query: `q="VS102"` | Gracefully falls back to local SQLite database search with local weighted ranking calculation | Returns local results with `fallback: True`, `status: offline` | ✅ PASSED |
| `TC-SR-09` | `test_engine_client.py` | `test_live_engine_search_noise_products` | Live search query against port 5000 | Returns full Noise catalog with composite scores $>0$ and integer ranks | 16+ products returned with live ranks | ✅ PASSED |
| `TC-SR-10` | `test_storefront.py` | `test_search_synonyms_ear_phones` | User queries `q="ear phones"` | Resolves natural language synonym to Wireless Earbuds; excludes Smartwatches | Noise audio products surfaced; smartwatches excluded | ✅ PASSED |
| `TC-SR-11` | `test_storefront.py` | `test_search_synonyms_ear_pods` | User queries brand slang `q="ear pods"` | Maps slang query to earbuds catalog without keyword miss | Air Buds and VS102 surfaced cleanly | ✅ PASSED |
| `TC-SR-12` | `test_storefront.py` | `test_search_headphones_whitespace_and_typos` | Queries: `"headphones"`, `"head phones"`, `"head-phones"`, `"headfone"`, `"headfones"` | Normalizes punctuation, collapses spaces, and performs phonetic correction (`fone` $\rightarrow$ `phone`) | All 5 query variants return Headphones products | ✅ PASSED |
| `TC-SR-13` | `test_storefront.py` | `test_search_typo_tolerance_and_whitespace` | Queries: `q="samrtwatch"`, `q="nekband"`, `q="earfones"` | Levenshtein edit distance and fuzzy vocabulary matching | Typo corrected to Smartwatches, Neckbands, Earbuds | ✅ PASSED |

---

## 3. How to Execute These Tests

```bash
# Run all Search & Dynamic Weights tests on the Ranking Engine
cd /home/blue/MiniProject/weighted-ranking-engine
python -m pytest tests/test_api.py tests/test_models.py tests/test_edge_cases.py -k "weight or search or filter or typo" -v

# Run all Search & Dynamic Weights tests on the Storefront Client
cd /home/blue/MiniProject/ECommerce-Site
python -m pytest tests/test_engine_client.py tests/test_storefront.py -k "weight or search or smart_rank or typo or synonym" -v
```
