# API Reference — Multi-Tenant Product Catalogue Ranked Search

This document outlines the external REST APIs and administrative endpoints provided by the **Product Catalogue Ranked Search**. External organizations can integrate this engine to power product search, multi-criteria attribute scoring, and date-capped sponsored placements across their e-commerce storefronts, SaaS applications, and marketplace platforms.

---

## 1. External B2B Search & Ranking REST API (v1)

External applications interact with these endpoints to query tenant catalogs, calculate deterministic ranking scores on the fly, retrieve attribute breakdowns, and interleave sponsored listings under anti-bias rules.

### `GET /api/v1/search` & `POST /api/v1/search`
Search and rank products for a specified tenant company.

#### Request Parameters
Parameters can be supplied via query string parameters (`GET`) or a JSON payload (`POST`). The tenant company ID can also be provided using the `X-Company-ID` HTTP header.

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `company_id` | `integer` | **Yes** | — | Unique identifier of the tenant organization. |
| `q` | `string` | No | `""` | Search query matching product names (case-insensitive). If omitted, ranks all products. |
| `category_id` | `integer` | No | `null` | Filters products and scoring to a specific category. |
| `limit` | `integer` | No | `20` | Maximum results to return (capped at 100). |
| `offset` | `integer` | No | `0` | Result offset for pagination. |
| `include_sponsors` | `boolean` | No | `true` | Whether to interleave active sponsored items at capped 1:5 slots. |
| `custom_weights` | `object` | No | `null` | Dynamic user preference overrides (e.g. `{"Battery Life": 60, "Weight": 40}`). Must sum to 100.0%. |
| `filter_attr_id` | `integer` | No | `null` | Attribute ID to filter candidate products by (FR-21). |
| `filter_attr` | `string` | No | `null` | Attribute name to filter candidate products by (FR-21). |
| `filter_min` | `float` | No | `null` | Minimum inclusive attribute value boundary (FR-21). |
| `filter_max` | `float` | No | `null` | Maximum inclusive attribute value boundary (FR-21). |

#### Example GET Request
```bash
curl -X GET "http://localhost:5000/api/v1/search?company_id=1&category_id=1&q=sony" \
     -H "Accept: application/json"
```

#### Example POST Request with Dynamic Personalization Weights
```bash
curl -X POST "http://localhost:5000/api/v1/search" \
     -H "Content-Type: application/json" \
     -d '{
       "company_id": 1,
       "category_id": 1,
       "custom_weights": {
         "Battery Life": 70.0,
         "Active Noise Cancellation": 30.0
       }
     }'
```

#### Successful JSON Response (`200 OK`)
```json
{
  "status": "success",
  "engine": "Product Catalogue Ranked Search",
  "company_id": 1,
  "company_name": "Apex Electronics",
  "query": "sony",
  "category_id": 1,
  "category_name": "Wireless Earbuds",
  "total_results": 1,
  "limit": 20,
  "offset": 0,
  "results": [
    {
      "rank": 1,
      "product_id": 4,
      "name": "Sony WF-1000XM5",
      "category_id": 1,
      "category_name": "Wireless Earbuds",
      "composite_score": 0.8842,
      "score_pct": "88.42%",
      "is_sponsored": true,
      "attributes": {
        "Battery Life": {
          "attribute_id": 1,
          "data_type": "numeric",
          "raw_value": 8.0,
          "normalized_value": 0.75,
          "weight": 35.0,
          "lower_is_better": false,
          "display_value": 8.0
        },
        "Active Noise Cancellation": {
          "attribute_id": 2,
          "data_type": "binary",
          "raw_value": 1.0,
          "normalized_value": 1.0,
          "weight": 25.0,
          "lower_is_better": false,
          "display_value": "YES"
        }
      }
    }
  ]
}
```

---

### `GET /api/v1/categories`
Retrieve all provisioned categories and active attribute configurations for a tenant organization. Enables external frontends to build dynamic filter sidebars and preference sliders.

#### Request Parameters
- `company_id` (required): Tenant company ID (via query param or `X-Company-ID` header).

#### Example Request
```bash
curl -X GET "http://localhost:5000/api/v1/categories?company_id=1"
```

