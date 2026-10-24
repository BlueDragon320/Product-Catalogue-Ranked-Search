import pytest
from datetime import datetime
from app.ranking.engine import normalize_value, compute_product_score, rank_products, recompute_category_scores
from app.models import Product, Attribute, ProductAttrValue, Category
from app import db

def test_normalize_value_basic():
    assert normalize_value(50.0, 0.0, 100.0) == 0.5
    
def test_normalize_value_lower_is_better():
    assert normalize_value(50.0, 0.0, 100.0, lower_is_better=True) == 0.5
    assert normalize_value(25.0, 0.0, 100.0, lower_is_better=True) == 0.75

def test_normalize_value_same_min_max():
    assert normalize_value(50.0, 50.0, 50.0) == 0.5

def test_normalize_value_at_boundaries():
    assert normalize_value(0.0, 0.0, 100.0) == 0.0
    assert normalize_value(100.0, 0.0, 100.0) == 1.0

def test_compute_product_score_single_attribute():
    values = [{
        'raw_value': 50.0,
        'min_value': 0.0,
        'max_value': 100.0,
        'weight': 100.0,
        'lower_is_better': False
    }]
    assert compute_product_score(values) == 0.5

def test_compute_product_score_multiple_attributes():
    values = [
        {
            'raw_value': 50.0,
            'min_value': 0.0,
            'max_value': 100.0,
            'weight': 50.0,
            'lower_is_better': False
        },
        {
            'raw_value': 10.0,
            'min_value': 0.0,
            'max_value': 10.0,
            'weight': 50.0,
            'lower_is_better': False
        }
    ]
    assert compute_product_score(values) == 0.75

def test_compute_product_score_empty():
    assert compute_product_score([]) == 0.0

def test_rank_products_by_score():
    products = [
        {'product_id': 1, 'name': 'A', 'composite_score': 0.5, 'created_at': datetime(2023, 1, 1)},
        {'product_id': 2, 'name': 'B', 'composite_score': 0.8, 'created_at': datetime(2023, 1, 1)}
    ]
    ranked = rank_products(products)
    assert ranked[0]['product_id'] == 2

def test_rank_products_tiebreak_created_at():
    products = [
        {'product_id': 1, 'name': 'A', 'composite_score': 0.8, 'created_at': datetime(2023, 1, 1)},
        {'product_id': 2, 'name': 'B', 'composite_score': 0.8, 'created_at': datetime(2023, 1, 2)}
    ]
    ranked = rank_products(products)
    assert ranked[0]['product_id'] == 2

def test_rank_products_tiebreak_product_id():
    products = [
        {'product_id': 2, 'name': 'B', 'composite_score': 0.8, 'created_at': datetime(2023, 1, 1)},
        {'product_id': 1, 'name': 'A', 'composite_score': 0.8, 'created_at': datetime(2023, 1, 1)}
    ]
    ranked = rank_products(products)
    assert ranked[0]['product_id'] == 1

def test_recompute_category_scores(app):
    with app.app_context():
        # Clean up
        db.session.query(ProductAttrValue).delete()
        db.session.query(Product).delete()
        db.session.query(Attribute).delete()
        db.session.query(Category).delete()
        db.session.commit()

        # Add data
        cat = Category(name="Laptops")
        db.session.add(cat)
        db.session.commit()

        attr = Attribute(category_id=cat.category_id, name="RAM", min_value=0, max_value=32, weight=100.0, is_active=True)
        db.session.add(attr)
        db.session.commit()

        p = Product(category_id=cat.category_id, name="MacBook")
        db.session.add(p)
        db.session.commit()

        pav = ProductAttrValue(product_id=p.product_id, attribute_id=attr.attribute_id, raw_value=16.0)
        db.session.add(pav)
        db.session.commit()

        recompute_category_scores(cat.category_id, db.session, Product, Attribute, ProductAttrValue)

        updated_p = db.session.get(Product, p.product_id)
        assert updated_p.composite_score == 0.5

def test_binary_attribute_normalization():
    """Verify binary attributes scale Yes=1.0 and No=0.0 with directionality."""
    # Yes (1.0) when higher is better
    assert normalize_value(1.0, 0.0, 1.0, lower_is_better=False) == 1.0
    # No (0.0) when higher is better
    assert normalize_value(0.0, 0.0, 1.0, lower_is_better=False) == 0.0
    # Inverted: Yes (1.0) when lower is better
    assert normalize_value(1.0, 0.0, 1.0, lower_is_better=True) == 0.0
    # Inverted: No (0.0) when lower is better
    assert normalize_value(0.0, 0.0, 1.0, lower_is_better=True) == 1.0

def test_binary_attribute_weighted_sum(app):
    """Test multi-criteria scoring combining numeric and binary attributes."""
    with app.app_context():
        product_values = [
            # 60% weight on numeric (100 out of 200 => 0.5)
            {'raw_value': 100.0, 'min_value': 0.0, 'max_value': 200.0, 'weight': 60.0, 'lower_is_better': False},
            # 40% weight on binary Yes (1.0 => 1.0)
            {'raw_value': 1.0, 'min_value': 0.0, 'max_value': 1.0, 'weight': 40.0, 'lower_is_better': False}
        ]
        score = compute_product_score(product_values)
        # Expected: 0.5 * 0.6 + 1.0 * 0.4 = 0.3 + 0.4 = 0.70
        assert round(score, 2) == 0.70


def test_rank_products_string_and_int_created_at():
    """Verify rank_products safely handles string ISO and int timestamp created_at values."""
    products = [
        {'product_id': 1, 'name': 'Old', 'composite_score': 0.8, 'created_at': '2023-01-01T00:00:00'},
        {'product_id': 2, 'name': 'New', 'composite_score': 0.8, 'created_at': 1700000000}
    ]
    ranked = rank_products(products)
    assert ranked[0]['product_id'] == 2


