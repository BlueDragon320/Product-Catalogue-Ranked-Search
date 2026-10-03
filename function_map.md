# Product Catalogue Ranked Search: Function & Class Map

This document provides a comprehensive directory of all classes, methods, functions, and configuration objects implemented across the codebase in Phase 1 Foundation.

---

## 1. Application Factory & Routes (`app/__init__.py`)

| Symbol | Type | Line | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `db` | `SQLAlchemy` | L17 | N/A | `SQLAlchemy` | Global SQLAlchemy database extension instance. |
| `migrate` | `Migrate` | L18 | N/A | `Migrate` | Flask-Migrate database migration engine instance. |
| `login_manager` | `LoginManager` | L19 | N/A | `LoginManager` | Flask-Login session management handler instance. |
| `main_bp` | `Blueprint` | L26 | `name='main'`, `import_name=__name__` | `Blueprint` | Core application blueprint serving public landing routes. |
| `index()` | Function | L28–L31 | None | `str` (HTML) | Handles `GET /`. Renders and returns `templates/index.html`. |
| `create_app()` | Function | L34–L93 | `config_name: str = 'development'` | `Flask` | Application factory. Loads configuration, initializes extensions, creates database tables, registers blueprints dynamically, and returns the configured Flask instance. |

---

## 2. Configuration Profiles (`config.py`)

| Class / Object | Inherits | Line | Key Attributes | Description |
| :--- | :--- | :--- | :--- | :--- |
| `BaseConfig` | `object` | L5–L7 | `SECRET_KEY`, `SQLALCHEMY_TRACK_MODIFICATIONS` | Base configuration containing default settings shared across environments. |
| `DevelopmentConfig`| `BaseConfig` | L9–L12 | `DEBUG = True`, `SQLALCHEMY_DATABASE_URI = .../instance/ranking_engine.db` | Development profile configuring local SQLite database storage and active debug reload. |
| `TestingConfig` | `BaseConfig` | L14–L18 | `TESTING = True`, `WTF_CSRF_ENABLED = False`, `SQLALCHEMY_DATABASE_URI = sqlite:///:memory:` | Test profile configuring in-memory SQLite database and disabled CSRF validation for automated test execution. |
| `ProductionConfig` | `BaseConfig` | L20–L23 | `DEBUG = False`, `SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')` | Production profile with debug disabled and production database connection string resolution. |
| `config` | `dict` | L25–L30 | `'development'`, `'testing'`, `'production'`, `'default'` | Environment-to-class configuration mapping dictionary used by `create_app()`. |

---

## 3. Application Entrypoint (`run.py`)

| Symbol | Type | Line | Parameters | Description |
| :--- | :--- | :--- | :--- | :--- |
| `app` | `Flask` | L4 | None | Top-level Flask application instance initialized via `create_app(os.getenv('FLASK_CONFIG') or 'development')`. |
| `app.run()` | Method | L7 | `debug=True`, `port=5000` | Starts the WSGI development server on `http://127.0.0.1:5000/`. |

---

## 4. Relational Data Models (`app/models.py`)

### 4.1 `Company`

- **File**: `app/models.py` (L6–L19)
- **Table**: `companies`
- **Inherits**: `db.Model`
- **Description**: Represents a tenant organization using the multi-tenant ranking platform.

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `company_id` | `db.Column(db.Integer, primary_key=True)` | Primary key identifier for the tenant company. |
| `name` | `db.Column(db.String(100), nullable=False)` | Organization or tenant brand name. |
| `created_at` | `db.Column(db.DateTime, default=datetime.utcnow)` | UTC timestamp of company record creation. |
| `users` | `db.relationship('User', backref='company', lazy='dynamic')` | Dynamic relationship yielding users associated with this tenant. |
| `categories` | `db.relationship('Category', backref='company', lazy='dynamic')` | Dynamic relationship yielding categories owned by this tenant. |
| `__repr__()` | Method (`-> str`) | Returns `<Company {name}>`. |

---

### 4.2 `User`

- **File**: `app/models.py` (L21–L45)
- **Table**: `users`
- **Inherits**: `flask_login.UserMixin`, `db.Model`
- **Description**: Authenticated user account with role-based flags and tenant association.

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `id` | `db.Column(db.Integer, primary_key=True)` | Primary key identifier for the user. |
| `username` | `db.Column(db.String(64), unique=True, index=True, nullable=False)` | Unique login username. |
| `email` | `db.Column(db.String(120), unique=True, index=True, nullable=False)`| Unique user email address. |
| `password_hash` | `db.Column(db.String(128))` | Werkzeug salted hash of user password. |
| `company_id` | `db.Column(db.Integer, db.ForeignKey('companies.company_id'), index=True)` | Foreign key reference linking user to tenant company. |
| `is_admin` | `db.Column(db.Boolean, default=False)` | Administrative privileges within assigned company. |
| `is_superadmin`| `db.Column(db.Boolean, default=False)` | Platform-wide administrative privileges. |
| `created_at` | `db.Column(db.DateTime, default=datetime.utcnow)` | UTC timestamp of user account registration. |
| `set_password(password: str)` | Method (`-> None`) | Computes and stores salted hash using `werkzeug.security.generate_password_hash`. |
| `check_password(password: str)` | Method (`-> bool`) | Verifies raw password against stored hash using `werkzeug.security.check_password_hash`. |
| `__repr__()` | Method (`-> str`) | Returns `<User {username}>`. |