#### Successful JSON Response (`200 OK`)
```json
{
  "status": "success",
  "company_id": 1,
  "company_name": "Apex Electronics",
  "categories": [
    {
      "category_id": 1,
      "name": "Wireless Earbuds",
      "product_count": 7,
      "attributes": [
        {
          "attribute_id": 1,
          "name": "Battery Life",
          "data_type": "numeric",
          "min_value": 4.0,
          "max_value": 12.0,
          "weight": 35.0,
          "lower_is_better": false
        },
        {
          "attribute_id": 2,
          "name": "Active Noise Cancellation",
          "data_type": "binary",
          "min_value": 0.0,
          "max_value": 1.0,
          "weight": 25.0,
          "lower_is_better": false
        }
      ]
    }
  ]
}
```

---

### `GET /api/v1/product/<int:product_id>`
Retrieve granular ranking metrics, score contributions, and attributes for an individual product.

#### Request Parameters
- `company_id` (required): Tenant company ID.

#### Example Request
```bash
curl -X GET "http://localhost:5000/api/v1/product/4?company_id=1"
```

#### Successful JSON Response (`200 OK`)
```json
{
  "status": "success",
  "product_id": 4,
  "name": "Sony WF-1000XM5",
  "company_id": 1,
  "company_name": "Apex Electronics",
  "category_id": 1,
  "category_name": "Wireless Earbuds",
  "composite_score": 0.8842,
  "score_pct": "88.42%",
  "search_count": 14,
  "is_sponsored": true,
  "score_breakdown": [
    {
      "attribute_name": "Battery Life",
      "raw_value": 8.0,
      "min_value": 4.0,
      "max_value": 12.0,
      "normalized_value": 0.75,
      "normalized_pct": 75.0,
      "weight": 35.0,
      "contribution": 0.2625,
      "contribution_pct": 29.7
    }
  ]
}
```

---

## 2. API Error Codes

| HTTP Status | Error Code | Description |
| :--- | :--- | :--- |
| `400 Bad Request` | `MISSING_COMPANY_ID` | `company_id` was not supplied. |
| `400 Bad Request` | `INVALID_CATEGORY_ID` | `category_id` was not an integer. |
| `400 Bad Request` | `INVALID_WEIGHT_SUM` | Custom weights did not sum to 100.0%. |
| `400 Bad Request` | `INVALID_WEIGHTS` | One or more custom weights were non-numeric. |
| `404 Not Found` | `COMPANY_NOT_FOUND` | No company exists with the provided ID. |
| `404 Not Found` | `CATEGORY_NOT_FOUND` | Category does not exist or belongs to another tenant. |
| `404 Not Found` | `PRODUCT_NOT_FOUND` | Product does not exist or belongs to another tenant. |

---

## 3. Platform Administration & Security Controls

All tenant and administrative lifecycle operations are strictly gated by authentication and role-based permissions:

### Platform Superadmin Endpoints
- **GET `/admin/`**: Platform Tenant Management dashboard. Displays all tenant companies, global KPI metrics, and manager account lists.
- **GET & POST `/admin/company/new`**: Provision new isolated tenant company and initial manager account.
- **GET & POST `/admin/company/<id>/edit`**: Edit company organization parameters.
- **POST `/admin/company/<id>/delete`**: Delete company and cascade delete all child categories, products, attributes, sponsors, and logs.
- **GET & POST `/admin/company/<company_id>/user/<user_id>/reset-password`**: Administrative override allowing superadmins to reset any company manager user's password directly.
- **GET `/admin/company/<id>/inspect`**: Switch into a tenant's console view to audit categories and products.
- **GET `/admin/company/exit-inspect`**: Exit inspection mode and return to the Platform Superadmin console.

### Authentication Endpoints
- **POST `/auth/login`**: User authentication for Platform Superadmins and Tenant Managers.
- **GET `/auth/logout`**: Terminate current session.
- **GET & POST `/auth/register`**: **DISABLED**. Public registration is permanently closed. Automatically redirects to `/auth/login` with an informational notice.

---

## 4. Internal Calibration Endpoints

- **GET `/api/weight-total/<category_id>`**: Returns the current sum of active weights (must be 100%).
- **POST `/api/weight-validate`**: Real-time validation helper for dynamic attribute weighting controls.
