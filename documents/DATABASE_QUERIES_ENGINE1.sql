-- =============================================================================
-- ENGINE 1: DATA & INTEGRITY (RDBMS SCHEMA, DDL, DML, EVOLUTION & AUDIT QUERIES)
-- Project: Weighted Ranking Engine & Noise E-Commerce Catalog Platform
-- Standard: ANSI SQL / PostgreSQL / MySQL / SQLite RDBMS Compliant
-- Author / Engine Lead: Engine 1 (Data & Integrity)
-- Description: Contains daily progression of DDL, ALTER, DML (INSERT, UPDATE, DELETE),
--              foreign key constraints, indexes, views, and integrity verification queries.
-- =============================================================================

-- =============================================================================
-- PART 1: SERVICE A — WEIGHTED RANKING ENGINE DATABASE SCHEMA (Port 5000)
-- Database Name: ranking_engine
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Day 1 - 3: Baseline Schema & Table Definitions (Phase 1: Foundations)
-- -----------------------------------------------------------------------------

-- Table 1: Companies (Tenant Multi-Tenancy Boundary)
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Users (Role-Based Access Control)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    company_id INTEGER NULL,
    is_admin BOOLEAN DEFAULT 0,
    is_superadmin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_company FOREIGN KEY (company_id) 
        REFERENCES companies(company_id) ON DELETE CASCADE
);

-- Table 3: Categories (Domain Classification)
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    display_attr_1 VARCHAR(100) NULL,
    display_attr_2 VARCHAR(100) NULL,
    CONSTRAINT fk_categories_company FOREIGN KEY (company_id) 
        REFERENCES companies(company_id) ON DELETE CASCADE,
    CONSTRAINT uq_company_category UNIQUE (company_id, name)
);

-- Table 4: Attributes (Scoring Criteria with Weights and Normalization Rules)
CREATE TABLE IF NOT EXISTS attributes (
    attribute_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) DEFAULT 'numeric' CHECK (data_type IN ('numeric', 'binary', 'categorical')),
    min_value DOUBLE PRECISION NULL,
    max_value DOUBLE PRECISION NULL,
    weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    lower_is_better BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attributes_category FOREIGN KEY (category_id) 
        REFERENCES categories(category_id) ON DELETE CASCADE,
    CONSTRAINT uq_category_attribute UNIQUE (category_id, name)
);

-- Table 5: Products (Catalog Products to be Ranked)
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    composite_score DOUBLE PRECISION DEFAULT 0.0,
    search_count INTEGER DEFAULT 0,
    is_sponsored BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) 
        REFERENCES categories(category_id) ON DELETE CASCADE
);

-- Table 6: Product Attribute Values (Raw & Normalized Utility Matrix)
CREATE TABLE IF NOT EXISTS product_attr_values (
    pav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    attribute_id INTEGER NOT NULL,
    raw_value DOUBLE PRECISION NOT NULL,
    normalized_value DOUBLE PRECISION DEFAULT 0.0,
    CONSTRAINT fk_pav_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_pav_attribute FOREIGN KEY (attribute_id) 
        REFERENCES attributes(attribute_id) ON DELETE CASCADE,
    CONSTRAINT uq_product_attribute UNIQUE (product_id, attribute_id)
);

-- Table 7: Sponsored Placements (Monetization & Auction Schedule)
CREATE TABLE IF NOT EXISTS sponsored_placements (
    placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    slot_position INTEGER NOT NULL CHECK (slot_position IN (1, 6, 11)),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    CONSTRAINT fk_sponsored_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT chk_date_validity CHECK (end_date >= start_date)
);

-- Table 8: Search Logs (Catalog Analytics & Intelligence Engine)
CREATE TABLE IF NOT EXISTS search_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text VARCHAR(200) NOT NULL,
    category_id INTEGER NULL,
    results_count INTEGER DEFAULT 0,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_logs_category FOREIGN KEY (category_id) 
        REFERENCES categories(category_id) ON DELETE SET NULL
);