---

### 4.3 `load_user()`

- **File**: `app/models.py` (L46–L49)
- **Decorator**: `@login_manager.user_loader`
- **Parameters**: `user_id: str | int`
- **Return Type**: `User | None`
- **Description**: Flask-Login user callback. Queries and returns the active `User` record given the session user ID.

---

### 4.4 `Category`

- **File**: `app/models.py` (L51–L65)
- **Table**: `categories`
- **Inherits**: `db.Model`
- **Description**: Product category taxonomy owned by a specific tenant company.

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `category_id` | `db.Column(db.Integer, primary_key=True)` | Primary key identifier for the category. |
| `company_id` | `db.Column(db.Integer, db.ForeignKey('companies.company_id'), index=True)` | Foreign key linking category to its tenant company. |
| `name` | `db.Column(db.String(100), nullable=False)` | Category name (e.g. "Laptops", "Smartphones"). |
| `created_at` | `db.Column(db.DateTime, default=datetime.utcnow)` | UTC timestamp of category creation. |
| `attributes` | `db.relationship('Attribute', backref='category', lazy='dynamic')` | Dynamic relationship yielding ranking attributes in this category. |
| `products` | `db.relationship('Product', backref='category', lazy='dynamic')` | Dynamic relationship yielding products belonging to this category. |
| `__repr__()` | Method (`-> str`) | Returns `<Category {name}>`. |

---

### 4.5 `Attribute`

- **File**: `app/models.py` (L67–L85)
- **Table**: `attributes`
- **Inherits**: `db.Model`
- **Description**: Scoring criteria defined for a category, specifying data type, boundaries, default weight, and directionality.

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `attribute_id` | `db.Column(db.Integer, primary_key=True)` | Primary key identifier for the attribute. |
| `category_id` | `db.Column(db.Integer, db.ForeignKey('categories.category_id'), index=True)` | Foreign key linking attribute to its category. |
| `name` | `db.Column(db.String(100), nullable=False)` | Attribute label (e.g. "Price", "RAM", "Battery"). |
| `data_type` | `db.Column(db.String(50), default='numeric')` | Data type (`numeric` or `binary`). |
| `min_value` | `db.Column(db.Float)` | Expected minimum boundary for scaling. |
| `max_value` | `db.Column(db.Float)` | Expected maximum boundary for scaling. |
| `weight` | `db.Column(db.Float, default=1.0)` | Default weight allocation percentage in category ranking. |
| `lower_is_better` | `db.Column(db.Boolean, default=False)` | Directional polarity flag. If `True`, lower raw values yield higher normalized scores. |
| `is_active` | `db.Column(db.Boolean, default=True)` | Flag enabling or disabling attribute participation in scoring. |
| `created_at` | `db.Column(db.DateTime, default=datetime.utcnow)` | UTC timestamp of attribute registration. |
| `__repr__()` | Method (`-> str`) | Returns `<Attribute {name}>`. |

---

### 4.6 `Product`

- **File**: `app/models.py` (L87–L105)
- **Table**: `products`
- **Inherits**: `db.Model`
- **Description**: Core inventory entity belonging to a category, ranked dynamically across attribute values.

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `product_id` | `db.Column(db.Integer, primary_key=True)` | Primary key identifier for the product. |
| `category_id` | `db.Column(db.Integer, db.ForeignKey('categories.category_id'), index=True)` | Foreign key linking product to its category. |
| `name` | `db.Column(db.String(200), nullable=False)` | Product title or commercial model name. |
| `composite_score` | `db.Column(db.Float, default=0.0)` | Cached or calculated multi-criteria composite score \([0.0, 1.0]\). |
| `search_count` | `db.Column(db.Integer, default=0)` | Query impression counter. |
| `is_sponsored` | `db.Column(db.Boolean, default=False)` | Indicator whether product is currently running a sponsored promotion. |
| `created_at` | `db.Column(db.DateTime, default=datetime.utcnow)` | Creation timestamp (used as Tier 2 tie-breaker). |
| `updated_at` | `db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)` | Last modification timestamp. |
| `attribute_values` | `db.relationship('ProductAttrValue', backref='product', lazy='dynamic')` | Dynamic relationship yielding raw and normalized attribute records for this product. |
| `sponsored_placements` | `db.relationship('SponsoredPlacement', backref='product', lazy='dynamic')` | Dynamic relationship yielding sponsored schedules for this product. |
| `__repr__()` | Method (`-> str`) | Returns `<Product {name}>`. |

