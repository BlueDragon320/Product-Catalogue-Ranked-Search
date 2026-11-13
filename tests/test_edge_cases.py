import pytest
from app import create_app, db
from app.models import Company, Category, Attribute, Product, ProductAttrValue
from app.ranking.engine import normalize_value, compute_product_score, recompute_category_scores

def test_empty_category_ranking(app):
    """Edge case: Category with no products should not crash."""
    with app.app_context():
        company = Company(name='Edge Co')
        db.session.add(company)
        db.session.commit()
        category = Category(name='Empty Category', company_id=company.company_id)
        db.session.add(category)
        db.session.commit()
        
        recompute_category_scores(category.category_id, db.session, Product, Attribute, ProductAttrValue)
        # Should not raise

def test_zero_weight_attributes(app):
    """Edge case: Attribute with 0 weight should contribute nothing to score."""
    with app.app_context():
        vals = [{'raw_value': 50, 'min_value': 0, 'max_value': 100, 'weight': 0, 'lower_is_better': False}]
        score = compute_product_score(vals)
        assert score == 0.0

def test_normalize_value_out_of_range():
    """Edge case: raw value outside min-max should be clamped."""
    result = normalize_value(150, 0, 100)
    assert result == 1.0  # Clamped to max
    
    result = normalize_value(-10, 0, 100)
    assert result == 0.0  # Clamped to min

def test_all_products_same_score(app):
    """Edge case: All products have identical scores — tie-break applies."""
    from datetime import datetime
    from app.ranking.engine import rank_products
    
    with app.app_context():
        products = [
            {'product_id': 3, 'name': 'C', 'composite_score': 0.5, 'created_at': datetime(2026, 1, 1)},
            {'product_id': 1, 'name': 'A', 'composite_score': 0.5, 'created_at': datetime(2026, 1, 1)},
            {'product_id': 2, 'name': 'B', 'composite_score': 0.5, 'created_at': datetime(2026, 1, 1)},
        ]
        ranked = rank_products(products)
        # Same score, same created_at → sort by product_id ASC
        assert ranked[0]['product_id'] == 1
        assert ranked[1]['product_id'] == 2
        assert ranked[2]['product_id'] == 3

def test_single_product_ranking(app):
    """Edge case: Category with one product should rank it first."""
    from datetime import datetime
    from app.ranking.engine import rank_products
    
    with app.app_context():
        products = [{'product_id': 1, 'name': 'Solo', 'composite_score': 0.75, 'created_at': datetime(2026, 1, 1)}]
        ranked = rank_products(products)
        assert len(ranked) == 1
        assert ranked[0]['product_id'] == 1

def test_lower_is_better_normalization():
    """Verify lower_is_better inverts the normalized value correctly."""
    # Price: min=500, max=15000. Lower price = better.
    # Product with price 500 (cheapest) should get norm = 1.0
    assert normalize_value(500, 500, 15000, lower_is_better=True) == 1.0
    # Product with price 15000 (most expensive) should get norm = 0.0
    assert normalize_value(15000, 500, 15000, lower_is_better=True) == 0.0
    # Product with price 7750 (middle) should get norm = 0.5
    assert normalize_value(7750, 500, 15000, lower_is_better=True) == 0.5

def test_maximum_score_product(app):
    """Edge case: Product with all best values should score 1.0."""
    with app.app_context():
        vals = [
            {'raw_value': 100, 'min_value': 0, 'max_value': 100, 'weight': 50, 'lower_is_better': False},
            {'raw_value': 0, 'min_value': 0, 'max_value': 100, 'weight': 50, 'lower_is_better': True},
        ]
        score = compute_product_score(vals)
        assert abs(score - 1.0) < 0.001