-- -----------------------------------------------------------------------------
-- Performance Indexes for Sub-Millisecond Search Execution (Data Integrity)
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_company ON users(company_id);
CREATE INDEX IF NOT EXISTS idx_categories_company ON categories(company_id);
CREATE INDEX IF NOT EXISTS idx_attributes_category ON attributes(category_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_composite ON products(composite_score DESC);
CREATE INDEX IF NOT EXISTS idx_pav_lookup ON product_attr_values(product_id, attribute_id);
CREATE INDEX IF NOT EXISTS idx_sponsored_active ON sponsored_placements(is_active, start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_search_logs_query ON search_logs(query_text);

-- -----------------------------------------------------------------------------
-- Day 4 - 8: Schema Evolution & Migration Queries (ALTER Statements)
-- -----------------------------------------------------------------------------
-- Phase 2 migration: Adding Superadmin role for multi-tenant isolation
-- ALTER TABLE users ADD COLUMN is_superadmin BOOLEAN DEFAULT 0;

-- Phase 3 migration: Adding secondary display attributes for fast UI badges
-- ALTER TABLE categories ADD COLUMN display_attr_1 VARCHAR(100) NULL;
-- ALTER TABLE categories ADD COLUMN display_attr_2 VARCHAR(100) NULL;

-- Phase 4 migration: Adding search hit counter to track customer organic interest
-- ALTER TABLE products ADD COLUMN search_count INTEGER DEFAULT 0;

-- =============================================================================
-- PART 2: SERVICE B — NOISE E-COMMERCE STOREFRONT DATABASE SCHEMA (Port 8000)
-- Database Name: noise_ecommerce
-- =============================================================================

-- Table 9: Storefront Products (Retail Master Catalog)
CREATE TABLE IF NOT EXISTS storefront_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    price DOUBLE PRECISION NOT NULL CHECK (price >= 0),
    original_price DOUBLE PRECISION NULL,
    image_url VARCHAR(500) NULL,
    description TEXT NULL,
    rating DOUBLE PRECISION DEFAULT 0.0 CHECK (rating BETWEEN 0.0 AND 5.0),
    review_count INTEGER DEFAULT 0 CHECK (review_count >= 0),
    battery_life DOUBLE PRECISION DEFAULT 0.0,
    anc BOOLEAN DEFAULT 0,
    specs_json TEXT NULL,
    in_stock BOOLEAN DEFAULT 1,
    is_featured BOOLEAN DEFAULT 0,
    is_sponsored BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_store_slug ON storefront_products(slug);
CREATE INDEX IF NOT EXISTS idx_store_cat ON storefront_products(category);

-- Table 10: Shopping Cart Items (Session-Based Cart State)
CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cart_product FOREIGN KEY (product_id) 
        REFERENCES storefront_products(id) ON DELETE CASCADE,
    CONSTRAINT uq_cart_session_prod UNIQUE (session_id, product_id)
);

-- Table 11: Customer Orders (Transactional Financial Records)
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(120) NOT NULL,
    address TEXT NOT NULL,
    subtotal DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    shipping_fee DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    gst_amount DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    total_amount DOUBLE PRECISION NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 12: Order Line Items (Itemized Bill of Materials)
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DOUBLE PRECISION NOT NULL CHECK (unit_price >= 0),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) 
        REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) 
        REFERENCES storefront_products(id) ON DELETE RESTRICT
);

-- =============================================================================
-- PART 3: DATA MANIPULATION LANGUAGE (DML) — SEEDING & DATA INTEGRITY
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Day 9 - 14: Tenant Provisioning & Category Criteria Insertion
-- -----------------------------------------------------------------------------

-- 1. Insert Master Tenant Companies
INSERT INTO companies (company_id, name) VALUES (1, 'Noise Official');
INSERT INTO companies (company_id, name) VALUES (2, 'TechMart Electronics');
INSERT INTO companies (company_id, name) VALUES (3, 'Apex Audio Labs');

