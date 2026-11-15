"""seed.py — Populate database with Noise Official catalog, attributes, and search analytics."""
import os
from datetime import date, datetime, timedelta, timezone
from app import create_app, db
from app.models import (
    User, Company, Category, Attribute, Product, ProductAttrValue,
    SponsoredPlacement, SearchLog
)
from app.ranking.engine import recompute_category_scores


def seed():
    """Seed the database with the complete Noise Official product catalog."""
    app = create_app(os.getenv('FLASK_CONFIG') or 'development')
    with app.app_context():
        print("🌱 Seeding Weighted Ranking Engine database with Noise Official catalog...")
        db.drop_all()
        db.create_all()

        # -------------------------------------------------------------
        # 1. Super Admin (Platform Operator without tenant lock)
        # -------------------------------------------------------------
        superadmin = User(
            username='admin',
            email='admin@rankengine.io',
            company_id=None,
            is_admin=True,
            is_superadmin=True
        )
        superadmin.set_password('admin123')
        db.session.add(superadmin)

        # -------------------------------------------------------------
        # 2. Tenant Company 1: Noise Official & Managers
        # -------------------------------------------------------------
        company1 = Company(company_id=1, name='Noise Official')
        db.session.add(company1)
        db.session.flush()

        techmart_manager = User(
            username='techmart_admin',
            email='admin@techmart.com',
            company_id=company1.company_id,
            is_admin=True,
            is_superadmin=False
        )
        techmart_manager.set_password('company123')
        db.session.add(techmart_manager)

        noise_manager = User(
            username='noise_admin',
            email='admin@gonoise.com',
            company_id=company1.company_id,
            is_admin=True,
            is_superadmin=False
        )
        noise_manager.set_password('company123')
        db.session.add(noise_manager)
        db.session.commit()

        # -------------------------------------------------------------
        # 3. Create the 5 Official Categories for Noise Official
        # Explicit Category IDs: 4 (Earbuds), 5 (Smartwatches), 6 (Neckbands), 7 (Headphones), 8 (Eyewear)
        # -------------------------------------------------------------
        category_configs = {
            'Wireless Earbuds': {
                'id': 4,
                'display_attr_1': 'Battery Life (hours)',
                'display_attr_2': 'Active Noise Cancelling',
                'attrs': [
                    {'name': 'Battery Life (hours)', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 100.0, 'weight': 35.0, 'lower_is_better': False},
                    {'name': 'Price (INR)', 'data_type': 'numeric', 'min_value': 500.0, 'max_value': 15000.0, 'weight': 35.0, 'lower_is_better': True},
                    {'name': 'Rating', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 5.0, 'weight': 15.0, 'lower_is_better': False},
                    {'name': 'Active Noise Cancelling', 'data_type': 'binary', 'min_value': 0.0, 'max_value': 1.0, 'weight': 15.0, 'lower_is_better': False}
                ]
            },
            'Smartwatches': {
                'id': 5,
                'display_attr_1': 'Battery Life (hours)',
                'display_attr_2': 'Rating',
                'attrs': [
                    {'name': 'Battery Life (hours)', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 300.0, 'weight': 35.0, 'lower_is_better': False},
                    {'name': 'Price (INR)', 'data_type': 'numeric', 'min_value': 1000.0, 'max_value': 15000.0, 'weight': 35.0, 'lower_is_better': True},
                    {'name': 'Rating', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 5.0, 'weight': 30.0, 'lower_is_better': False}
                ]
            },
            'Neckbands': {
                'id': 6,
                'display_attr_1': 'Battery Life (hours)',
                'display_attr_2': 'Active Noise Cancelling',
                'attrs': [
                    {'name': 'Battery Life (hours)', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 120.0, 'weight': 35.0, 'lower_is_better': False},
                    {'name': 'Price (INR)', 'data_type': 'numeric', 'min_value': 500.0, 'max_value': 10000.0, 'weight': 35.0, 'lower_is_better': True},
                    {'name': 'Rating', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 5.0, 'weight': 15.0, 'lower_is_better': False},
                    {'name': 'Active Noise Cancelling', 'data_type': 'binary', 'min_value': 0.0, 'max_value': 1.0, 'weight': 15.0, 'lower_is_better': False}
                ]
            },
            'Headphones': {
                'id': 7,
                'display_attr_1': 'Battery Life (hours)',
                'display_attr_2': 'Active Noise Cancelling',
                'attrs': [
                    {'name': 'Battery Life (hours)', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 100.0, 'weight': 35.0, 'lower_is_better': False},
                    {'name': 'Price (INR)', 'data_type': 'numeric', 'min_value': 500.0, 'max_value': 15000.0, 'weight': 35.0, 'lower_is_better': True},
                    {'name': 'Rating', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 5.0, 'weight': 15.0, 'lower_is_better': False},
                    {'name': 'Active Noise Cancelling', 'data_type': 'binary', 'min_value': 0.0, 'max_value': 1.0, 'weight': 15.0, 'lower_is_better': False}
                ]
            },
            'Smart Eyewear': {
                'id': 8,
                'display_attr_1': 'Battery Life (hours)',
                'display_attr_2': 'Rating',
                'attrs': [
                    {'name': 'Battery Life (hours)', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 24.0, 'weight': 35.0, 'lower_is_better': False},
                    {'name': 'Price (INR)', 'data_type': 'numeric', 'min_value': 1000.0, 'max_value': 15000.0, 'weight': 35.0, 'lower_is_better': True},
                    {'name': 'Rating', 'data_type': 'numeric', 'min_value': 0.0, 'max_value': 5.0, 'weight': 30.0, 'lower_is_better': False}
                ]
            }
        }

        created_cats = {}
        attr_objs = {}

        for cat_name, conf in category_configs.items():
            cat = Category(
                category_id=conf['id'],
                name=cat_name,
                company_id=company1.company_id,
                display_attr_1=conf.get('display_attr_1'),
                display_attr_2=conf.get('display_attr_2')
            )
            db.session.add(cat)
            db.session.flush()
            created_cats[cat_name] = cat

            attr_objs[cat_name] = {}
            for attr_def in conf['attrs']:
                attr = Attribute(
                    category_id=cat.category_id,
                    name=attr_def['name'],
                    data_type=attr_def['data_type'],
                    min_value=attr_def['min_value'],
                    max_value=attr_def['max_value'],
                    weight=attr_def['weight'],
                    lower_is_better=attr_def['lower_is_better']
                )
                db.session.add(attr)
                db.session.flush()
                attr_objs[cat_name][attr_def['name']] = attr

        db.session.commit()

        # -------------------------------------------------------------
        # 4. Catalog Products (16 Noise products matching Storefront)
        # -------------------------------------------------------------
        products_data = [
            # Smartwatches (Category ID 5)
            {
                "name": "Noise ColorFit Ultra 3",
                "category": "Smartwatches",
                "price": 2999.0,
                "battery": 168.0,
                "rating": 4.5,
                "anc": 0.0,
                "hits": 184,
                "image_url": "https://www.gonoise.com/cdn/shop/files/NoiseColorFitUltra3-BlackEliteEdition_1_grande.png?v=1695122129"
            },
            {
                "name": "NoiseFit Halo",
                "category": "Smartwatches",
                "price": 2499.0,
                "battery": 168.0,
                "rating": 4.4,
                "anc": 0.0,
                "hits": 142,
                "image_url": "https://www.gonoise.com/cdn/shop/files/1_1_b18f77db-5fef-4698-9902-a48fec2b8efa_grande.png?v=1704963291"
            },
            {
                "name": "Noise ColorFit Icon 2",
                "category": "Smartwatches",
                "price": 1499.0,
                "battery": 120.0,
                "rating": 4.2,
                "anc": 0.0,
                "hits": 289,
                "image_url": "https://www.gonoise.com/cdn/shop/products/Icon2-5_grande.png?v=1681610912"
            },
            {
                "name": "Noise ColorFit Pro 4 Alpha",
                "category": "Smartwatches",
                "price": 3499.0,
                "battery": 168.0,
                "rating": 4.6,
                "anc": 0.0,
                "hits": 92,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/products/1_0ba84c50-3527-4c98-b643-f3f4f3075c27.png?v=1686911647"
            },
            {
                "name": "Noise Diva Smartwatch",
                "category": "Smartwatches",
                "price": 2999.0,
                "battery": 96.0,
                "rating": 4.4,
                "anc": 0.0,
                "hits": 64,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/files/Artboard19_result_5250da54-389e-4afa-a440-870f0bae2459.webp?v=1776673795"
            },
            
            # Wireless Earbuds (Category ID 4)
            {
                "name": "Noise Buds VS102",
                "category": "Wireless Earbuds",
                "price": 1099.0,
                "battery": 50.0,
                "rating": 4.1,
                "anc": 0.0,
                "hits": 352,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/files/1_9e839f18-7b82-4b71-ab98-471982ca91ef.png?v=1682439948"
            },
            {
                "name": "Noise Buds VS404",
                "category": "Wireless Earbuds",
                "price": 1299.0,
                "battery": 45.0,
                "rating": 4.3,
                "anc": 0.0,
                "hits": 218,
                "image_url": "https://www.gonoise.com/cdn/shop/files/image_2023_09_19T10_11_28_596Z_grande.png?v=1695119844"
            },
            {
                "name": "Noise Air Buds Pro 2 with ANC",
                "category": "Wireless Earbuds",
                "price": 2499.0,
                "battery": 40.0,
                "rating": 4.5,
                "anc": 1.0,
                "hits": 165,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/files/3.74_copy_result.webp?v=1744177541"
            },
            {
                "name": "Noise Buds Combat",
                "category": "Wireless Earbuds",
                "price": 1399.0,
                "battery": 45.0,
                "rating": 4.2,
                "anc": 0.0,
                "hits": 112,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/products/Black-Combat-Carousel-500x500-1.png?v=1673874381"
            },
            {
                "name": "Noise Buds VS201 V2",
                "category": "Wireless Earbuds",
                "price": 1199.0,
                "battery": 36.0,
                "rating": 4.0,
                "anc": 0.0,
                "hits": 189,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/products/b3.png?v=1627585394"
            },
            {
                "name": "Noise Master Buds",
                "category": "Wireless Earbuds",
                "price": 3999.0,
                "battery": 48.0,
                "rating": 4.7,
                "anc": 1.0,
                "hits": 78,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/files/Artboard9_result_e8b91d73-7a1a-4375-a0ce-f6a825fad7e2.webp?v=1773898750"
            },
            {
                "name": "Noise Pure Pods",
                "category": "Wireless Earbuds",
                "price": 2999.0,
                "battery": 80.0,
                "rating": 4.3,
                "anc": 0.0,
                "hits": 86,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/files/5_78ab6c3d-0bf3-495b-9580-c640e5cf459d.webp?v=1720444316"
            },

            # Neckbands (Category ID 6)
            {
                "name": "Noise Tune Charge",
                "category": "Neckbands",
                "price": 999.0,
                "battery": 35.0,
                "rating": 4.2,
                "anc": 0.0,
                "hits": 274,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/products/Artboard1_f25c5842-36c2-4588-a9b3-f6482b5e28c1.png?v=1627585694"
            },
            {
                "name": "Noise Flair XL",
                "category": "Neckbands",
                "price": 1299.0,
                "battery": 80.0,
                "rating": 4.4,
                "anc": 0.0,
                "hits": 139,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/products/2.1699.png?v=1656585389"
            },

            # Headphones (Category ID 7)
            {
                "name": "Noise Two Wireless Headphones",
                "category": "Headphones",
                "price": 1799.0,
                "battery": 50.0,
                "rating": 4.2,
                "anc": 0.0,
                "hits": 69,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/files/1_3941f406-f4ff-4692-8ef4-6719497a0f56.webp?v=1720759157"
            },

            # Smart Eyewear (Category ID 8)
            {
                "name": "Noise i1 Smart Glasses",
                "category": "Smart Eyewear",
                "price": 4999.0,
                "battery": 9.0,
                "rating": 4.1,
                "anc": 0.0,
                "hits": 42,
                "image_url": "https://cdn.shopify.com/s/files/1/0997/6284/products/S1_57e9472f-ddeb-4b8d-b74c-2ef1bf551ab1.png?v=1682400943"
            }
        ]

        air_buds_pro_product = None

        for p_data in products_data:
            cat_name = p_data['category']
            cat = created_cats[cat_name]

            prod = Product(
                name=p_data['name'],
                category_id=cat.category_id,
                search_count=p_data['hits'],
                image_url=p_data.get('image_url')
            )
            db.session.add(prod)
            db.session.flush()

            if prod.name == "Noise Air Buds Pro 2 with ANC":
                air_buds_pro_product = prod

            cat_attrs = attr_objs[cat_name]
            for attr_name, attr_model in cat_attrs.items():
                if attr_name == 'Battery Life (hours)':
                    val = p_data['battery']
                elif attr_name == 'Price (INR)':
                    val = p_data['price']
                elif attr_name == 'Rating':
                    val = p_data['rating']
                elif attr_name == 'Active Noise Cancelling':
                    val = p_data['anc']
                else:
                    val = 0.0

                pav = ProductAttrValue(
                    product_id=prod.product_id,
                    attribute_id=attr_model.attribute_id,
                    raw_value=val
                )
                db.session.add(pav)

        db.session.commit()

        # -------------------------------------------------------------
        # 5. Recompute composite scores for all categories
        # -------------------------------------------------------------
        for cat_name, cat in created_cats.items():
            recompute_category_scores(cat.category_id, db.session, Product, Attribute, ProductAttrValue)

        # -------------------------------------------------------------
        # 6. Add active sponsored placement for Noise Air Buds Pro 2 with ANC
        # -------------------------------------------------------------
        if air_buds_pro_product:
            sp = SponsoredPlacement(
                product_id=air_buds_pro_product.product_id,
                slot_position=1,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                is_active=True
            )
            db.session.add(sp)
            db.session.commit()

        # -------------------------------------------------------------
        # 7. Add seed search logs for insights
        # -------------------------------------------------------------
        search_queries = [
            ("ear phones", created_cats['Wireless Earbuds'].category_id, 7),
            ("earbuds", created_cats['Wireless Earbuds'].category_id, 7),
            ("smart watch", created_cats['Smartwatches'].category_id, 5),
            ("anc earbuds", created_cats['Wireless Earbuds'].category_id, 2),
            ("noise smart watch", created_cats['Smartwatches'].category_id, 5),
            ("wireless neckband", created_cats['Neckbands'].category_id, 2),
            ("noise headphones", created_cats['Headphones'].category_id, 1),
            ("smart glasses", created_cats['Smart Eyewear'].category_id, 1)
        ]
        for q_text, cid, r_cnt in search_queries:
            slog = SearchLog(
                query_text=q_text,
                category_id=cid,
                results_count=r_cnt,
                searched_at=datetime.now(timezone.utc) - timedelta(minutes=10)
            )
            db.session.add(slog)
        db.session.commit()

        print("✅ Database seeded successfully with 16 Noise products across 5 categories!")
        print("   Platform Superadmin : admin / admin123")
        print("   Tenant ('Noise Official'): techmart_admin / company123, noise_admin / company123")
        print("   Categories: Wireless Earbuds (7), Smartwatches (5), Neckbands (2), Headphones (1), Smart Eyewear (1)")


if __name__ == '__main__':
    seed()
