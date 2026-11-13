"""
tests/test_insights.py — Unit and integration tests for Insights & Search Intelligence.
Author: Dev-A (Vaibhav) | Phase: P7
"""
import pytest
from app import db
from app.models import Company, Category, Product, Attribute, ProductAttrValue, SponsoredPlacement, SearchLog, User

def login_as_tenant(client, company_id=None):
    user = User(
        username=f'mgr_{company_id or 0}',
        email=f'mgr_{company_id or 0}@test.com',
        company_id=company_id,
        is_admin=True,
        is_superadmin=(company_id is None)
    )
    user.set_password('pass123')
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True
    return user

def test_insights_unauthenticated_redirects(client):
    """Verify that unauthenticated visitors are redirected to login."""
    response = client.get('/insights/')
    assert response.status_code == 302

def test_insights_page_loads(client, app):
    """Test that the insights dashboard loads successfully when authenticated."""
    with app.app_context():
        co = Company(name='Test Co')
        db.session.add(co)
        db.session.commit()
        login_as_tenant(client, company_id=co.company_id)
        response = client.get('/insights/')
        assert response.status_code == 200
        assert b'CATALOG INSIGHTS' in response.data

def test_insights_sponsor_compliance(client, app):
    """Test that anti-bias sponsor compliance ratio is rendered accurately."""
    with app.app_context():
        co = Company(name='Test Co')
        db.session.add(co)
        db.session.commit()
        login_as_tenant(client, company_id=co.company_id)
        response = client.get('/insights/')
        assert response.status_code == 200
        assert b'SPONSOR_CAP' in response.data
        assert b'20.0% MAX' in response.data


# -----------------------------------------------------------------------------
# FR-21: Insights Attribute Range Filtering Tests
# -----------------------------------------------------------------------------

