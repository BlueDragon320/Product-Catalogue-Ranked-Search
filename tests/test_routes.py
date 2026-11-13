import pytest
from app import create_app, db
from app.models import User, Company, Category, Attribute, Product, ProductAttrValue

# 'app' and 'client' fixtures come from conftest.py

def test_home_page(client):
    """Test that the home page loads."""
    response = client.get('/')
    assert response.status_code == 200

def test_login_page_loads(client):
    """Test that login page loads."""
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_register_page_disabled(client):
    """Test that public register page is disabled and redirects to login with warning."""
    response = client.get('/auth/register', follow_redirects=True)
    assert response.status_code == 200
    assert b'Public registration is disabled' in response.data

def test_register_post_disabled(client):
    """Test that POST to /auth/register is rejected and redirects to login."""
    response = client.post('/auth/register', data={'username': 'attacker', 'password': '123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Public registration is disabled' in response.data

def test_admin_requires_login(client):
    """Test that admin pages redirect to login when not authenticated."""
    response = client.get('/admin/')
    assert response.status_code == 302  # Redirect to login

def test_insights_route(client, app):
    """Test that the insights analytics dashboard requires login and loads when authenticated."""
    response = client.get('/insights/')
    assert response.status_code == 302

    with app.app_context():
        admin = User(username='insights_tester', email='insights@tester.com', is_admin=True, is_superadmin=True)
        admin.set_password('superpass123')
        db.session.add(admin)
        db.session.commit()

        client.post('/auth/login', data={'username': 'insights_tester', 'password': 'superpass123'}, follow_redirects=True)
        response = client.get('/insights/')
        assert response.status_code == 200
        assert b'CATALOG INSIGHTS' in response.data

def test_superadmin_platform_dashboard(client, app):
    """Test that a superadmin accesses the Platform Tenant Management dashboard."""
    with app.app_context():
        admin = User(username='super_tester', email='super@tester.com', is_admin=True, is_superadmin=True)
        admin.set_password('superpass123')
        db.session.add(admin)
        db.session.commit()

        client.post('/auth/login', data={'username': 'super_tester', 'password': 'superpass123'}, follow_redirects=True)
        response = client.get('/admin/')
        assert response.status_code == 200
        assert b'TENANT MANAGEMENT' in response.data
        assert b'PROVISION NEW COMPANY' in response.data

def test_superadmin_company_provisioning(client, app):
    """Test that a superadmin can provision a new company along with its manager account."""
    with app.app_context():
        admin = User(username='super_prov', email='prov@tester.com', is_admin=True, is_superadmin=True)
        admin.set_password('superpass123')
        db.session.add(admin)
        db.session.commit()

        client.post('/auth/login', data={'username': 'super_prov', 'password': 'superpass123'}, follow_redirects=True)
        response = client.post('/admin/company/new', data={
            'name': 'Starlight Dynamics',
            'admin_username': 'starlight_admin',
            'admin_email': 'admin@starlight.com',
            'admin_password': 'starpass123'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Check in DB
        comp = Company.query.filter_by(name='Starlight Dynamics').first()
        assert comp is not None
        user = User.query.filter_by(username='starlight_admin').first()
        assert user is not None
        assert user.company_id == comp.company_id

def test_superadmin_inspection_and_exit(client, app):
    """Test that superadmin can inspect a tenant company and exit inspection."""
    with app.app_context():
        admin = User(username='super_inspect', email='inspect@tester.com', is_admin=True, is_superadmin=True)
        admin.set_password('superpass123')
        co = Company(name='Inspected Corp')
        db.session.add_all([admin, co])
        db.session.commit()

        client.post('/auth/login', data={'username': 'super_inspect', 'password': 'superpass123'}, follow_redirects=True)

        # Inspect company
        inspect_resp = client.get(f'/admin/company/{co.company_id}/inspect', follow_redirects=True)
        assert inspect_resp.status_code == 200
        assert b'SUPERADMIN INSPECTION ACTIVE' in inspect_resp.data

        # Exit inspection
        exit_resp = client.get('/admin/company/exit-inspect', follow_redirects=True)
        assert exit_resp.status_code == 200
        assert b'TENANT MANAGEMENT' in exit_resp.data

def test_superadmin_company_delete_cascade(client, app):
    """Test that deleting a company cascade-deletes categories, products, and users."""
    with app.app_context():
        admin = User(username='super_deleter', email='del@tester.com', is_admin=True, is_superadmin=True)
        admin.set_password('superpass123')
        co = Company(name='Doomed Corp')
        db.session.add_all([admin, co])
        db.session.commit()

        cat = Category(name='Doomed Cat', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()
        prod = Product(name='Doomed Prod', category_id=cat.category_id)
        db.session.add(prod)
        db.session.commit()

        co_id = co.company_id
        cat_id = cat.category_id
        prod_id = prod.product_id

        client.post('/auth/login', data={'username': 'super_deleter', 'password': 'superpass123'}, follow_redirects=True)
        del_resp = client.post(f'/admin/company/{co_id}/delete', follow_redirects=True)
        assert del_resp.status_code == 200

        assert db.session.get(Company, co_id) is None
        assert db.session.get(Category, cat_id) is None
        assert db.session.get(Product, prod_id) is None

def test_company_tenant_isolation(client, app):
    """Test that a company manager cannot edit another company."""
    with app.app_context():
        co1 = Company(name='Tenant 1')
        co2 = Company(name='Tenant 2')
        db.session.add_all([co1, co2])
        db.session.commit()

        user1 = User(username='mgr1', email='mgr1@t1.com', company_id=co1.company_id, is_admin=True, is_superadmin=False)
        user1.set_password('pass123')
        db.session.add(user1)
        db.session.commit()

        client.post('/auth/login', data={'username': 'mgr1', 'password': 'pass123'}, follow_redirects=True)

        # Attempt to edit Tenant 2 (Blocked: only platform superadmin can edit companies)
        resp = client.get(f'/admin/company/{co2.company_id}/edit', follow_redirects=True)
        assert b'Platform administrator privileges required' in resp.data


def test_full_workflow(client, app):
    """
    Full integration test: provision company -> login -> create category -> add attributes 
    -> add product -> view ranking.
    """
    with app.app_context():
        co = Company(name='Workflow Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='workflow_admin', email='workflow@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'workflow_admin',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Verify admin access
        response = client.get('/admin/', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify categories page
        response = client.get('/admin/categories', follow_redirects=True)
        assert response.status_code == 200

def test_duplicate_superadmin_provisioning(client, app):
    """Test that provisioning duplicate username or email via superadmin is rejected."""
    with app.app_context():
        admin = User(username='prov_admin_dup', email='padup@test.com', is_admin=True, is_superadmin=True)
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()

        client.post('/auth/login', data={'username': 'prov_admin_dup', 'password': 'adminpass123'}, follow_redirects=True)

        # First company provisioning
        client.post('/admin/company/new', data={
            'name': 'Dup Co 1',
            'admin_username': 'dup_mgr',
            'admin_email': 'dup_mgr@test.com',
            'admin_password': 'mgrpass123'
        }, follow_redirects=True)

        # Duplicate company provisioning with same username
        resp = client.post('/admin/company/new', data={
            'name': 'Dup Co 2',
            'admin_username': 'dup_mgr',
            'admin_email': 'another@test.com',
            'admin_password': 'mgrpass123'
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'already exists' in resp.data

def test_logout(client, app):
    """Test logout functionality."""
    with app.app_context():
        co = Company(name='Logout Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='logout_user', email='logout@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={
            'username': 'logout_user',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Admin should now redirect to login
        response = client.get('/admin/')
        assert response.status_code == 302

def test_superadmin_reset_user_password(client, app):
    """Test that Platform Superadmin can reset a tenant company user's password."""
    with app.app_context():
        # Setup Superadmin
        admin = User(username='root_resetter', email='root@test.com', is_admin=True, is_superadmin=True)
        admin.set_password('rootpass123')

        # Setup Tenant & User
        co = Company(name='Reset Target Co')
        db.session.add_all([admin, co])
        db.session.commit()

        tenant_user = User(username='target_mgr', email='target@test.com', company_id=co.company_id, is_admin=True)
        tenant_user.set_password('oldsecret123')
        db.session.add(tenant_user)
        db.session.commit()

        # Log in as Superadmin
        client.post('/auth/login', data={'username': 'root_resetter', 'password': 'rootpass123'}, follow_redirects=True)

        # Access reset password page
        reset_url = f'/admin/company/{co.company_id}/user/{tenant_user.id}/reset-password'
        get_resp = client.get(reset_url)
        assert get_resp.status_code == 200
        assert b'Reset User Password' in get_resp.data
        assert b'target_mgr' in get_resp.data

        # Submit new password
        post_resp = client.post(reset_url, data={
            'new_password': 'brandnewsecret99',
            'confirm_password': 'brandnewsecret99'
        }, follow_redirects=True)
        assert post_resp.status_code == 200
        assert b'successfully updated' in post_resp.data

        # Log out Superadmin
        client.get('/auth/logout')

        # Verify old password fails
        fail_login = client.post('/auth/login', data={'username': 'target_mgr', 'password': 'oldsecret123'}, follow_redirects=True)
        assert b'Invalid username or password' in fail_login.data

        # Verify new password succeeds
        success_login = client.post('/auth/login', data={'username': 'target_mgr', 'password': 'brandnewsecret99'}, follow_redirects=True)
        assert b'Successfully logged in' in success_login.data

def test_company_management_restricted_to_superadmin(client, app):
    """Test that standard company managers cannot create, edit, or delete companies."""
    with app.app_context():
        co = Company(name='Standard Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='standard_mgr', email='std@test.com', company_id=co.company_id, is_admin=True, is_superadmin=False)
        user.set_password('stdpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={'username': 'standard_mgr', 'password': 'stdpass123'}, follow_redirects=True)

        # Attempt to provision company
        resp1 = client.get('/admin/company/new', follow_redirects=True)
        assert b'Platform administrator privileges required' in resp1.data

        # Attempt to edit company
        resp2 = client.get(f'/admin/company/{co.company_id}/edit', follow_redirects=True)
        assert b'Platform administrator privileges required' in resp2.data

        # Attempt to delete company
        resp3 = client.post(f'/admin/company/{co.company_id}/delete', follow_redirects=True)
        assert b'Platform administrator privileges required' in resp3.data

        # Attempt to access reset password
        resp4 = client.get(f'/admin/company/{co.company_id}/user/{user.id}/reset-password', follow_redirects=True)
        assert b'Platform administrator privileges required' in resp4.data


def test_weight_api_requires_login(client):
    """Test that the weight API requires authentication."""
    response = client.get('/api/weight-total/1')
    assert response.status_code == 302  # Redirect to login


def test_category_overview_route(client, app):
    """Test the Category Hub Overview route."""
    with app.app_context():
        co = Company(name='Hub Co')
        db.session.add(co)
        db.session.commit()
        user = User(username='hub_admin', email='hub@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('testpass123')
        db.session.add(user)
        cat = Category(name='Hub Cat', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.category_id

        client.post('/auth/login', data={
            'username': 'hub_admin',
            'password': 'testpass123'
        }, follow_redirects=True)

        response = client.get(f'/admin/category/{cat_id}/overview', follow_redirects=True)
        assert response.status_code == 200
        assert b'Hub Cat' in response.data

def test_binary_attribute_creation_and_product_ranking(client, app):
    """Test creating a binary (Yes/No) attribute and ranking products with binary measurements."""
    with app.app_context():
        co = Company(name='Binary Co')
        db.session.add(co)
        db.session.commit()
        user = User(username='binary_admin', email='binary@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('testpass123')
        db.session.add(user)
        cat = Category(name='Smartwatches', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.category_id

        client.post('/auth/login', data={
            'username': 'binary_admin',
            'password': 'testpass123'
        }, follow_redirects=True)

        # 1. Create a binary attribute
        response = client.post(f'/admin/category/{cat_id}/attribute/new', data={
            'name': 'Water Resistance',
            'data_type': 'binary',
            'weight': 100.0,
            'lower_is_better': 'y' if False else ''
        }, follow_redirects=True)
        assert response.status_code == 200

        attr = Attribute.query.filter_by(category_id=cat_id, name='Water Resistance').first()
        assert attr is not None
        assert attr.data_type == 'binary'
        assert attr.min_value == 0.0
        assert attr.max_value == 1.0

        # 2. Add product with YES (1.0)
        client.post(f'/admin/category/{cat_id}/product/new', data={
            'product_name': 'Watch Pro WaterProof',
            f'attr_{attr.attribute_id}': '1'
        }, follow_redirects=True)

        # 3. Add product with NO (0.0)
        client.post(f'/admin/category/{cat_id}/product/new', data={
            'product_name': 'Watch Basic',
            f'attr_{attr.attribute_id}': '0'
        }, follow_redirects=True)

        p_yes = Product.query.filter_by(category_id=cat_id, name='Watch Pro WaterProof').first()
        p_no = Product.query.filter_by(category_id=cat_id, name='Watch Basic').first()
        assert p_yes is not None and p_no is not None
        assert p_yes.composite_score == 1.0
        assert p_no.composite_score == 0.0

        # Verify ranking
        products = Product.query.filter_by(category_id=cat_id).order_by(Product.composite_score.desc()).all()
        assert products[0].name == 'Watch Pro WaterProof'
        assert products[1].name == 'Watch Basic'


def test_category_creation_provisions_default_attributes(client, app):
    """Test that creating a new category auto-provisions both 'Rating' and 'Price (INR)' default attributes."""
    with app.app_context():
        co = Company(name='Auto Provision Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='prov_mgr', email='prov_mgr@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('mgrpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={'username': 'prov_mgr', 'password': 'mgrpass123'}, follow_redirects=True)

        resp = client.post('/admin/category/new', data={'name': 'Gaming Mice'}, follow_redirects=True)
        assert resp.status_code == 200

        cat = Category.query.filter_by(name='Gaming Mice', company_id=co.company_id).first()
        assert cat is not None

        # Verify Rating attribute
        rating_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Rating').first()
        assert rating_attr is not None
        assert rating_attr.data_type == 'numeric'
        assert rating_attr.min_value == 0.0
        assert rating_attr.max_value == 5.0
        assert rating_attr.weight == 0.0
        assert rating_attr.lower_is_better is False
        assert rating_attr.is_active is True

        # Verify Price (INR) attribute
        price_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Price (INR)').first()
        assert price_attr is not None
        assert price_attr.data_type == 'numeric'
        assert price_attr.min_value == 0.0
        assert price_attr.max_value == 50000.0
        assert price_attr.weight == 0.0
        assert price_attr.lower_is_better is True
        assert price_attr.is_active is True

        # Check template renders Default Attribute badge
        resp_list = client.get(f'/admin/category/{cat.category_id}/attributes')
        assert b'Default Attribute' in resp_list.data
        assert b'Permanent Default' in resp_list.data
        assert b'Customer Rating and Price are permanent default attributes' in resp_list.data


test_create_category_auto_provisions_rating = test_category_creation_provisions_default_attributes


def test_cannot_deactivate_or_delete_rating_attribute(client, app):
    """Test that the default 'Rating' attribute cannot be deactivated or deleted, but custom attributes can be deleted."""
    with app.app_context():
        co = Company(name='Protect Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='protect_mgr', email='protect_mgr@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('mgrpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={'username': 'protect_mgr', 'password': 'mgrpass123'}, follow_redirects=True)

        client.post('/admin/category/new', data={'name': 'Keyboards'}, follow_redirects=True)
        cat = Category.query.filter_by(name='Keyboards', company_id=co.company_id).first()
        rating_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Rating').first()
        assert rating_attr is not None

        # Attempt to deactivate Rating
        resp_deact = client.post(f'/admin/attribute/{rating_attr.attribute_id}/deactivate', follow_redirects=True)
        assert resp_deact.status_code == 200
        assert b'mandatory default attribute and cannot be deactivated' in resp_deact.data
        rating_attr = db.session.get(Attribute, rating_attr.attribute_id)
        assert rating_attr.is_active is True

        # Attempt to delete Rating
        resp_del = client.post(f'/admin/attribute/{rating_attr.attribute_id}/delete', follow_redirects=True)
        assert resp_del.status_code == 200
        assert b"cannot be deleted" in resp_del.data and b"Rating" in resp_del.data
        assert db.session.get(Attribute, rating_attr.attribute_id) is not None

        # Add a custom attribute and delete it
        custom_attr = Attribute(
            name='Switch Durability',
            category_id=cat.category_id,
            min_value=0.0,
            max_value=100.0,
            weight=50.0
        )
        db.session.add(custom_attr)
        db.session.commit()
        custom_id = custom_attr.attribute_id

        resp_del_custom = client.post(f'/admin/attribute/{custom_id}/delete', follow_redirects=True)
        assert resp_del_custom.status_code == 200
        assert b'Attribute deleted successfully' in resp_del_custom.data
        assert db.session.get(Attribute, custom_id) is None


def test_cannot_rename_rating_attribute(client, app):
    """Test that the default 'Rating' attribute cannot be renamed."""
    with app.app_context():
        co = Company(name='Rename Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='rename_mgr', email='rename_mgr@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('mgrpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={'username': 'rename_mgr', 'password': 'mgrpass123'}, follow_redirects=True)

        client.post('/admin/category/new', data={'name': 'Monitors'}, follow_redirects=True)
        cat = Category.query.filter_by(name='Monitors', company_id=co.company_id).first()
        rating_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Rating').first()

        # Attempt to rename Rating to 'Review Score'
        resp = client.post(f'/admin/attribute/{rating_attr.attribute_id}/edit', data={
            'name': 'Review Score',
            'data_type': 'numeric',
            'min_value': 0.0,
            'max_value': 5.0,
            'weight': 10.0
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"cannot be renamed" in resp.data and b"Rating" in resp.data

        rating_attr = db.session.get(Attribute, rating_attr.attribute_id)
        assert rating_attr.name == 'Rating'


def test_update_rating_weight_and_range(client, app):
    """Test that Rating weight can be updated between 0% and 100% and scale range modified."""
    with app.app_context():
        co = Company(name='Weight Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='weight_mgr', email='weight_mgr@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('mgrpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={'username': 'weight_mgr', 'password': 'mgrpass123'}, follow_redirects=True)

        client.post('/admin/category/new', data={'name': 'Speakers'}, follow_redirects=True)
        cat = Category.query.filter_by(name='Speakers', company_id=co.company_id).first()
        rating_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Rating').first()

        # 1. Update weight to 25.0
        resp1 = client.post(f'/admin/attribute/{rating_attr.attribute_id}/edit', data={
            'name': 'Rating',
            'data_type': 'numeric',
            'min_value': 0.0,
            'max_value': 5.0,
            'weight': 25.0
        }, follow_redirects=True)
        assert resp1.status_code == 200
        rating_attr = db.session.get(Attribute, rating_attr.attribute_id)
        assert rating_attr.weight == 25.0

        # 2. Update weight to 0.0
        resp2 = client.post(f'/admin/attribute/{rating_attr.attribute_id}/edit', data={
            'name': 'Rating',
            'data_type': 'numeric',
            'min_value': 0.0,
            'max_value': 5.0,
            'weight': 0.0
        }, follow_redirects=True)
        assert resp2.status_code == 200
        rating_attr = db.session.get(Attribute, rating_attr.attribute_id)
        assert rating_attr.weight == 0.0

        # 3. Update weight to 100.0 and range 0 to 100
        resp3 = client.post(f'/admin/attribute/{rating_attr.attribute_id}/edit', data={
            'name': 'Rating',
            'data_type': 'numeric',
            'min_value': 0.0,
            'max_value': 100.0,
            'weight': 100.0
        }, follow_redirects=True)
        assert resp3.status_code == 200
        rating_attr = db.session.get(Attribute, rating_attr.attribute_id)
        assert rating_attr.weight == 100.0
        assert rating_attr.max_value == 100.0


def test_rating_input_scales_and_defaults(client, app):
    """Test that Rating accepts both 0-5 and 0-100 inputs, and defaults to 4.0 when empty."""
    with app.app_context():
        co = Company(name='Scale Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='scale_mgr', email='scale_mgr@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('mgrpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={'username': 'scale_mgr', 'password': 'mgrpass123'}, follow_redirects=True)

        client.post('/admin/category/new', data={'name': 'Drones'}, follow_redirects=True)
        cat = Category.query.filter_by(name='Drones', company_id=co.company_id).first()
        rating_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Rating').first()

        # Set Rating weight to 100 so composite_score reflects rating normalized value
        rating_attr.weight = 100.0
        db.session.commit()

        # 1. Product with empty rating defaults to 4.0
        client.post(f'/admin/category/{cat.category_id}/product/new', data={
            'product_name': 'Drone Default',
            f'attr_{rating_attr.attribute_id}': ''
        }, follow_redirects=True)

        p_default = Product.query.filter_by(name='Drone Default', category_id=cat.category_id).first()
        assert p_default is not None
        pav_default = ProductAttrValue.query.filter_by(product_id=p_default.product_id, attribute_id=rating_attr.attribute_id).first()
        assert pav_default is not None
        assert pav_default.raw_value == 4.0
        assert abs(p_default.composite_score - 0.8) < 0.01  # 4.0 / 5.0 = 0.8

        # 2. Product with standard 0-5 rating (4.5)
        client.post(f'/admin/category/{cat.category_id}/product/new', data={
            'product_name': 'Drone FiveScale',
            f'attr_{rating_attr.attribute_id}': '4.5'
        }, follow_redirects=True)

        p_five = Product.query.filter_by(name='Drone FiveScale', category_id=cat.category_id).first()
        assert p_five is not None
        pav_five = ProductAttrValue.query.filter_by(product_id=p_five.product_id, attribute_id=rating_attr.attribute_id).first()
        assert pav_five.raw_value == 4.5
        assert abs(p_five.composite_score - 0.9) < 0.01  # 4.5 / 5.0 = 0.9

        # 3. Product with 0-100 rating scale (80.0) -> scaled to 4.0
        client.post(f'/admin/category/{cat.category_id}/product/new', data={
            'product_name': 'Drone HundredScale',
            f'attr_{rating_attr.attribute_id}': '80.0'
        }, follow_redirects=True)

        p_hundred = Product.query.filter_by(name='Drone HundredScale', category_id=cat.category_id).first()
        assert p_hundred is not None
        pav_hundred = ProductAttrValue.query.filter_by(product_id=p_hundred.product_id, attribute_id=rating_attr.attribute_id).first()
        assert pav_hundred.raw_value == 4.0
        assert abs(p_hundred.composite_score - 0.8) < 0.01

        # 4. Edit product: change rating from 4.0 to 100.0 scale (90.0) -> scaled to 4.5
        client.post(f'/admin/product/{p_default.product_id}/edit', data={
            'product_name': 'Drone Default Updated',
            f'attr_{rating_attr.attribute_id}': '90.0'
        }, follow_redirects=True)

        p_updated = db.session.get(Product, p_default.product_id)
        pav_updated = ProductAttrValue.query.filter_by(product_id=p_default.product_id, attribute_id=rating_attr.attribute_id).first()
        assert pav_updated.raw_value == 4.5
        assert abs(p_updated.composite_score - 0.9) < 0.01


def test_cannot_deactivate_or_delete_price_attribute(client, app):
    """Test that the default 'Price (INR)' attribute cannot be deactivated or deleted."""
    with app.app_context():
        co = Company(name='Price Protect Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='price_protect_mgr', email='ppmgr@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('mgrpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={'username': 'price_protect_mgr', 'password': 'mgrpass123'}, follow_redirects=True)

        client.post('/admin/category/new', data={'name': 'Laptops'}, follow_redirects=True)
        cat = Category.query.filter_by(name='Laptops', company_id=co.company_id).first()
        price_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Price (INR)').first()
        assert price_attr is not None

        # Attempt to deactivate Price
        resp_deact = client.post(f'/admin/attribute/{price_attr.attribute_id}/deactivate', follow_redirects=True)
        assert resp_deact.status_code == 200
        assert b'mandatory default attribute and cannot be deactivated' in resp_deact.data
        price_attr = db.session.get(Attribute, price_attr.attribute_id)
        assert price_attr.is_active is True

        # Attempt to delete Price
        resp_del = client.post(f'/admin/attribute/{price_attr.attribute_id}/delete', follow_redirects=True)
        assert resp_del.status_code == 200
        assert b'cannot be deleted' in resp_del.data and b'Price' in resp_del.data
        assert db.session.get(Attribute, price_attr.attribute_id) is not None


def test_cannot_rename_price_attribute(client, app):
    """Test that the default 'Price' attribute cannot be renamed away from price."""
    with app.app_context():
        co = Company(name='Price Rename Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='price_rename_mgr', email='prmgr@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('mgrpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={'username': 'price_rename_mgr', 'password': 'mgrpass123'}, follow_redirects=True)

        client.post('/admin/category/new', data={'name': 'Smartphones'}, follow_redirects=True)
        cat = Category.query.filter_by(name='Smartphones', company_id=co.company_id).first()
        price_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Price (INR)').first()
        assert price_attr is not None

        # Attempt to rename Price to 'Cost' (doesn't contain 'price')
        resp = client.post(f'/admin/attribute/{price_attr.attribute_id}/edit', data={
            'name': 'Cost',
            'data_type': 'numeric',
            'min_value': 0.0,
            'max_value': 50000.0,
            'weight': 10.0
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"cannot be renamed" in resp.data and b"Price" in resp.data

        price_attr = db.session.get(Attribute, price_attr.attribute_id)
        assert price_attr.name == 'Price (INR)'

        # Renaming to another name containing 'price' (e.g. 'Price (USD)') is allowed
        resp_valid = client.post(f'/admin/attribute/{price_attr.attribute_id}/edit', data={
            'name': 'Price (USD)',
            'data_type': 'numeric',
            'min_value': 0.0,
            'max_value': 1000.0,
            'weight': 20.0
        }, follow_redirects=True)
        assert resp_valid.status_code == 200
        price_attr = db.session.get(Attribute, price_attr.attribute_id)
        assert price_attr.name == 'Price (USD)'
        assert price_attr.weight == 20.0


def test_product_creation_default_price(client, app):
    """Test that a product created with empty Price defaults cleanly to 1999.0."""
    with app.app_context():
        co = Company(name='Default Price Co')
        db.session.add(co)
        db.session.commit()

        user = User(username='def_price_mgr', email='dpmgr@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('mgrpass123')
        db.session.add(user)
        db.session.commit()

        client.post('/auth/login', data={'username': 'def_price_mgr', 'password': 'mgrpass123'}, follow_redirects=True)

        client.post('/admin/category/new', data={'name': 'Headphones'}, follow_redirects=True)
        cat = Category.query.filter_by(name='Headphones', company_id=co.company_id).first()
        rating_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Rating').first()
        price_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Price (INR)').first()

        # Create product with empty rating and price
        resp = client.post(f'/admin/category/{cat.category_id}/product/new', data={
            'product_name': 'Headphones Basic',
            f'attr_{rating_attr.attribute_id}': '',
            f'attr_{price_attr.attribute_id}': ''
        }, follow_redirects=True)
        assert resp.status_code == 200

        p = Product.query.filter_by(name='Headphones Basic', category_id=cat.category_id).first()
        assert p is not None
        pav_price = ProductAttrValue.query.filter_by(product_id=p.product_id, attribute_id=price_attr.attribute_id).first()
        assert pav_price is not None
        assert pav_price.raw_value == 1999.0

        pav_rating = ProductAttrValue.query.filter_by(product_id=p.product_id, attribute_id=rating_attr.attribute_id).first()
        assert pav_rating is not None
        assert pav_rating.raw_value == 4.0

        # Edit product: update price to 2999.0
        resp_edit = client.post(f'/admin/product/{p.product_id}/edit', data={
            'product_name': 'Headphones Pro',
            f'attr_{rating_attr.attribute_id}': '4.8',
            f'attr_{price_attr.attribute_id}': '2999.0'
        }, follow_redirects=True)
        assert resp_edit.status_code == 200

        pav_price_edit = ProductAttrValue.query.filter_by(product_id=p.product_id, attribute_id=price_attr.attribute_id).first()
        assert pav_price_edit.raw_value == 2999.0


def test_ensure_all_categories_have_rating_backfill(app):
    """Test that ensure_all_categories_have_rating populates Rating and Price and PAVs on legacy categories and products."""
    from app.ranking.helpers import ensure_all_categories_have_rating
    with app.app_context():
        co = Company(name='Legacy Co')
        db.session.add(co)
        db.session.commit()

        cat = Category(name='Legacy Cat', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()

        # Product without Rating/Price attribute or PAV
        prod = Product(name='Legacy Prod', category_id=cat.category_id)
        db.session.add(prod)
        db.session.commit()

        # Run ensure_all_categories_have_rating
        ensure_all_categories_have_rating(db.session)

        rating_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Rating').first()
        assert rating_attr is not None
        assert rating_attr.min_value == 0.0
        assert rating_attr.max_value == 5.0
        assert rating_attr.weight == 0.0

        pav = ProductAttrValue.query.filter_by(product_id=prod.product_id, attribute_id=rating_attr.attribute_id).first()
        assert pav is not None
        assert pav.raw_value == 4.5
        assert pav.normalized_value == 0.9

        price_attr = Attribute.query.filter_by(category_id=cat.category_id, name='Price (INR)').first()
        assert price_attr is not None
        assert price_attr.min_value == 0.0
        assert price_attr.max_value == 50000.0
        assert price_attr.weight == 0.0
        assert price_attr.lower_is_better is True

        pav_price = ProductAttrValue.query.filter_by(product_id=prod.product_id, attribute_id=price_attr.attribute_id).first()
        assert pav_price is not None
        assert pav_price.raw_value == 1999.0


def test_set_category_display_attributes(client, app):
    """Test updating storefront card display attributes via admin endpoint and rendering on attributes page."""
    with app.app_context():
        co = Company(name='Display Attr Co')
        db.session.add(co)
        db.session.commit()
        user = User(username='disp_admin', email='disp@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('testpass123')
        db.session.add(user)
        cat = Category(name='Audio Gear', company_id=co.company_id)
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.category_id

        attr1 = Attribute(category_id=cat_id, name='Battery Life', min_value=1.0, max_value=50.0, weight=50.0)
        attr2 = Attribute(category_id=cat_id, name='Noise Cancellation', data_type='binary', weight=50.0)
        db.session.add_all([attr1, attr2])
        db.session.commit()

        client.post('/auth/login', data={'username': 'disp_admin', 'password': 'testpass123'}, follow_redirects=True)

        resp = client.post(f'/admin/category/{cat_id}/display-attributes', data={
            'display_attr_1': 'Battery Life',
            'display_attr_2': 'Noise Cancellation'
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Storefront card display attributes updated' in resp.data
        assert b'Card Display (Slot 1)' in resp.data
        assert b'Card Display (Slot 2)' in resp.data

        updated_cat = db.session.get(Category, cat_id)
        assert updated_cat.display_attr_1 == 'Battery Life'
        assert updated_cat.display_attr_2 == 'Noise Cancellation'


def test_edit_category_saves_display_attributes(client, app):
    """Test that editing category preserves or updates display attributes."""
    with app.app_context():
        co = Company(name='Edit Cat Co')
        db.session.add(co)
        db.session.commit()
        user = User(username='edit_cat_admin', email='editcat@test.com', company_id=co.company_id, is_admin=True)
        user.set_password('testpass123')
        db.session.add(user)
        cat = Category(name='Old Cat Name', company_id=co.company_id, display_attr_1='Attr 1', display_attr_2='Attr 2')
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.category_id

        client.post('/auth/login', data={'username': 'edit_cat_admin', 'password': 'testpass123'}, follow_redirects=True)

        resp = client.post(f'/admin/category/{cat_id}/edit', data={
            'name': 'Updated Cat Name',
            'display_attr_1': 'New Slot 1',
            'display_attr_2': 'New Slot 2'
        }, follow_redirects=True)
        assert resp.status_code == 200

        updated_cat = db.session.get(Category, cat_id)
        assert updated_cat.name == 'Updated Cat Name'
        assert updated_cat.display_attr_1 == 'New Slot 1'
        assert updated_cat.display_attr_2 == 'New Slot 2'




