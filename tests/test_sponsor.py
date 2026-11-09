import pytest
from datetime import date, timedelta
from app import create_app, db
from app.models import Company, Category, Product, SponsoredPlacement
from app.ranking.helpers import insert_sponsored_placements

# 'app' fixture comes from conftest.py

def test_sponsor_insertion_basic(app):
    """FR-15: Sponsored product appears in slot 1."""
    with app.app_context():
        company = Company(name='Test Co')
        db.session.add(company)
        db.session.commit()
        category = Category(name='Test', company_id=company.company_id)
        db.session.add(category)
        db.session.commit()
        
        products = []
        for i in range(5):
            p = Product(name=f'Product {i}', category_id=category.category_id, composite_score=0.5-i*0.1)
            db.session.add(p)
            products.append(p)
        db.session.commit()
        
        sponsored = [products[3]]  # Sponsor a lower-ranked product
        organic = [p for p in products if p not in sponsored]
        
        results = insert_sponsored_placements(products, sponsored)
        
        assert results[0]['is_sponsored'] == True
        assert results[0]['product'].product_id == products[3].product_id
        # Rest should be organic
        for r in results[1:]:
            assert r['is_sponsored'] == False

def test_sponsor_cap_enforcement(app):
    """NFR-5.6: No more than 1 sponsored per 5 results."""
    with app.app_context():
        company = Company(name='Test Co')
        db.session.add(company)
        db.session.commit()
        category = Category(name='Test', company_id=company.company_id)
        db.session.add(category)
        db.session.commit()
        
        products = []
        for i in range(10):
            p = Product(name=f'Product {i}', category_id=category.category_id, composite_score=1.0-i*0.1)
            db.session.add(p)
            products.append(p)
        db.session.commit()
        
        sponsored = [products[8], products[9]]
        results = insert_sponsored_placements(products, sponsored)
        
        # Check that sponsored items are at most 1 per 5 slots
        for i in range(0, len(results), 5):
            chunk = results[i:i+5]
            sponsor_count = sum(1 for r in chunk if r['is_sponsored'])
            assert sponsor_count <= 1

def test_sponsor_expiry(app):
    """FR-17: Expired sponsorships should not show."""
    with app.app_context():
        company = Company(name='Test Co')
        db.session.add(company)
        db.session.commit()
        category = Category(name='Test', company_id=company.company_id)
        db.session.add(category)
        db.session.commit()
        
        p = Product(name='Sponsored Product', category_id=category.category_id)
        db.session.add(p)
        db.session.commit()
        
        # Expired placement
        sp = SponsoredPlacement(
            product_id=p.product_id,
            slot_position=1,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() - timedelta(days=1),
            is_active=True
        )
        db.session.add(sp)
        db.session.commit()
        
        from app.ranking.helpers import get_active_sponsored_products
        active = get_active_sponsored_products(category.category_id, Product, SponsoredPlacement)
        assert len(active) == 0

def test_sponsor_active(app):
    """FR-14: Active sponsorship should show."""
    with app.app_context():
        company = Company(name='Test Co')
        db.session.add(company)
        db.session.commit()
        category = Category(name='Test', company_id=company.company_id)
        db.session.add(category)
        db.session.commit()
        
        p = Product(name='Sponsored Product', category_id=category.category_id)
        db.session.add(p)
        db.session.commit()
        
        sp = SponsoredPlacement(
            product_id=p.product_id,
            slot_position=1,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
            is_active=True
        )
        db.session.add(sp)
        db.session.commit()
        
        from app.ranking.helpers import get_active_sponsored_products
        active = get_active_sponsored_products(category.category_id, Product, SponsoredPlacement)
        assert len(active) == 1