def test_insights_attribute_range_filter(client, app):
    """Test that /insights catalog search filters results by attribute range."""
    with app.app_context():
        co = Company(name='Insights Filter Co')
        db.session.add(co)
        db.session.commit()
        login_as_tenant(client, company_id=co.company_id)

        cat = Category(name='Audio', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr_battery = Attribute(category_id=cat.category_id, name='Battery Life', min_value=0, max_value=60, weight=100.0)
        db.session.add(attr_battery)
        db.session.commit()

        p_high = Product(name='Titanium Battery Buds', category_id=cat.category_id, composite_score=0.92)
        p_low = Product(name='Mini Battery Buds', category_id=cat.category_id, composite_score=0.55)
        db.session.add_all([p_high, p_low])
        db.session.commit()

        pav1 = ProductAttrValue(product_id=p_high.product_id, attribute_id=attr_battery.attribute_id, raw_value=45.0)
        pav2 = ProductAttrValue(product_id=p_low.product_id, attribute_id=attr_battery.attribute_id, raw_value=12.0)
        db.session.add_all([pav1, pav2])
        db.session.commit()

        # Query /insights with q=Buds and filter_attr_id, filter_min=30
        response = client.get(
            f'/insights/?q=Buds&category_id={cat.category_id}'
            f'&filter_attr_id={attr_battery.attribute_id}&filter_min=30'
        )
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Titanium Battery Buds' in html
        assert 'Mini Battery Buds' not in html
        assert 'FILTER ACTIVE' in html


def test_insights_attribute_range_filter_between_no_query(client, app):
    """Test /insights filtering by range [min, max] without keyword query."""
    with app.app_context():
        co = Company(name='Insights Range Co')
        db.session.add(co)
        db.session.commit()
        login_as_tenant(client, company_id=co.company_id)

        cat = Category(name='Laptops', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr_weight = Attribute(category_id=cat.category_id, name='Weight KG', min_value=1.0, max_value=4.0, weight=100.0)
        db.session.add(attr_weight)
        db.session.commit()

        p_feather = Product(name='Feather Laptop', category_id=cat.category_id, composite_score=0.90)
        p_tank = Product(name='Tank Workstation', category_id=cat.category_id, composite_score=0.70)
        db.session.add_all([p_feather, p_tank])
        db.session.commit()

        pav1 = ProductAttrValue(product_id=p_feather.product_id, attribute_id=attr_weight.attribute_id, raw_value=1.2)
        pav2 = ProductAttrValue(product_id=p_tank.product_id, attribute_id=attr_weight.attribute_id, raw_value=3.5)
        db.session.add_all([pav1, pav2])
        db.session.commit()

        # Filter weight between 1.0 and 2.0 without q
        response = client.get(
            f'/insights/?category_id={cat.category_id}'
            f'&filter_attr_id={attr_weight.attribute_id}&filter_min=1.0&filter_max=2.0'
        )
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Feather Laptop' in html
        assert 'Tank Workstation' not in html
        assert 'QUERY RESULTS MATRIX' in html


def test_insights_available_attributes_rendered_in_filter_ui(client, app):
    """Test that available category attributes are provided to the template context and dropdown."""
    with app.app_context():
        co = Company(name='Insights UI Co')
        db.session.add(co)
        db.session.commit()
        login_as_tenant(client, company_id=co.company_id)

        cat = Category(name='Monitors', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr1 = Attribute(category_id=cat.category_id, name='Refresh Rate Hz', min_value=60, max_value=240, weight=50.0)
        attr2 = Attribute(category_id=cat.category_id, name='Screen Size Inch', min_value=24, max_value=49, weight=50.0)
        db.session.add_all([attr1, attr2])
        db.session.commit()

        response = client.get(f'/insights/?category_id={cat.category_id}')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Refresh Rate Hz' in html
        assert 'Screen Size Inch' in html


def test_tenant_insights_isolation(client, app):
    """Verify company user only sees their own company categories/products in insights."""
    with app.app_context():
        # Company A
        co_a = Company(name='Tenant Alpha')
        db.session.add(co_a)
        db.session.commit()
        user_a = User(username='alpha_mgr', email='alpha@test.com', company_id=co_a.company_id)
        user_a.set_password('pass123')
        db.session.add(user_a)
        cat_a = Category(name='Alpha Gadgets', company_id=co_a.company_id)
        db.session.add(cat_a)
        db.session.commit()
        prod_a = Product(name='Alpha Device 100', category_id=cat_a.category_id, composite_score=0.91)
        db.session.add(prod_a)

        # Company B
        co_b = Company(name='Tenant Beta')
        db.session.add(co_b)
        db.session.commit()
        cat_b = Category(name='Beta Gizmos', company_id=co_b.company_id)
        db.session.add(cat_b)
        db.session.commit()
        prod_b = Product(name='Beta Gizmo 500', category_id=cat_b.category_id, composite_score=0.85)
        db.session.add(prod_b)
        db.session.commit()

        # Log in as user_a
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user_a.id)
            sess['_fresh'] = True

        response = client.get('/insights/')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        assert 'Tenant Alpha' in data
        assert 'Alpha Gadgets' in data
        assert 'Beta Gizmos' not in data

def test_tenant_insights_empty_catalog(client, app):
    """Verify when a company user deletes/has no categories, an isolated empty state is shown."""
    with app.app_context():
        co_empty = Company(name='Empty Tenant Corp')
        db.session.add(co_empty)
        db.session.commit()
        user_empty = User(username='empty_mgr', email='empty_corp@test.com', company_id=co_empty.company_id)
        user_empty.set_password('pass123')
        db.session.add(user_empty)
        db.session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(user_empty.id)
            sess['_fresh'] = True

        response = client.get('/insights/')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        assert 'NO CATALOG DATA FOUND' in data
        assert 'Empty Tenant Corp' in data


def test_insights_search_query_execution(client, app):
    """Test that running a query records search log and returns ranked products."""
    with app.app_context():
        co = Company(name='Search Co')
        db.session.add(co)
        db.session.commit()
        login_as_tenant(client, company_id=co.company_id)
        cat = Category(name='Audio', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()
        prod = Product(name='Wireless Pro Earphones', category_id=cat.category_id, composite_score=0.88)
        db.session.add(prod)
        db.session.commit()
        prod_id = prod.product_id

        # Execute search
        response = client.get('/insights/?q=Earphones')
        assert response.status_code == 200
        assert b'Wireless Pro Earphones' in response.data
        assert b'QUERY RESULTS MATRIX' in response.data

        # Verify search log created
        log_entry = SearchLog.query.filter_by(query_text='Earphones').first()
        assert log_entry is not None
        assert log_entry.results_count >= 1

        # Verify search_count incremented
        updated_prod = db.session.get(Product, prod_id)
        assert updated_prod.search_count >= 1

def test_insights_category_filter(client, app):
    """Test searching with category filter."""
    with app.app_context():
        co = Company(name='Filter Co')
        db.session.add(co)
        db.session.commit()
        login_as_tenant(client, company_id=co.company_id)
        cat1 = Category(name='Shoes', company_id=co.company_id)
        cat2 = Category(name='Shirts', company_id=co.company_id)
        db.session.add_all([cat1, cat2])
        db.session.commit()

        prod1 = Product(name='Running Shoes Nike', category_id=cat1.category_id, composite_score=0.75)
        prod2 = Product(name='Running Shoes Adidas', category_id=cat2.category_id, composite_score=0.70)
        db.session.add_all([prod1, prod2])
        db.session.commit()

        response = client.get(f'/insights/?q=Running&category_id={cat1.category_id}')
        assert response.status_code == 200
        assert b'Running Shoes Nike' in response.data
        assert b'Running Shoes Adidas' not in response.data

def test_insights_attribute_range_filter_single_threshold(client, app):
    """Test FR-21: Attribute range filtering in insights simulation with single threshold."""
    with app.app_context():
        co = Company(name='Range Filter Co')
        db.session.add(co)
        db.session.commit()
        login_as_tenant(client, company_id=co.company_id)
        cat = Category(name='Monitors', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()
        attr = Attribute(category_id=cat.category_id, name='RefreshRate', min_value=60, max_value=240, weight=100.0)
        db.session.add(attr)
        db.session.commit()

        p_low = Product(name='Standard 60Hz Display', category_id=cat.category_id, composite_score=0.40)
        p_high = Product(name='Pro Gaming 144Hz Display', category_id=cat.category_id, composite_score=0.90)
        db.session.add_all([p_low, p_high])
        db.session.commit()

        pav_low = ProductAttrValue(product_id=p_low.product_id, attribute_id=attr.attribute_id, raw_value=60.0, normalized_value=0.0)
        pav_high = ProductAttrValue(product_id=p_high.product_id, attribute_id=attr.attribute_id, raw_value=144.0, normalized_value=0.46)
        db.session.add_all([pav_low, pav_high])
        db.session.commit()

        # Filter for RefreshRate >= 100
        response = client.get(f'/insights/?filter_attr_id={attr.attribute_id}&filter_min=100')
        assert response.status_code == 200
        assert b'Pro Gaming 144Hz Display' in response.data
        assert b'Standard 60Hz Display' not in response.data