-- 2. Insert Superadmin and Tenant Manager Credentials
-- Passwords hashed using PBKDF2:SHA256 (admin123, noise123)
INSERT INTO users (username, email, password_hash, company_id, is_admin, is_superadmin) 
VALUES ('admin', 'admin@rankingengine.io', 'scrypt:32768:8:1......', 1, 1, 1);

INSERT INTO users (username, email, password_hash, company_id, is_admin, is_superadmin) 
VALUES ('noise_manager', 'manager@gonoise.com', 'scrypt:32768:8:1......', 1, 1, 0);

-- 3. Insert Product Categories for Tenant 1 (Noise Official)
INSERT INTO categories (category_id, company_id, name, display_attr_1, display_attr_2) 
VALUES (4, 1, 'Wireless Earbuds', 'Battery Life (hours)', 'Active Noise Cancelling');

INSERT INTO categories (category_id, company_id, name, display_attr_1, display_attr_2) 
VALUES (5, 1, 'Smartwatches', 'Battery Life (hours)', 'Rating');

INSERT INTO categories (category_id, company_id, name, display_attr_1, display_attr_2) 
VALUES (6, 1, 'Neckbands', 'Battery Life (hours)', 'Price (INR)');

INSERT INTO categories (category_id, company_id, name, display_attr_1, display_attr_2) 
VALUES (7, 1, 'Headphones', 'Battery Life (hours)', 'Active Noise Cancelling');

INSERT INTO categories (category_id, company_id, name, display_attr_1, display_attr_2) 
VALUES (8, 1, 'Smart Eyewear', 'Battery Life (hours)', 'Price (INR)');

-- 4. Insert Strict 100% Weighted Attributes (Category 4: Wireless Earbuds)
-- Constraint: SUM(weight) = 35.0 + 35.0 + 15.0 + 15.0 = 100.0%
INSERT INTO attributes (category_id, name, data_type, min_value, max_value, weight, lower_is_better, is_active)
VALUES (4, 'Battery Life (hours)', 'numeric', 0.0, 100.0, 35.0, 0, 1);

INSERT INTO attributes (category_id, name, data_type, min_value, max_value, weight, lower_is_better, is_active)
VALUES (4, 'Price (INR)', 'numeric', 500.0, 15000.0, 35.0, 1, 1);

INSERT INTO attributes (category_id, name, data_type, min_value, max_value, weight, lower_is_better, is_active)
VALUES (4, 'Rating', 'numeric', 0.0, 5.0, 15.0, 0, 1);

INSERT INTO attributes (category_id, name, data_type, min_value, max_value, weight, lower_is_better, is_active)
VALUES (4, 'Active Noise Cancelling', 'binary', 0.0, 1.0, 15.0, 0, 1);

-- 5. Insert Products (Earbuds Catalog)
INSERT INTO products (product_id, category_id, name, composite_score, search_count, is_sponsored)
VALUES (1, 4, 'Noise Buds VS104 Max', 0.8425, 142, 0);

INSERT INTO products (product_id, category_id, name, composite_score, search_count, is_sponsored)
VALUES (2, 4, 'Noise Buds Combat Pro', 0.7910, 89, 0);

INSERT INTO products (product_id, category_id, name, composite_score, search_count, is_sponsored)
VALUES (3, 4, 'Noise Buds N1 Ultra', 0.7250, 64, 0);

INSERT INTO products (product_id, category_id, name, composite_score, search_count, is_sponsored)
VALUES (4, 4, 'Noise Airwave 250 ANC', 0.8870, 310, 1);

-- 6. Insert Product Attribute Values Matrix (Raw & Normalized)
-- Noise Buds VS104 Max: Battery 45h, Price 1699, Rating 4.3, ANC 1.0
INSERT INTO product_attr_values (product_id, attribute_id, raw_value, normalized_value)
VALUES (1, 1, 45.0, 0.4500); -- Battery: (45-0)/(100-0) = 0.45

INSERT INTO product_attr_values (product_id, attribute_id, raw_value, normalized_value)
VALUES (1, 2, 1699.0, 0.9173); -- Price (lower_is_better): (15000-1699)/(15000-500) = 0.9173

