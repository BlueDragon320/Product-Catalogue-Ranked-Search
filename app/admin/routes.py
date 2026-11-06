from functools import wraps
from flask import render_template, redirect, url_for, flash, request, session, g
from flask_login import login_required, current_user
from app import db
from app.models import Company, Category, Attribute, Product, ProductAttrValue, SponsoredPlacement, User, SearchLog
from app.admin import admin
from app.admin.forms import CompanyForm, CompanyAccountForm, CategoryForm, AttributeForm, SponsorForm, UserPasswordResetForm

from app.ranking.helpers import get_category_stats, get_sponsor_status, format_score_display, ensure_default_category_attributes, is_default_attribute

@admin.before_request
@login_required
def admin_before_request():
    if current_user.is_authenticated:
        g.is_superadmin = bool(getattr(current_user, 'is_superadmin', False) or (getattr(current_user, 'is_admin', False) and getattr(current_user, 'company_id', None) is None))
        inspect_id = session.get('inspect_company_id')
        if g.is_superadmin and inspect_id:
            g.company_id = inspect_id
            g.inspecting = True
            g.inspect_company = db.session.get(Company, inspect_id)
        else:
            g.company_id = getattr(current_user, 'company_id', None)
            g.inspecting = False
            g.inspect_company = None

def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.company_id:
            if getattr(g, 'is_superadmin', False):
                flash("Please select a company to inspect and view its data.", "info")
                return redirect(url_for('admin.index'))
            flash("You must be assigned to a company.", "danger")
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'is_superadmin', False):
            flash("Platform administrator privileges required.", "danger")
            return redirect(url_for('admin.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
def index():
    # 1. Super Admin Platform Dashboard (when not in tenant inspection mode)
    if g.is_superadmin and not g.inspecting:
        companies = Company.query.order_by(Company.created_at.desc()).all()
        company_data = []
        total_platform_categories = 0
        total_platform_products = 0
        total_platform_sponsors = 0

        for comp in companies:
            cat_count = comp.categories.count()
            prod_count = Product.query.join(Category).filter(Category.company_id == comp.company_id).count()
            user_count = comp.users.count()
            sponsors_count = SponsoredPlacement.query.join(Product).join(Category).filter(Category.company_id == comp.company_id).count()
            
            total_platform_categories += cat_count
            total_platform_products += prod_count
            total_platform_sponsors += sponsors_count

            company_data.append({
                'company': comp,
                'category_count': cat_count,
                'product_count': prod_count,
                'user_count': user_count,
                'sponsor_count': sponsors_count,
                'users': comp.users.all()
            })

        return render_template(
            'admin/platform_dashboard.html',
            companies=company_data,
            total_companies=len(companies),
            total_categories=total_platform_categories,
            total_products=total_platform_products,
            total_sponsors=total_platform_sponsors
        )

    # 2. Company Operations Dashboard (for Tenant user or Superadmin Inspecting Tenant)
    if not g.company_id:
        flash("No active company found for this account.", "warning")
        return redirect('/')

    company = db.get_or_404(Company, g.company_id)
    categories = Category.query.filter_by(company_id=g.company_id).all()
    category_summaries = []
    total_products = 0
    total_attributes = 0
    active_sponsors_count = 0
    for cat in categories:
        stats = get_category_stats(cat.category_id)
        total_products += stats.get('product_count', 0)
        total_attributes += stats.get('attribute_count', 0)
        active_sponsors_count += stats.get('active_sponsor_count', 0)
        category_summaries.append({'category': cat, 'stats': stats})

    return render_template(
        'admin/index.html',
        company=company,
        categories=categories,
        category_summaries=category_summaries,
        total_categories=len(categories),
        total_products=total_products,
        total_attributes=total_attributes,
        active_sponsors_count=active_sponsors_count,
        inspecting=g.inspecting,
        inspect_company=g.inspect_company
    )

@admin.route('/companies')
@login_required
@superadmin_required
def list_companies():
    companies = Company.query.order_by(Company.created_at.desc()).all()
    return render_template('admin/company_list.html', companies=companies, is_superadmin=True)

@admin.route('/company/new', methods=['GET', 'POST'])
@login_required
@superadmin_required
def new_company():
    """
    Provision a new isolated tenant company along with its primary manager account.
    Restricted exclusively to Platform Superadmin.
    """
    form = CompanyAccountForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == form.admin_username.data) | (User.email == form.admin_email.data)
        ).first()
        if existing_user:
            flash(f"User with username '{form.admin_username.data}' or email already exists.", "danger")
            return render_template('admin/company_form.html', form=form, title="Provision New Company", is_superadmin=True)

        company = Company(name=form.name.data)
        db.session.add(company)
        db.session.flush()

        user = User(
            username=form.admin_username.data,
            email=form.admin_email.data,
            company_id=company.company_id,
            is_admin=True,
            is_superadmin=False
        )
        user.set_password(form.admin_password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"Company '{company.name}' and manager account '{user.username}' created successfully.", 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/company_form.html', form=form, title="Provision New Company", is_superadmin=True)

@admin.route('/company/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit_company(company_id):
    """
    Edit company details. Restricted exclusively to Platform Superadmin.
    """
    company = db.get_or_404(Company, company_id)
    form = CompanyForm(obj=company)
    users = company.users.all()
    if form.validate_on_submit():
        company.name = form.name.data
        db.session.commit()
        flash('Company updated successfully.', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/company_form.html', form=form, title=f"Edit {company.name}", is_superadmin=True, company=company, users=users)

@admin.route('/company/<int:company_id>/user/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
@superadmin_required
def reset_user_password(company_id, user_id):
    """
    Reset password for a company's manager/user account.
    Restricted exclusively to Platform Superadmin.
    """
    company = db.get_or_404(Company, company_id)
    target_user = User.query.filter_by(id=user_id, company_id=company_id).first_or_404()
    form = UserPasswordResetForm()
    if form.validate_on_submit():
        target_user.set_password(form.new_password.data)
        db.session.commit()
        flash(f"Password for user '{target_user.username}' (Company: {company.name}) successfully updated.", 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/user_password_reset.html', form=form, company=company, target_user=target_user)


@admin.route('/company/<int:company_id>/delete', methods=['POST'])
@login_required
@superadmin_required
def delete_company(company_id):
    company = db.get_or_404(Company, company_id)
    company_name = company.name

    # Cascade delete all child entities
    categories = Category.query.filter_by(company_id=company_id).all()
    cat_ids = [cat.category_id for cat in categories]
    if cat_ids:
        SearchLog.query.filter(SearchLog.category_id.in_(cat_ids)).update({SearchLog.category_id: None}, synchronize_session=False)

    for cat in categories:
        # Delete sponsored placements
        products = Product.query.filter_by(category_id=cat.category_id).all()
        for prod in products:
            SponsoredPlacement.query.filter_by(product_id=prod.product_id).delete()
            ProductAttrValue.query.filter_by(product_id=prod.product_id).delete()
            db.session.delete(prod)
        
        # Delete attributes
        Attribute.query.filter_by(category_id=cat.category_id).delete()
        db.session.delete(cat)

    # Delete users
    User.query.filter_by(company_id=company_id).delete()
    
    # Delete company
    db.session.delete(company)
    db.session.commit()

    if session.get('inspect_company_id') == company_id:
        session.pop('inspect_company_id', None)

    flash(f"Company '{company_name}' and all associated categories, products, and users deleted.", 'success')
    return redirect(url_for('admin.index'))

@admin.route('/company/<int:company_id>/inspect')
@login_required
@superadmin_required
def inspect_company(company_id):
    company = db.get_or_404(Company, company_id)
    session['inspect_company_id'] = company_id
    flash(f"Switched context: Now inspecting company '{company.name}'.", "info")
    return redirect(url_for('admin.index'))

@admin.route('/company/exit-inspect')
@login_required
@superadmin_required
def exit_inspect():
    session.pop('inspect_company_id', None)
    flash("Exited tenant inspection mode. Returned to Platform Admin Console.", "info")
    return redirect(url_for('admin.index'))



# Category Routes

@admin.route('/categories')
@company_required
def list_categories():
    """List all categories for the current company (FR-2)."""
    categories = Category.query.filter_by(company_id=g.company_id).all()
    category_cards = [{'category': c, 'stats': get_category_stats(c.category_id)} for c in categories]
    return render_template('admin/category_list.html', categories=categories, category_cards=category_cards)

@admin.route('/category/<int:category_id>/overview')
@company_required
def category_overview(category_id):
    """Category Hub Overview — unified command center for managing a category."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    stats = get_category_stats(category_id)
    top_products = Product.query.filter_by(category_id=category_id).order_by(Product.composite_score.desc()).limit(5).all()
    attributes = Attribute.query.filter_by(category_id=category_id).all()
    from datetime import date
    today = date.today()
    sponsors = SponsoredPlacement.query.join(Product).filter(
        Product.category_id == category_id,
        SponsoredPlacement.start_date <= today,
        SponsoredPlacement.end_date >= today,
        SponsoredPlacement.is_active == True
    ).all()
    return render_template(
        'admin/category_overview.html',
        category=category,
        stats=stats,
        top_products=top_products,
        attributes=attributes,
        sponsors=sponsors,
        format_score=format_score_display
    )

@admin.route('/category/new', methods=['GET', 'POST'])
@company_required
def new_category():
    """Create a new category for the current company (FR-2)."""
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, company_id=g.company_id)
        db.session.add(category)
        db.session.commit()
        ensure_default_category_attributes(category.category_id, db.session)
        flash('Category created successfully.', 'success')
        return redirect(url_for('admin.list_categories'))
    return render_template('admin/category_form.html', form=form, title="New Category")

@admin.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@company_required
def edit_category(category_id):
    """Edit an existing category (FR-2)."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    stats = get_category_stats(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        if 'display_attr_1' in request.form:
            category.display_attr_1 = request.form.get('display_attr_1', '').strip() or None
        if 'display_attr_2' in request.form:
            category.display_attr_2 = request.form.get('display_attr_2', '').strip() or None
        db.session.commit()
        flash('Category updated successfully.', 'success')
        return redirect(url_for('admin.list_categories'))
    return render_template('admin/category_form.html', form=form, title="Edit Category", category=category, stats=stats)

@admin.route('/category/<int:category_id>/display-attributes', methods=['POST'])
@company_required
def set_display_attributes(category_id):
    """Update storefront card display attributes for a category."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    display_attr_1 = request.form.get('display_attr_1', '').strip()
    display_attr_2 = request.form.get('display_attr_2', '').strip()
    category.display_attr_1 = display_attr_1 or None
    category.display_attr_2 = display_attr_2 or None
    db.session.commit()
    flash(f"Storefront card display attributes updated for '{category.name}'.", 'success')
    return redirect(url_for('admin.list_attributes', category_id=category_id))

@admin.route('/category/<int:category_id>/delete', methods=['POST'])
@company_required
def delete_category(category_id):
    """Delete a category and cascade-clean its child products, attributes, sponsors, and logs."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    cat_name = category.name

    # 1. Cascade delete child products, sponsored placements, and attribute measurements
    products = Product.query.filter_by(category_id=category_id).all()
    for prod in products:
        SponsoredPlacement.query.filter_by(product_id=prod.product_id).delete()
        ProductAttrValue.query.filter_by(product_id=prod.product_id).delete()
        db.session.delete(prod)
    
    # 2. Delete category attributes
    Attribute.query.filter_by(category_id=category_id).delete()

    # 3. Disassociate search logs
    from app.models import SearchLog
    SearchLog.query.filter_by(category_id=category_id).update({'category_id': None})

    # 4. Delete category
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{cat_name}" and associated catalog data deleted successfully.', 'success')
    return redirect(url_for('admin.list_categories'))



# Attribute Routes

@admin.route('/category/<int:category_id>/attributes')
@company_required
def list_attributes(category_id):
    """List all attributes for a given category (FR-4)."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    attributes = Attribute.query.filter_by(category_id=category_id).all()
    stats = get_category_stats(category_id)
    return render_template('admin/attribute_list.html', category=category, attributes=attributes, stats=stats)

@admin.route('/category/<int:category_id>/attribute/new', methods=['GET', 'POST'])
@company_required
def new_attribute(category_id):
    """Create a new attribute for a category (FR-4)."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    form = AttributeForm()
    if form.validate_on_submit():
        data_type = form.data_type.data
        if data_type == 'binary':
            min_val = 0.0
            max_val = 1.0
        else:
            min_val = form.min_value.data
            max_val = form.max_value.data
            if min_val is None or max_val is None:
                flash('Minimum and maximum values are required for numeric attributes.', 'danger')
                return render_template('admin/attribute_form.html', form=form, title="New Attribute", category=category)
            if min_val >= max_val:
                flash('Minimum value must be less than maximum value.', 'danger')
                return render_template('admin/attribute_form.html', form=form, title="New Attribute", category=category)

        attr = Attribute(
            category_id=category.category_id,
            name=form.name.data,
            data_type=data_type,
            min_value=min_val,
            max_value=max_val,
            weight=form.weight.data,
            lower_is_better=form.lower_is_better.data,
            is_active=True
        )
        db.session.add(attr)
        db.session.commit()
        flash('Attribute created successfully.', 'success')
        return redirect(url_for('admin.list_attributes', category_id=category.category_id))
    return render_template('admin/attribute_form.html', form=form, title="New Attribute", category=category)

@admin.route('/attribute/<int:attribute_id>/edit', methods=['GET', 'POST'])
@company_required
def edit_attribute(attribute_id):
    """Edit an existing attribute (FR-4)."""
    attribute = Attribute.query.join(Category).filter(
        Attribute.attribute_id == attribute_id,
        Category.company_id == g.company_id
    ).first_or_404()
    category = attribute.category
    
    form = AttributeForm(obj=attribute)
    if form.validate_on_submit():
        if attribute.name.strip().lower() == 'rating' and form.name.data.strip().lower() != 'rating':
            flash("The default 'Rating' attribute cannot be renamed.", "warning")
            return render_template('admin/attribute_form.html', form=form, title="Edit Attribute", category=category)

        if 'price' in attribute.name.strip().lower() and 'price' not in form.name.data.strip().lower():
            flash("The default 'Price' attribute cannot be renamed.", "warning")
            return render_template('admin/attribute_form.html', form=form, title="Edit Attribute", category=category)

        data_type = form.data_type.data
        if data_type == 'binary':
            min_val = 0.0
            max_val = 1.0
        else:
            min_val = form.min_value.data
            max_val = form.max_value.data
            if min_val is None or max_val is None:
                flash('Minimum and maximum values are required for numeric attributes.', 'danger')
                return render_template('admin/attribute_form.html', form=form, title="Edit Attribute", category=category)
            if min_val >= max_val:
                flash('Minimum value must be less than maximum value.', 'danger')
                return render_template('admin/attribute_form.html', form=form, title="Edit Attribute", category=category)

        attribute.name = form.name.data
        attribute.data_type = data_type
        attribute.min_value = min_val
        attribute.max_value = max_val
        attribute.weight = form.weight.data
        attribute.lower_is_better = form.lower_is_better.data
        db.session.commit()
        from app.ranking.engine import recompute_category_scores
        recompute_category_scores(attribute.category_id, db.session, Product, Attribute, ProductAttrValue)
        flash('Attribute updated successfully.', 'success')
        return redirect(url_for('admin.list_attributes', category_id=category.category_id))
    return render_template('admin/attribute_form.html', form=form, title="Edit Attribute", category=category)

@admin.route('/attribute/<int:attribute_id>/deactivate', methods=['POST'])
@company_required
def deactivate_attribute(attribute_id):
    """Deactivate or toggle an attribute and recompute composite scores (FR-4)."""
    attribute = Attribute.query.join(Category).filter(
        Attribute.attribute_id == attribute_id,
        Category.company_id == g.company_id
    ).first_or_404()
    if is_default_attribute(attribute.name) and attribute.is_active:
        flash(f"The '{attribute.name}' attribute is a mandatory default attribute and cannot be deactivated. To disable its ranking influence, set its weight to 0%.", "warning")
        return redirect(url_for('admin.list_attributes', category_id=attribute.category_id))
    attribute.is_active = not attribute.is_active
    db.session.commit()
    from app.ranking.engine import recompute_category_scores
    recompute_category_scores(attribute.category_id, db.session, Product, Attribute, ProductAttrValue)
    status_label = "activated" if attribute.is_active else "deactivated"
    flash(f'Attribute "{attribute.name}" {status_label}. Product scores recomputed.', 'info')
    return redirect(url_for('admin.list_attributes', category_id=attribute.category_id))

@admin.route('/attribute/<int:attribute_id>/delete', methods=['POST'])
@company_required
def delete_attribute(attribute_id):
    """Delete an attribute (non-Rating) and recompute composite scores."""
    attribute = Attribute.query.join(Category).filter(
        Attribute.attribute_id == attribute_id,
        Category.company_id == g.company_id
    ).first_or_404()
    category_id = attribute.category_id

    if is_default_attribute(attribute.name):
        flash(f"The default '{attribute.name}' attribute cannot be deleted. You can set its weight to 0% to remove its ranking influence.", "danger")
        return redirect(url_for('admin.list_attributes', category_id=category_id))

    ProductAttrValue.query.filter_by(attribute_id=attribute.attribute_id).delete()
    db.session.delete(attribute)
    db.session.commit()
    from app.ranking.engine import recompute_category_scores
    recompute_category_scores(category_id, db.session, Product, Attribute, ProductAttrValue)
    flash('Attribute deleted successfully.', 'success')
    return redirect(url_for('admin.list_attributes', category_id=category_id))

# Product CRUD routes
@admin.route('/category/<int:category_id>/products')
@company_required
def list_products(category_id):
    """List all products in a category. FR-7."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    products = Product.query.filter_by(category_id=category_id).order_by(Product.composite_score.desc()).all()
    stats = get_category_stats(category_id)
    attributes = Attribute.query.filter_by(category_id=category_id, is_active=True).all()
    product_attrs = {}
    for p in products:
        pavs = ProductAttrValue.query.filter_by(product_id=p.product_id).all()
        product_attrs[p.product_id] = {pav.attribute_id: pav.raw_value for pav in pavs}
    return render_template(
        'admin/product_list.html',
        category=category,
        products=products,
        attributes=attributes,
        product_attrs=product_attrs,
        stats=stats,
        format_score=format_score_display
    )

@admin.route('/category/<int:category_id>/product/new', methods=['GET', 'POST'])
@company_required
def new_product(category_id):
    """Add a new product to a category. FR-5, FR-6."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    attributes = Attribute.query.filter_by(category_id=category_id, is_active=True).all()
    
    if request.method == 'POST':
        name = request.form.get('product_name')
        if not name:
            flash('Product name is required.', 'danger')
            return render_template('admin/product_form.html', category=category, attributes=attributes)
        
        product = Product(name=name, category_id=category_id)
        db.session.add(product)
        db.session.flush()  # Get product_id before adding values
        
        # Save attribute values
        for attr in attributes:
            raw_value = request.form.get(f'attr_{attr.attribute_id}')
            is_rating = (attr.name.strip().lower() == 'rating')
            is_price = ('price' in attr.name.strip().lower())

            if is_rating and (raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == '')):
                raw_val = 4.0 if (attr.min_value is not None and attr.max_value is not None and attr.min_value <= 4.0 <= attr.max_value) else (attr.min_value if attr.min_value is not None else 4.0)
                pav = ProductAttrValue(
                    product_id=product.product_id,
                    attribute_id=attr.attribute_id,
                    raw_value=raw_val
                )
                db.session.add(pav)
                continue

            if is_price and (raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == '')):
                raw_val = 1999.0 if (attr.min_value is None or attr.min_value <= 1999.0) else attr.min_value
                pav = ProductAttrValue(
                    product_id=product.product_id,
                    attribute_id=attr.attribute_id,
                    raw_value=raw_val
                )
                db.session.add(pav)
                continue

            if raw_value is not None and (not isinstance(raw_value, str) or raw_value.strip() != ''):
                try:
                    raw_val = float(raw_value)
                except ValueError:
                    flash(f'{attr.name} must be a valid number.', 'danger')
                    db.session.rollback()
                    return render_template('admin/product_form.html', category=category, attributes=attributes)

                if is_rating and raw_val > 5.0 and raw_val <= 100.0 and attr.max_value is not None and attr.max_value <= 5.0:
                    raw_val = round((raw_val / 100.0) * attr.max_value, 2)

                # FR-6: Validate value is within range
                if raw_val < attr.min_value or raw_val > attr.max_value:
                    flash(f'{attr.name} must be between {attr.min_value} and {attr.max_value}.', 'danger')
                    db.session.rollback()
                    return render_template('admin/product_form.html', category=category, attributes=attributes)
                
                pav = ProductAttrValue(
                    product_id=product.product_id,
                    attribute_id=attr.attribute_id,
                    raw_value=raw_val
                )
                db.session.add(pav)
        
        db.session.commit()
        
        # Trigger recomputation (FR-11)
        try:
            from app.ranking.engine import recompute_category_scores
            recompute_category_scores(category_id, db.session, Product, Attribute, ProductAttrValue)
        except ImportError:
            pass  # Ranking engine not yet available
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.list_products', category_id=category_id))
    
    return render_template('admin/product_form.html', category=category, attributes=attributes)

@admin.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@company_required
def edit_product(product_id):
    """Edit an existing product. FR-7, FR-8."""
    product = db.get_or_404(Product, product_id)
    category = Category.query.filter_by(category_id=product.category_id, company_id=g.company_id).first_or_404()
    attributes = Attribute.query.filter_by(category_id=category.category_id, is_active=True).all()
    
    # Get existing values
    existing_values = {}
    for pav in ProductAttrValue.query.filter_by(product_id=product_id).all():
        existing_values[pav.attribute_id] = pav.raw_value
    
    if request.method == 'POST':
        product.name = request.form.get('product_name', product.name)
        
        for attr in attributes:
            raw_value = request.form.get(f'attr_{attr.attribute_id}')
            is_rating = (attr.name.strip().lower() == 'rating')
            is_price = ('price' in attr.name.strip().lower())

            if is_rating and (raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == '')):
                raw_val = 4.0 if (attr.min_value is not None and attr.max_value is not None and attr.min_value <= 4.0 <= attr.max_value) else (attr.min_value if attr.min_value is not None else 4.0)
                pav = ProductAttrValue.query.filter_by(
                    product_id=product_id, attribute_id=attr.attribute_id
                ).first()
                if pav:
                    pav.raw_value = raw_val
                else:
                    pav = ProductAttrValue(
                        product_id=product_id, attribute_id=attr.attribute_id, raw_value=raw_val
                    )
                    db.session.add(pav)
                continue

            if is_price and (raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == '')):
                raw_val = 1999.0 if (attr.min_value is None or attr.min_value <= 1999.0) else attr.min_value
                pav = ProductAttrValue.query.filter_by(
                    product_id=product_id, attribute_id=attr.attribute_id
                ).first()
                if pav:
                    pav.raw_value = raw_val
                else:
                    pav = ProductAttrValue(
                        product_id=product_id, attribute_id=attr.attribute_id, raw_value=raw_val
                    )
                    db.session.add(pav)
                continue

            if raw_value is not None and (not isinstance(raw_value, str) or raw_value.strip() != ''):
                try:
                    raw_val = float(raw_value)
                except ValueError:
                    flash(f'{attr.name} must be a valid number.', 'danger')
                    return render_template('admin/product_form.html', category=category, attributes=attributes, product=product, existing_values=existing_values)

                if is_rating and raw_val > 5.0 and raw_val <= 100.0 and attr.max_value is not None and attr.max_value <= 5.0:
                    raw_val = round((raw_val / 100.0) * attr.max_value, 2)

                if raw_val < attr.min_value or raw_val > attr.max_value:
                    flash(f'{attr.name} must be between {attr.min_value} and {attr.max_value}.', 'danger')
                    return render_template('admin/product_form.html', category=category, attributes=attributes, product=product, existing_values=existing_values)
                
                pav = ProductAttrValue.query.filter_by(
                    product_id=product_id, attribute_id=attr.attribute_id
                ).first()
                if pav:
                    pav.raw_value = raw_val
                else:
                    pav = ProductAttrValue(
                        product_id=product_id, attribute_id=attr.attribute_id, raw_value=raw_val
                    )
                    db.session.add(pav)
        
        from datetime import datetime, timezone
        product.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Trigger recomputation (FR-11)
        try:
            from app.ranking.engine import recompute_category_scores
            recompute_category_scores(category.category_id, db.session, Product, Attribute, ProductAttrValue)
        except ImportError:
            pass
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.list_products', category_id=category.category_id))
    
    return render_template('admin/product_form.html', category=category, attributes=attributes, product=product, existing_values=existing_values)

@admin.route('/product/<int:product_id>/delete', methods=['POST'])
@company_required
def delete_product(product_id):
    """Delete a product. FR-7."""
    product = db.get_or_404(Product, product_id)
    category = Category.query.filter_by(category_id=product.category_id, company_id=g.company_id).first_or_404()
    category_id = category.category_id
    
    # Delete sponsored placements and attribute values first
    SponsoredPlacement.query.filter_by(product_id=product_id).delete()
    ProductAttrValue.query.filter_by(product_id=product_id).delete()
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('admin.list_products', category_id=category_id))


