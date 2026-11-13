"""seed.py — Populate database with multi-tenant companies, catalog data, and search analytics."""
from app import create_app, db
from app.models import User, Company, Category, Attribute, Product, ProductAttrValue, SponsoredPlacement, SearchLog
from app.ranking.engine import recompute_category_scores
from datetime import date, datetime, timedelta

def seed():
    """Seed the database with platform test data."""
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # 1. Create Super Admin (Platform Operator without tenant lock)
        superadmin = User(
            username='admin',
            email='admin@rankengine.io',
            company_id=None,
            is_admin=True,
            is_superadmin=True
        )
        superadmin.set_password('admin123')
        db.session.add(superadmin)
        db.session.commit()

        # 2. Create Tenant Company 1: TechMart Electronics
        company1 = Company(name='TechMart Electronics')
        db.session.add(company1)
        db.session.commit()
        
        # Create company manager for TechMart
        techmart_manager = User(
            username='techmart_admin',
            email='admin@techmart.com',
            company_id=company1.company_id,
            is_admin=True,
            is_superadmin=False
        )
        techmart_manager.set_password('company123')
        db.session.add(techmart_manager)
        db.session.commit()

        # 3. Create Tenant Company 2: Apex Audio Labs
        company2 = Company(name='Apex Audio Labs')
        db.session.add(company2)
        db.session.commit()

        apex_manager = User(
            username='apex_admin',
            email='manager@apexaudio.com',
            company_id=company2.company_id,
            is_admin=True,
            is_superadmin=False
        )
        apex_manager.set_password('company123')
        db.session.add(apex_manager)
        db.session.commit()
        
        # 4. TechMart Categories: Wireless Earbuds
        earbuds = Category(name='Wireless Earbuds', company_id=company1.company_id)
        db.session.add(earbuds)
        db.session.commit()
        
        battery = Attribute(name='Battery Life (hours)', category_id=earbuds.category_id,
                           data_type='numeric', min_value=0, max_value=40, weight=35.0, lower_is_better=False)
        price = Attribute(name='Price (INR)', category_id=earbuds.category_id,
                         data_type='numeric', min_value=500, max_value=15000, weight=35.0, lower_is_better=True)
        rating = Attribute(name='Rating', category_id=earbuds.category_id,
                          data_type='numeric', min_value=0, max_value=5, weight=15.0, lower_is_better=False)
        anc = Attribute(name='Active Noise Cancelling', category_id=earbuds.category_id,
                        data_type='binary', min_value=0.0, max_value=1.0, weight=15.0, lower_is_better=False)
        db.session.add_all([battery, price, rating, anc])
        db.session.commit()
        
        # Add products with initial search hits and binary anc values (1.0 = Yes, 0.0 = No)
        earbuds_data = [
            ('Sony WF-1000XM5', {'battery': 30, 'price': 12990, 'rating': 4.5, 'anc': 1.0}, 98),
            ('boAt Airdopes 141', {'battery': 42, 'price': 999, 'rating': 3.8, 'anc': 0.0}, 142),
            ('JBL Tune 230NC', {'battery': 28, 'price': 4999, 'rating': 4.2, 'anc': 1.0}, 54),
            ('Samsung Galaxy Buds2 Pro', {'battery': 18, 'price': 11999, 'rating': 4.3, 'anc': 1.0}, 63),
            ('OnePlus Nord Buds 2', {'battery': 36, 'price': 2799, 'rating': 4.0, 'anc': 1.0}, 41),
            ('Apple AirPods Pro 2', {'battery': 30, 'price': 14900, 'rating': 4.7, 'anc': 1.0}, 115),
            ('Realme Buds Air 5', {'battery': 38, 'price': 3499, 'rating': 3.9, 'anc': 1.0}, 32),
        ]
        
        for name, values, hits in earbuds_data:
            product = Product(name=name, category_id=earbuds.category_id, search_count=hits)
            db.session.add(product)
            db.session.flush()
            
            for attr, val in [(battery, values['battery']), (price, values['price']), (rating, values['rating']), (anc, values['anc'])]:
                pav = ProductAttrValue(
                    product_id=product.product_id,
                    attribute_id=attr.attribute_id,
                    raw_value=val
                )
                db.session.add(pav)
        
        db.session.commit()
        recompute_category_scores(earbuds.category_id, db.session, Product, Attribute, ProductAttrValue)
        
        # TechMart Category: Budget Laptops
        laptops = Category(name='Budget Laptops', company_id=company1.company_id)
        db.session.add(laptops)
        db.session.commit()
        
        perf = Attribute(name='Performance Score', category_id=laptops.category_id,
                        min_value=0, max_value=100, weight=40.0)
        lap_price = Attribute(name='Price (INR)', category_id=laptops.category_id,
                             min_value=20000, max_value=80000, weight=35.0, lower_is_better=True)
        display = Attribute(name='Display Quality', category_id=laptops.category_id,
                           min_value=0, max_value=10, weight=25.0)
        db.session.add_all([perf, lap_price, display])
        db.session.commit()
        
        laptop_data = [
            ('HP Pavilion 15', {'perf': 72, 'price': 52990, 'display': 7.5}, 76),
            ('Lenovo IdeaPad 3', {'perf': 65, 'price': 35990, 'display': 6.8}, 58),
            ('Acer Aspire 5', {'perf': 70, 'price': 42990, 'display': 7.2}, 39),
            ('ASUS VivoBook 15', {'perf': 68, 'price': 39990, 'display': 7.0}, 44),
            ('Dell Inspiron 15', {'perf': 75, 'price': 55990, 'display': 8.0}, 85),
        ]
        
        for name, values, hits in laptop_data:
            product = Product(name=name, category_id=laptops.category_id, search_count=hits)
            db.session.add(product)
            db.session.flush()
            for attr, val in [(perf, values['perf']), (lap_price, values['price']), (display, values['display'])]:
                pav = ProductAttrValue(product_id=product.product_id, attribute_id=attr.attribute_id, raw_value=val)
                db.session.add(pav)
        
        db.session.commit()
        recompute_category_scores(laptops.category_id, db.session, Product, Attribute, ProductAttrValue)
        
        # 5. Apex Audio Category: Studio Monitors
        studio = Category(name='Studio Monitors', company_id=company2.company_id)
        db.session.add(studio)
        db.session.commit()

        clarity = Attribute(name='Acoustic Clarity (%)', category_id=studio.category_id,
                            min_value=0, max_value=100, weight=50.0)
        studio_price = Attribute(name='Price (INR)', category_id=studio.category_id,
                                min_value=10000, max_value=60000, weight=50.0, lower_is_better=True)
        studio_rating = Attribute(name='Rating', category_id=studio.category_id,
                                  data_type='numeric', min_value=0.0, max_value=5.0,
                                  weight=0.0, lower_is_better=False, is_active=True)
        db.session.add_all([clarity, studio_price, studio_rating])
        db.session.commit()

        monitors_data = [
            ('Yamaha HS5', {'clarity': 92, 'price': 28500, 'rating': 4.6}, 67),
            ('KRK Rokit 5 G4', {'clarity': 88, 'price': 24900, 'rating': 4.4}, 51),
            ('JBL 305P MkII', {'clarity': 86, 'price': 21000, 'rating': 4.3}, 43),
        ]
        for name, values, hits in monitors_data:
            product = Product(name=name, category_id=studio.category_id, search_count=hits)
            db.session.add(product)
            db.session.flush()
            for attr, val in [(clarity, values['clarity']), (studio_price, values['price']), (studio_rating, values['rating'])]:
                pav = ProductAttrValue(product_id=product.product_id, attribute_id=attr.attribute_id, raw_value=val)
                db.session.add(pav)

        db.session.commit()
        recompute_category_scores(studio.category_id, db.session, Product, Attribute, ProductAttrValue)

        # 6. Sponsored Placement (Anti-bias capped at slot 1)
        boat = Product.query.filter_by(name='boAt Airdopes 141').first()
        if boat:
            sp = SponsoredPlacement(
                product_id=boat.product_id,
                slot_position=1,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                is_active=True
            )
            db.session.add(sp)
            db.session.commit()

        # 7. Seed Search Analytics Logs
        demo_queries = [
            ('noise cancelling earbuds', earbuds.category_id, 4),
            ('boAt Airdopes', earbuds.category_id, 1),
            ('budget student laptop', laptops.category_id, 3),
            ('Sony audio', earbuds.category_id, 1),
            ('Dell Inspiron', laptops.category_id, 1),
            ('studio monitor speakers', studio.category_id, 3),
            ('AirPods Pro', earbuds.category_id, 1),
            ('lightweight laptops under 50k', laptops.category_id, 2),
        ]
        for query_text, cat_id, res_count in demo_queries:
            log_item = SearchLog(
                query_text=query_text,
                category_id=cat_id,
                results_count=res_count,
                searched_at=datetime.utcnow() - timedelta(minutes=15)
            )
            db.session.add(log_item)
        db.session.commit()
        
        print('✅ Database seeded successfully!')
        print('   Platform Superadmin: admin / admin123 (Full Tenant Management & Inspection)')
        print(f'   Tenant 1: {company1.name} (Manager: techmart_admin / company123)')
        print(f'   Tenant 2: {company2.name} (Manager: apex_admin / company123)')
        print('   Categories: Wireless Earbuds (7), Budget Laptops (5), Studio Monitors (3)')
        print('   Search Analytics: 8 query logs, populated hit counters')

if __name__ == '__main__':
    seed()