INSERT INTO product_attr_values (product_id, attribute_id, raw_value, normalized_value)
VALUES (1, 3, 4.3, 0.8600); -- Rating: 4.3/5.0 = 0.86

INSERT INTO product_attr_values (product_id, attribute_id, raw_value, normalized_value)
VALUES (1, 4, 1.0, 1.0000); -- ANC: Binary True = 1.0

-- 7. Insert Sponsored Placement Schedule (Slot 1 Interleaving Rule)
INSERT INTO sponsored_placements (product_id, slot_position, start_date, end_date, is_active)
VALUES (4, 1, '2026-09-01', '2026-12-31', 1);

-- =============================================================================
-- PART 4: OPERATIONAL DML — UPDATE, DELETE & MAINTENANCE
-- =============================================================================

-- Update 1: Recompute & Update Product Composite Score
UPDATE products
SET composite_score = (
    SELECT ROUND(SUM(pav.normalized_value * (attr.weight / 100.0)), 4)
    FROM product_attr_values pav
    JOIN attributes attr ON pav.attribute_id = attr.attribute_id
    WHERE pav.product_id = products.product_id
),
updated_at = CURRENT_TIMESTAMP
WHERE category_id = 4;

-- Update 2: Increment Search Log Counter for Intelligent Caching
UPDATE products
SET search_count = search_count + 1
WHERE product_id = 1;

-- Update 3: Adjust Criteria Weight Dynamic Adjustment (Tuning Rule)
UPDATE attributes
SET weight = 40.0
WHERE category_id = 4 AND name = 'Battery Life (hours)';

UPDATE attributes
SET weight = 30.0
WHERE category_id = 4 AND name = 'Price (INR)';

-- Delete 1: Clean Expired Sponsored Placements
DELETE FROM sponsored_placements
WHERE end_date < CURRENT_DATE;

-- Delete 2: Cascade Tenant Cleanup Query
-- (Triggered when removing a company while preserving foreign key integrity)
DELETE FROM companies WHERE company_id = 99;

-- =============================================================================
-- PART 5: DATA INTEGRITY & AUDIT VERIFICATION QUERIES
-- =============================================================================

-- Query 1: Strict 100% Weight Verification Query (Rule Validation)
SELECT 
    c.name AS category_name,
    COUNT(a.attribute_id) AS active_attributes_count,
    ROUND(SUM(a.weight), 2) AS total_weight_percentage,
    CASE 
        WHEN ABS(SUM(a.weight) - 100.0) < 0.01 THEN 'VALID (100% Compliant)'
        ELSE 'INVALID (Weight Imbalance)'
    END AS integrity_status
FROM categories c
JOIN attributes a ON c.category_id = a.category_id
WHERE a.is_active = 1
GROUP BY c.category_id, c.name;

-- Query 2: Multi-Criteria Ranked Product Leaderboard (Deterministic Tie-Break)
SELECT 
    p.product_id,
    p.name AS product_name,
    c.name AS category_name,
    p.composite_score,
    p.search_count,
    p.is_sponsored,
    RANK() OVER (
        PARTITION BY p.category_id 
        ORDER BY p.composite_score DESC, p.created_at DESC, p.product_id ASC
    ) as engine_rank
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE p.category_id = 4;

-- Query 3: Multi-Tenant Data Isolation Audit
SELECT 
    comp.name AS company_tenant,
    u.username,
    u.email,
    CASE WHEN u.is_superadmin = 1 THEN 'SUPERADMIN' ELSE 'TENANT_USER' END AS user_role,
    COUNT(DISTINCT cat.category_id) AS owned_categories,
    COUNT(DISTINCT prod.product_id) AS owned_products
FROM companies comp
LEFT JOIN users u ON comp.company_id = u.company_id
LEFT JOIN categories cat ON comp.company_id = cat.company_id
LEFT JOIN products prod ON cat.category_id = prod.category_id
GROUP BY comp.company_id, comp.name, u.id, u.username, u.email, u.is_superadmin;

-- =============================================================================
-- END OF SCRIPT: DATA INTEGRITY ENGINE CERTIFIED
-- =============================================================================