---

### 4.7 `ProductAttrValue`

- **File**: `app/models.py` (L107–L123)
- **Table**: `product_attr_values`
- **Inherits**: `db.Model`
- **Description**: Entity-Attribute-Value (EAV) junction table storing raw and normalized metrics for a given product and attribute.

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `pav_id` | `db.Column(db.Integer, primary_key=True)` | Primary key identifier for the value record. |
| `product_id` | `db.Column(db.Integer, db.ForeignKey('products.product_id'), index=True)` | Foreign key reference to target product. |
| `attribute_id` | `db.Column(db.Integer, db.ForeignKey('attributes.attribute_id'), index=True)` | Foreign key reference to defined attribute. |
| `raw_value` | `db.Column(db.Float)` | Raw un-normalized metric value (e.g. `1299.99` USD). |
| `normalized_value` | `db.Column(db.Float)` | Normalized metric value scaled to \([0.0, 1.0]\). |
| `attribute` | `db.relationship('Attribute', backref='attr_values')` | Direct relation to parent attribute definition. |
| `__table_args__` | `Tuple` | `UniqueConstraint('product_id', 'attribute_id', name='_product_attr_uc')` enforcing strict one-value-per-attribute policy per product. |
| `__repr__()` | Method (`-> str`) | Returns `<ProductAttrValue Product:{product_id} Attr:{attribute_id}>`. |

---

### 4.8 `SponsoredPlacement`

- **File**: `app/models.py` (L125–L138)
- **Table**: `sponsored_placements`
- **Inherits**: `db.Model`
- **Description**: Date-bounded sponsored placement definition for interleaving products into search positions.

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `placement_id` | `db.Column(db.Integer, primary_key=True)` | Primary key identifier for the placement schedule. |
| `product_id` | `db.Column(db.Integer, db.ForeignKey('products.product_id'), index=True)` | Foreign key reference to promoted product. |
| `slot_position` | `db.Column(db.Integer, nullable=False)` | Assigned target slot position (e.g. 1, 6, 11). |
| `start_date` | `db.Column(db.Date, nullable=False)` | Inclusive start date for campaign visibility. |
| `end_date` | `db.Column(db.Date, nullable=False)` | Inclusive end date for campaign visibility. |
| `is_active` | `db.Column(db.Boolean, default=True)` | Administrative toggle to activate or suspend campaign. |
| `__repr__()` | Method (`-> str`) | Returns `<SponsoredPlacement Product:{product_id} Slot:{slot_position}>`. |

---

### 4.9 `SearchLog`

- **File**: `app/models.py` (L140–L154)
- **Table**: `search_logs`
- **Inherits**: `db.Model`
- **Description**: Audit search logging table tracking executed queries, matched category, yield count, and timestamp.

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `log_id` | `db.Column(db.Integer, primary_key=True)` | Primary key identifier for the search audit record. |
| `query_text` | `db.Column(db.String(200), nullable=False)` | Search query entered by user or API caller. |
| `category_id` | `db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)` | Optional foreign key reference to target category. |
| `results_count` | `db.Column(db.Integer, default=0)` | Number of matching products returned. |
| `searched_at` | `db.Column(db.DateTime, default=datetime.utcnow)` | UTC timestamp of query execution. |
| `category` | `db.relationship('Category', backref='search_logs')` | Direct reference to target category entity. |
| `__repr__()` | Method (`-> str`) | Returns `<SearchLog query='{query_text}' results={results_count}>`. |

---

## 5. UI Templates & Presentation Components

| File | Template Type | Engine | Key Blocks / Elements |
| :--- | :--- | :--- | :--- |
| `app/templates/base.html` | Layout Shell | Engine 3 | `safe_url` macro, `[R//E]` brand mark, dynamic nav links, `user-identity` badge, flash alerts block, `{% block content %}`, semantic footer with live system indicator. |
| `app/templates/index.html` | Content View | Engine 3 | Extended from `base.html`, hero banner, 4 quantitative telemetry cards, 4 Core Engine breakdown cards, algorithm math terminal box, quick access cards. |
| `app/static/css/style.css` | Stylesheet | Engine 3 | Technical Minimalist variables, Space Grotesk, General Sans, JetBrains Mono font integrations, alert cards, badges, buttons, responsive grid utilities. |