# Sponsored Placement CRUD routes
@admin.route('/category/<int:category_id>/sponsors')
@company_required
def list_sponsors(category_id):
    """List all sponsored placements for products in a category. FR-14."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    placements = SponsoredPlacement.query.join(Product).filter(
        Product.category_id == category_id
    ).order_by(SponsoredPlacement.start_date.desc()).all()
    stats = get_category_stats(category_id)
    placements_with_status = [{'placement': p, 'status': get_sponsor_status(p)} for p in placements]
    return render_template(
        'admin/sponsor_list.html',
        category=category,
        placements=placements,
        placements_with_status=placements_with_status,
        stats=stats
    )

@admin.route('/category/<int:category_id>/sponsor/new', methods=['GET', 'POST'])
@company_required
def new_sponsor(category_id):
    """Create a new sponsored placement. FR-14."""
    category = Category.query.filter_by(category_id=category_id, company_id=g.company_id).first_or_404()
    form = SponsorForm()
    # Populate product choices with products from this category
    products = Product.query.filter_by(category_id=category_id).all()
    form.product_id.choices = [(p.product_id, p.name) for p in products]
    
    if form.validate_on_submit():
        placement = SponsoredPlacement(
            product_id=form.product_id.data,
            slot_position=form.slot_position.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_active=True
        )
        db.session.add(placement)
        db.session.commit()
        flash('Sponsored placement created.', 'success')
        return redirect(url_for('admin.list_sponsors', category_id=category_id))
    
    return render_template('admin/sponsor_form.html', form=form, category=category, title='New Sponsor')

@admin.route('/sponsor/<int:placement_id>/edit', methods=['GET', 'POST'])
@company_required
def edit_sponsor(placement_id):
    """Edit an existing sponsored placement. FR-14."""
    placement = db.get_or_404(SponsoredPlacement, placement_id)
    product = db.get_or_404(Product, placement.product_id)
    category = Category.query.filter_by(category_id=product.category_id, company_id=g.company_id).first_or_404()
    
    form = SponsorForm(obj=placement)
    products = Product.query.filter_by(category_id=category.category_id).all()
    form.product_id.choices = [(p.product_id, p.name) for p in products]
    
    if form.validate_on_submit():
        placement.product_id = form.product_id.data
        placement.slot_position = form.slot_position.data
        placement.start_date = form.start_date.data
        placement.end_date = form.end_date.data
        db.session.commit()
        flash('Sponsored placement updated.', 'success')
        return redirect(url_for('admin.list_sponsors', category_id=category.category_id))
    
    return render_template('admin/sponsor_form.html', form=form, category=category, title='Edit Sponsor')

@admin.route('/sponsor/<int:placement_id>/delete', methods=['POST'])
@company_required
def delete_sponsor(placement_id):
    """Remove a sponsored placement. FR-14."""
    placement = db.get_or_404(SponsoredPlacement, placement_id)
    product = db.get_or_404(Product, placement.product_id)
    category = Category.query.filter_by(category_id=product.category_id, company_id=g.company_id).first_or_404()
    category_id = category.category_id
    db.session.delete(placement)
    db.session.commit()
    flash('Sponsored placement deleted.', 'success')
    return redirect(url_for('admin.list_sponsors', category_id=category_id))
