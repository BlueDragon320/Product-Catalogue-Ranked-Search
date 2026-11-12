import pytest
from datetime import date, timedelta
from app import db
from app.models import Company, Category, Attribute, Product, ProductAttrValue, SponsoredPlacement, SearchLog

def test_api_missing_company_id(client):
    """Test that GET /api/v1/search without company_id returns 400 Bad Request."""
    response = client.get('/api/v1/search')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['error'] == 'MISSING_COMPANY_ID'

def test_api_nonexistent_company_id(client):
    """Test that GET /api/v1/search with invalid company_id returns 404 Not Found."""
    response = client.get('/api/v1/search?company_id=99999')
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['error'] == 'COMPANY_NOT_FOUND'

def test_api_search_and_ranking(client, app):
    """Test that GET /api/v1/search returns ranked products with composite scores and attributes."""
    with app.app_context():
        co = Company(name='Apex API Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Audio', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr1 = Attribute(category_id=cat.category_id, name='Sound', min_value=0, max_value=10, weight=60.0)
        attr2 = Attribute(category_id=cat.category_id, name='Battery', min_value=0, max_value=20, weight=40.0)
        db.session.add_all([attr1, attr2])
        db.session.commit()

        p1 = Product(name='Pro Earbuds', category_id=cat.category_id, composite_score=0.85)
        p2 = Product(name='Lite Earbuds', category_id=cat.category_id, composite_score=0.60)
        db.session.add_all([p1, p2])
        db.session.commit()

        pav1 = ProductAttrValue(product_id=p1.product_id, attribute_id=attr1.attribute_id, raw_value=9.0, normalized_value=0.9)
        pav2 = ProductAttrValue(product_id=p2.product_id, attribute_id=attr1.attribute_id, raw_value=6.0, normalized_value=0.6)
        db.session.add_all([pav1, pav2])
        db.session.commit()

        # Query API
        response = client.get(f'/api/v1/search?company_id={co.company_id}&q=Earbuds')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['total_results'] == 2
        assert len(data['results']) == 2
        # Check rank ordering (highest composite score first)
        assert data['results'][0]['name'] == 'Pro Earbuds'
        assert data['results'][0]['rank'] == 1
        assert data['results'][1]['name'] == 'Lite Earbuds'
        assert data['results'][1]['rank'] == 2
        assert 'Sound' in data['results'][0]['attributes']

        # Check telemetry: search_count should have incremented
        updated_p1 = db.session.get(Product, p1.product_id)
        assert updated_p1.search_count >= 1

def test_api_tenant_isolation(client, app):
    """Test that search queries strictly isolate products to the requested company."""
    with app.app_context():
        co1 = Company(name='Tenant One')
        co2 = Company(name='Tenant Two')
        db.session.add_all([co1, co2])
        db.session.commit()

        cat1 = Category(name='Phones', company_id=co1.company_id)
        cat2 = Category(name='Phones', company_id=co2.company_id)
        db.session.add_all([cat1, cat2])
        db.session.commit()

        p1 = Product(name='Galaxy S24', category_id=cat1.category_id, composite_score=0.9)
        p2 = Product(name='iPhone 15', category_id=cat2.category_id, composite_score=0.95)
        db.session.add_all([p1, p2])
        db.session.commit()

        # Query Tenant One
        resp1 = client.get(f'/api/v1/search?company_id={co1.company_id}')
        data1 = resp1.get_json()
        prod_names1 = [r['name'] for r in data1['results']]
        assert 'Galaxy S24' in prod_names1
        assert 'iPhone 15' not in prod_names1

        # Query Tenant Two
        resp2 = client.get(f'/api/v1/search?company_id={co2.company_id}')
        data2 = resp2.get_json()
        prod_names2 = [r['name'] for r in data2['results']]
        assert 'iPhone 15' in prod_names2
        assert 'Galaxy S24' not in prod_names2

def test_api_cross_company_category_restriction(client, app):
    """Test that passing a category_id belonging to another company returns 404."""
    with app.app_context():
        co1 = Company(name='Org Alpha')
        co2 = Company(name='Org Beta')
        db.session.add_all([co1, co2])
        db.session.commit()

        cat2 = Category(name='Beta Domain', company_id=co2.company_id)
        db.session.add(cat2)
        db.session.commit()

        # Company 1 attempts to query Company 2's category
        resp = client.get(f'/api/v1/search?company_id={co1.company_id}&category_id={cat2.category_id}')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['error'] == 'CATEGORY_NOT_FOUND'

def test_api_categories_list(client, app):
    """Test GET /api/v1/categories endpoint."""
    with app.app_context():
        co = Company(name='Cat Explorer Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Wearables', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr = Attribute(category_id=cat.category_id, name='Waterproof', data_type='binary', weight=100.0)
        db.session.add(attr)
        db.session.commit()

        resp = client.get(f'/api/v1/categories?company_id={co.company_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert len(data['categories']) == 1
        assert data['categories'][0]['name'] == 'Wearables'
        assert data['categories'][0]['attributes'][0]['data_type'] == 'binary'

def test_api_product_detail(client, app):
    """Test GET /api/v1/product/<id> endpoint."""
    with app.app_context():
        co = Company(name='Detail Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Displays', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr = Attribute(category_id=cat.category_id, name='Resolution', min_value=1080, max_value=4000, weight=100.0)
        db.session.add(attr)
        db.session.commit()

        prod = Product(name='4K Monitor', category_id=cat.category_id, composite_score=0.92)
        db.session.add(prod)
        db.session.commit()

        pav = ProductAttrValue(product_id=prod.product_id, attribute_id=attr.attribute_id, raw_value=3840.0, normalized_value=0.9452)
        db.session.add(pav)
        db.session.commit()

        resp = client.get(f'/api/v1/product/{prod.product_id}?company_id={co.company_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert data['name'] == '4K Monitor'
        assert data['composite_score'] == 0.92
        assert len(data['score_breakdown']) == 1
        assert data['score_breakdown'][0]['attribute_name'] == 'Resolution'

def test_api_sponsor_injection(client, app):
    """Test that active sponsored items are flagged and placed according to 1:5 rule."""
    with app.app_context():
        co = Company(name='Sponsor Test Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Audio', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        p1 = Product(name='Organic Earbud 1', category_id=cat.category_id, composite_score=0.99)
        p2 = Product(name='Sponsored Earbud 1', category_id=cat.category_id, composite_score=0.50)
        db.session.add_all([p1, p2])
        db.session.commit()

        today = date.today()
        sp = SponsoredPlacement(
            product_id=p2.product_id,
            slot_position=1,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=5),
            is_active=True
        )
        db.session.add(sp)
        db.session.commit()

        resp = client.get(f'/api/v1/search?company_id={co.company_id}&category_id={cat.category_id}&include_sponsors=true')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['results']) == 2
        # Position 1 should be the sponsored product per 1:5 rule
        assert data['results'][0]['is_sponsored'] is True
        assert data['results'][0]['name'] == 'Sponsored Earbud 1'
        assert data['results'][1]['is_sponsored'] is False
        assert data['results'][1]['name'] == 'Organic Earbud 1'

def test_api_custom_weights_personalization(client, app):
    """Test dynamic weight override query for on-the-fly personalization."""
    with app.app_context():
        co = Company(name='Custom Weight Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Laptops', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr_ram = Attribute(category_id=cat.category_id, name='RAM', min_value=8, max_value=64, weight=50.0)
        attr_weight = Attribute(category_id=cat.category_id, name='Weight', min_value=1.0, max_value=3.0, weight=50.0, lower_is_better=True)
        db.session.add_all([attr_ram, attr_weight])
        db.session.commit()

        p_heavy = Product(name='Heavy Workstation', category_id=cat.category_id, composite_score=0.5)
        p_light = Product(name='Ultralight Laptop', category_id=cat.category_id, composite_score=0.5)
        db.session.add_all([p_heavy, p_light])
        db.session.commit()

        pav1 = ProductAttrValue(product_id=p_heavy.product_id, attribute_id=attr_ram.attribute_id, raw_value=64.0)
        pav2 = ProductAttrValue(product_id=p_heavy.product_id, attribute_id=attr_weight.attribute_id, raw_value=3.0)
        pav3 = ProductAttrValue(product_id=p_light.product_id, attribute_id=attr_ram.attribute_id, raw_value=16.0)
        pav4 = ProductAttrValue(product_id=p_light.product_id, attribute_id=attr_weight.attribute_id, raw_value=1.0)
        db.session.add_all([pav1, pav2, pav3, pav4])
        db.session.commit()

        # Query with 90% priority on RAM (Heavy workstation should win)
        post_data = {
            'company_id': co.company_id,
            'category_id': cat.category_id,
            'custom_weights': {
                'RAM': 90.0,
                'Weight': 10.0
            }
        }
        resp = client.post('/api/v1/search', json=post_data)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['results'][0]['name'] == 'Heavy Workstation'

        # Query with 90% priority on Weight (Ultralight should win)
        post_data_light = {
            'company_id': co.company_id,
            'category_id': cat.category_id,
            'custom_weights': {
                'RAM': 10.0,
                'Weight': 90.0
            }
        }
        resp2 = client.post('/api/v1/search', json=post_data_light)
        assert resp2.status_code == 200
        data2 = resp2.get_json()
        assert data2['results'][0]['name'] == 'Ultralight Laptop'


def test_api_whitespace_and_typo_search(client, app):
    """Test whitespace collapsing and typo tolerance in search queries."""
    with app.app_context():
        co = Company(name='Audio Tech Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Headphones', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        p = Product(name='Noise Combat Pro Headphones', category_id=cat.category_id, composite_score=0.88)
        db.session.add(p)
        db.session.commit()

        # Whitespace test: "head phones" -> matches "Headphones"
        resp1 = client.get(f'/api/v1/search?company_id={co.company_id}&q=head+phones')
        assert resp1.status_code == 200
        data1 = resp1.get_json()
        assert len(data1['results']) >= 1
        assert data1['results'][0]['name'] == 'Noise Combat Pro Headphones'

        # Typo test: "combatt" -> matches "Combat"
        resp2 = client.get(f'/api/v1/search?company_id={co.company_id}&q=combatt')
        assert resp2.status_code == 200
        data2 = resp2.get_json()
        assert len(data2['results']) >= 1
        assert data2['results'][0]['name'] == 'Noise Combat Pro Headphones'


def test_api_product_is_sponsored_attribute_priority(client, app):
    """Test that a product with is_sponsored=True leads at rank #1."""
    with app.app_context():
        co = Company(name='Priority Sponsor Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Audio', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        p1 = Product(name='Top Scoring Organic Earbuds', category_id=cat.category_id, composite_score=0.99, is_sponsored=False)
        p2 = Product(name='Sponsored Low Score Earbuds', category_id=cat.category_id, composite_score=0.45, is_sponsored=True)
        db.session.add_all([p1, p2])
        db.session.commit()

        resp = client.get(f'/api/v1/search?company_id={co.company_id}&category_id={cat.category_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['results']) == 2
        assert data['results'][0]['name'] == 'Sponsored Low Score Earbuds'
        assert data['results'][0]['is_sponsored'] is True
        assert data['results'][0]['rank'] == 1


# -----------------------------------------------------------------------------
# FR-21: Attribute Range Filtering Tests
# -----------------------------------------------------------------------------

def test_api_engine_title_updated(client, app):
    """Test that API search endpoint returns updated engine title 'Product Catalogue Ranked Search'."""
    with app.app_context():
        co = Company(name='Engine Title Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Gadgets', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        p = Product(name='Test Gadget', category_id=cat.category_id, composite_score=0.75)
        db.session.add(p)
        db.session.commit()

        resp = client.get(f'/api/v1/search?company_id={co.company_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['engine'] == 'Product Catalogue Ranked Search'


def test_api_attribute_range_filter_min(client, app):
    """Test filtering by attribute ID with filter_min (e.g. battery life >= 30). Excluded items must not appear."""
    with app.app_context():
        co = Company(name='Battery Range Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Earbuds', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr_battery = Attribute(category_id=cat.category_id, name='Battery Life', min_value=0, max_value=60, weight=100.0)
        db.session.add(attr_battery)
        db.session.commit()

        p_high = Product(name='Ultra Battery Buds', category_id=cat.category_id, composite_score=0.90)
        p_mid = Product(name='Balanced Buds', category_id=cat.category_id, composite_score=0.70)
        p_low = Product(name='Basic Buds', category_id=cat.category_id, composite_score=0.50)
        db.session.add_all([p_high, p_mid, p_low])
        db.session.commit()

        pav1 = ProductAttrValue(product_id=p_high.product_id, attribute_id=attr_battery.attribute_id, raw_value=40.0)
        pav2 = ProductAttrValue(product_id=p_mid.product_id, attribute_id=attr_battery.attribute_id, raw_value=30.0)
        pav3 = ProductAttrValue(product_id=p_low.product_id, attribute_id=attr_battery.attribute_id, raw_value=15.0)
        db.session.add_all([pav1, pav2, pav3])
        db.session.commit()

        # Filter battery >= 30: both Ultra (40) and Balanced (30) should be included; Basic (15) excluded
        resp = client.get(
            f'/api/v1/search?company_id={co.company_id}&category_id={cat.category_id}'
            f'&filter_attr_id={attr_battery.attribute_id}&filter_min=30'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert data['total_results'] == 2
        names = [r['name'] for r in data['results']]
        assert 'Ultra Battery Buds' in names
        assert 'Balanced Buds' in names
        assert 'Basic Buds' not in names


def test_api_attribute_range_filter_between(client, app):
    """Test filtering by attribute range [filter_min, filter_max] (e.g. price between 1000 and 3000)."""
    with app.app_context():
        co = Company(name='Price Range Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Smartphones', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr_price = Attribute(category_id=cat.category_id, name='Price', min_value=100, max_value=5000, weight=100.0, lower_is_better=True)
        db.session.add(attr_price)
        db.session.commit()

        p_budget = Product(name='Budget Phone', category_id=cat.category_id, composite_score=0.85)
        p_mid = Product(name='Midrange Phone', category_id=cat.category_id, composite_score=0.75)
        p_flagship = Product(name='Flagship Phone', category_id=cat.category_id, composite_score=0.65)
        db.session.add_all([p_budget, p_mid, p_flagship])
        db.session.commit()

        pav1 = ProductAttrValue(product_id=p_budget.product_id, attribute_id=attr_price.attribute_id, raw_value=800.0)
        pav2 = ProductAttrValue(product_id=p_mid.product_id, attribute_id=attr_price.attribute_id, raw_value=2200.0)
        pav3 = ProductAttrValue(product_id=p_flagship.product_id, attribute_id=attr_price.attribute_id, raw_value=4500.0)
        db.session.add_all([pav1, pav2, pav3])
        db.session.commit()

        # Query range 1000 to 3000 using filter_attr (by attribute name)
        resp = client.get(
            f'/api/v1/search?company_id={co.company_id}&category_id={cat.category_id}'
            f'&filter_attr=Price&filter_min=1000&filter_max=3000'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total_results'] == 1
        assert len(data['results']) == 1
        assert data['results'][0]['name'] == 'Midrange Phone'


def test_api_attribute_range_filter_excludes_unmatched_attribute(client, app):
    """Test that products missing the filtered attribute are strictly excluded."""
    with app.app_context():
        co = Company(name='Missing Attr Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Tablets', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr_storage = Attribute(category_id=cat.category_id, name='Storage', min_value=32, max_value=512, weight=100.0)
        db.session.add(attr_storage)
        db.session.commit()

        p_with_attr = Product(name='Tablet With Storage', category_id=cat.category_id, composite_score=0.8)
        p_without_attr = Product(name='Tablet Without Attr', category_id=cat.category_id, composite_score=0.9)
        db.session.add_all([p_with_attr, p_without_attr])
        db.session.commit()

        pav = ProductAttrValue(product_id=p_with_attr.product_id, attribute_id=attr_storage.attribute_id, raw_value=128.0)
        db.session.add(pav)
        db.session.commit()

        resp = client.get(
            f'/api/v1/search?company_id={co.company_id}&filter_attr_id={attr_storage.attribute_id}&filter_min=64'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total_results'] == 1
        assert data['results'][0]['name'] == 'Tablet With Storage'


def test_api_attribute_range_filter_with_sponsored_exclusion(client, app):
    """Test that sponsored products excluded by range filter do NOT appear in results."""
    with app.app_context():
        co = Company(name='Sponsor Range Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Audio', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr_battery = Attribute(category_id=cat.category_id, name='Battery', min_value=0, max_value=50, weight=100.0)
        db.session.add(attr_battery)
        db.session.commit()

        p_organic = Product(name='Organic 40h Buds', category_id=cat.category_id, composite_score=0.85)
        p_sponsored = Product(name='Sponsored 10h Buds', category_id=cat.category_id, composite_score=0.95, is_sponsored=True)
        db.session.add_all([p_organic, p_sponsored])
        db.session.commit()

        pav1 = ProductAttrValue(product_id=p_organic.product_id, attribute_id=attr_battery.attribute_id, raw_value=40.0)
        pav2 = ProductAttrValue(product_id=p_sponsored.product_id, attribute_id=attr_battery.attribute_id, raw_value=10.0)
        db.session.add_all([pav1, pav2])
        db.session.commit()

        today = date.today()
        sp = SponsoredPlacement(
            product_id=p_sponsored.product_id,
            slot_position=1,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=5),
            is_active=True
        )
        db.session.add(sp)
        db.session.commit()

        # Filter battery >= 30: p_sponsored has battery 10, so it must NOT appear
        resp = client.get(
            f'/api/v1/search?company_id={co.company_id}&category_id={cat.category_id}'
            f'&filter_attr_id={attr_battery.attribute_id}&filter_min=30&include_sponsors=true'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total_results'] == 1
        assert data['results'][0]['name'] == 'Organic 40h Buds'
        # Ensure sponsored low-battery buds do NOT appear
        names = [r['name'] for r in data['results']]
        assert 'Sponsored 10h Buds' not in names


def test_api_attribute_range_filter_invalid_numeric(client, app):
    """Test that invalid numeric filter_min or filter_max returns 400."""
    with app.app_context():
        co = Company(name='Invalid Filter Co')
        db.session.add(co)
        db.session.commit()

        resp1 = client.get(f'/api/v1/search?company_id={co.company_id}&filter_min=invalid')
        assert resp1.status_code == 400
        assert resp1.get_json()['error'] == 'INVALID_FILTER_MIN'

        resp2 = client.get(f'/api/v1/search?company_id={co.company_id}&filter_max=invalid')
        assert resp2.status_code == 400
        assert resp2.get_json()['error'] == 'INVALID_FILTER_MAX'


def test_api_include_sponsors_false_strips_sponsors(client, app):
    """Verify that include_sponsors=false strips sponsored items from search results."""
    with app.app_context():
        co = Company(name='Strip Sponsor Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Audio', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        p_org = Product(name='Organic Product', category_id=cat.category_id, composite_score=0.8)
        p_sp = Product(name='Sponsored Product', category_id=cat.category_id, composite_score=0.9, is_sponsored=True)
        db.session.add_all([p_org, p_sp])
        db.session.commit()

        resp = client.get(
            f'/api/v1/search?company_id={co.company_id}&category_id={cat.category_id}&include_sponsors=false'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        names = [r['name'] for r in data['results']]
        assert 'Organic Product' in names
        assert 'Sponsored Product' not in names


def test_update_product_price_and_attributes(client):
    """Test updating a product's price, rating, and attributes via /api/v1/product/<id>?company_id=1."""
    with client.application.app_context():
        co = Company(company_id=1, name='Noise Official')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Audio', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        attr_price = Attribute(
            category_id=cat.category_id,
            name='Price (INR)',
            min_value=500.0,
            max_value=15000.0,
            weight=50.0,
            lower_is_better=True
        )
        attr_rating = Attribute(
            category_id=cat.category_id,
            name='Rating',
            min_value=1.0,
            max_value=5.0,
            weight=50.0,
            lower_is_better=False
        )
        db.session.add_all([attr_price, attr_rating])
        db.session.commit()

        p = Product(name='Initial Earbuds', category_id=cat.category_id, composite_score=0.2)
        db.session.add(p)
        db.session.commit()

        pav_price = ProductAttrValue(
            product_id=p.product_id,
            attribute_id=attr_price.attribute_id,
            raw_value=12000.0,
            normalized_value=0.2069
        )
        pav_rating = ProductAttrValue(
            product_id=p.product_id,
            attribute_id=attr_rating.attribute_id,
            raw_value=2.0,
            normalized_value=0.25
        )
        db.session.add_all([pav_price, pav_rating])
        db.session.commit()

        prod_id = p.product_id

    # 1. Update product price and rating via PUT with company_id=1
    update_data = {
        'name': 'Updated Pro Earbuds',
        'price': 2000.0,
        'rating': 4.5
    }
    resp = client.put(f'/api/v1/product/{prod_id}?company_id=1', json=update_data)
    assert resp.status_code == 200
    res = resp.get_json()
    assert res['status'] == 'success'
    assert res['message'] == 'Product updated and re-ranked successfully'
    assert res['product_id'] == prod_id
    assert res['name'] == 'Updated Pro Earbuds'
    assert res['category_id'] is not None
    assert res['composite_score'] is not None
    assert res['composite_score'] > 0.2
    assert 'score_pct' in res

    # 2. Verify subsequent GET /api/v1/product/<id> shows updated attribute values
    get_resp = client.get(f'/api/v1/product/{prod_id}?company_id=1')
    assert get_resp.status_code == 200
    get_data = get_resp.get_json()
    assert get_data['status'] == 'success'
    assert get_data['product_id'] == prod_id
    assert get_data['name'] == 'Updated Pro Earbuds'
    assert get_data['composite_score'] == res['composite_score']

    breakdown_map = {item['attribute_name']: item['raw_value'] for item in get_data['score_breakdown']}
    assert breakdown_map['Price (INR)'] == 2000.0
    assert breakdown_map['Rating'] == 4.5

    # 3. Test updating via 'attributes' dict directly
    attr_patch = {
        'attributes': {
            'Price (INR)': 1000.0,
            'Rating': 4.9
        }
    }
    patch_resp = client.patch(f'/api/v1/product/{prod_id}?company_id=1', json=attr_patch)
    assert patch_resp.status_code == 200
    patch_data = patch_resp.get_json()
    assert patch_data['status'] == 'success'
    assert patch_data['composite_score'] > res['composite_score']

    get_resp2 = client.get(f'/api/v1/product/{prod_id}?company_id=1')
    assert get_resp2.status_code == 200
    breakdown_map2 = {item['attribute_name']: item['raw_value'] for item in get_resp2.get_json()['score_breakdown']}
    assert breakdown_map2['Price (INR)'] == 1000.0
    assert breakdown_map2['Rating'] == 4.9


def test_api_get_categories_display_attributes(client, app):
    """Test that /v1/categories returns display_attr_1, display_attr_2, and display_attributes."""
    with app.app_context():
        co = Company(name='Cat Display Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(
            name='Audio',
            company_id=co.company_id,
            display_attr_1='Battery Life',
            display_attr_2='Noise Cancellation'
        )
        db.session.add(cat)
        db.session.commit()

        resp = client.get(f'/api/v1/categories?company_id={co.company_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert len(data['categories']) == 1
        cat_data = data['categories'][0]
        assert cat_data['display_attr_1'] == 'Battery Life'
        assert cat_data['display_attr_2'] == 'Noise Cancellation'
        assert cat_data['display_attributes'] == ['Battery Life', 'Noise Cancellation']


def test_api_search_display_attributes_and_badges(client, app):
    """Test that /v1/search includes display_attr fields and display_badges on products."""
    with app.app_context():
        co = Company(name='Search Badges Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(
            name='Audio Headsets',
            company_id=co.company_id,
            display_attr_1='Battery Life',
            display_attr_2='Water Resistance'
        )
        db.session.add(cat)
        db.session.commit()

        attr_battery = Attribute(category_id=cat.category_id, name='Battery Life', min_value=1.0, max_value=60.0, weight=50.0)
        attr_water = Attribute(category_id=cat.category_id, name='Water Resistance', data_type='binary', weight=50.0)
        db.session.add_all([attr_battery, attr_water])
        db.session.commit()

        p = Product(name='Pro Earbuds ANC', category_id=cat.category_id, composite_score=0.92)
        db.session.add(p)
        db.session.commit()

        pav1 = ProductAttrValue(product_id=p.product_id, attribute_id=attr_battery.attribute_id, raw_value=40.0)
        pav2 = ProductAttrValue(product_id=p.product_id, attribute_id=attr_water.attribute_id, raw_value=1.0)
        db.session.add_all([pav1, pav2])
        db.session.commit()

        resp = client.get(f'/api/v1/search?company_id={co.company_id}&category_id={cat.category_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert data['display_attr_1'] == 'Battery Life'
        assert data['display_attr_2'] == 'Water Resistance'
        assert data['display_attributes'] == ['Battery Life', 'Water Resistance']

        assert len(data['results']) == 1
        prod_data = data['results'][0]
        assert 'display_badges' in prod_data
        badges = prod_data['display_badges']
        assert len(badges) == 2
        assert badges[0]['name'] == 'Battery Life'
        assert badges[0]['raw_value'] == 40.0
        assert badges[0]['value'] == 40.0
        assert badges[0]['data_type'] == 'numeric'

        assert badges[1]['name'] == 'Water Resistance'
        assert badges[1]['raw_value'] == 1.0
        assert badges[1]['value'] == 'YES'
        assert badges[1]['data_type'] == 'binary'


def test_api_search_fallback_display_badges(client, app):
    """Test fallback to first 2 non-price, non-rating attributes when display attributes are not set."""
    with app.app_context():
        co = Company(name='Fallback Badges Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(
            name='Monitors',
            company_id=co.company_id,
            display_attr_1=None,
            display_attr_2=None
        )
        db.session.add(cat)
        db.session.commit()

        attr_price = Attribute(category_id=cat.category_id, name='Price (INR)', min_value=1000, max_value=50000, weight=25.0, lower_is_better=True)
        attr_rating = Attribute(category_id=cat.category_id, name='Rating', min_value=1.0, max_value=5.0, weight=25.0)
        attr_refresh = Attribute(category_id=cat.category_id, name='Refresh Rate', min_value=60, max_value=240, weight=25.0)
        attr_hdr = Attribute(category_id=cat.category_id, name='HDR Support', data_type='binary', weight=25.0)
        db.session.add_all([attr_price, attr_rating, attr_refresh, attr_hdr])
        db.session.commit()

        p = Product(name='Gaming Monitor 27', category_id=cat.category_id, composite_score=0.88)
        db.session.add(p)
        db.session.commit()

        pav1 = ProductAttrValue(product_id=p.product_id, attribute_id=attr_price.attribute_id, raw_value=15000.0)
        pav2 = ProductAttrValue(product_id=p.product_id, attribute_id=attr_rating.attribute_id, raw_value=4.6)
        pav3 = ProductAttrValue(product_id=p.product_id, attribute_id=attr_refresh.attribute_id, raw_value=144.0)
        pav4 = ProductAttrValue(product_id=p.product_id, attribute_id=attr_hdr.attribute_id, raw_value=1.0)
        db.session.add_all([pav1, pav2, pav3, pav4])
        db.session.commit()

        resp = client.get(f'/api/v1/search?company_id={co.company_id}&category_id={cat.category_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert data['display_attr_1'] is None
        assert data['display_attr_2'] is None
        assert data['display_attributes'] == []

        assert len(data['results']) == 1
        badges = data['results'][0]['display_badges']
        assert len(badges) == 2
        badge_names = [b['name'] for b in badges]
        assert 'Price (INR)' not in badge_names
        assert 'Rating' not in badge_names
        assert 'Refresh Rate' in badge_names
        assert 'HDR Support' in badge_names






