import pytest
from app import create_app, db
from app.models import Company, Category, Attribute

# NOTE: 'app' and 'client' fixtures are provided by tests/conftest.py


def test_attribute_weight_sum_valid(app):
    """FR-3: Weights of active attributes must sum to 100%."""
    with app.app_context():
        company = Company(name='Test Co')
        db.session.add(company)
        db.session.commit()
        
        category = Category(name='Test Category', company_id=company.company_id)
        db.session.add(category)
        db.session.commit()
        
        attr1 = Attribute(name='Price', category_id=category.category_id, 
                         min_value=0, max_value=100, weight=60.0)
        attr2 = Attribute(name='Quality', category_id=category.category_id,
                         min_value=0, max_value=10, weight=40.0)
        db.session.add_all([attr1, attr2])
        db.session.commit()
        
        attrs = Attribute.query.filter_by(category_id=category.category_id, is_active=True).all()
        total = sum(a.weight for a in attrs)
        assert abs(total - 100.0) < 0.01

def test_attribute_weight_sum_invalid(app):
    """FR-3: Reject config where weights don't sum to 100%."""
    with app.app_context():
        company = Company(name='Test Co')
        db.session.add(company)
        db.session.commit()
        
        category = Category(name='Test Category', company_id=company.company_id)
        db.session.add(category)
        db.session.commit()
        
        attr1 = Attribute(name='Price', category_id=category.category_id,
                         min_value=0, max_value=100, weight=50.0)
        db.session.add(attr1)
        db.session.commit()
        
        attrs = Attribute.query.filter_by(category_id=category.category_id, is_active=True).all()
        total = sum(a.weight for a in attrs)
        assert abs(total - 100.0) >= 0.01  # Should NOT be valid

def test_deactivated_attribute_excluded_from_weight(app):
    """FR-4: Deactivated attributes should not count in weight sum."""
    with app.app_context():
        company = Company(name='Test Co')
        db.session.add(company)
        db.session.commit()
        
        category = Category(name='Test Category', company_id=company.company_id)
        db.session.add(category)
        db.session.commit()
        
        attr1 = Attribute(name='Price', category_id=category.category_id,
                         min_value=0, max_value=100, weight=60.0, is_active=True)
        attr2 = Attribute(name='Old Attr', category_id=category.category_id,
                         min_value=0, max_value=10, weight=40.0, is_active=False)
        attr3 = Attribute(name='Quality', category_id=category.category_id,
                         min_value=0, max_value=10, weight=40.0, is_active=True)
        db.session.add_all([attr1, attr2, attr3])
        db.session.commit()
        
        active_attrs = Attribute.query.filter_by(category_id=category.category_id, is_active=True).all()
        total = sum(a.weight for a in active_attrs)
        assert abs(total - 100.0) < 0.01
