def apply_tiebreak_sort(products: list) -> list:
    """
    Sort product objects by the FR-13 tie-break rule.
    Works with SQLAlchemy Product objects directly.
    """
    return sorted(
        products,
        key=lambda p: (
            0 if getattr(p, 'is_sponsored', False) else 1,
            -(p.composite_score if p.composite_score is not None else 0.0),
            -(p.created_at.timestamp() if p.created_at else 0.0),
            p.product_id or 0
        )
    )

def format_score_display(score: float) -> str:
    """Format a composite score for display (e.g., 0.8523 -> '85.23%')."""
    return f"{(score or 0.0) * 100:.2f}%"

def get_score_breakdown(product, attributes, product_attr_values) -> list[dict]:
    """
    Get a detailed breakdown of how a product's score was computed.
    Useful for the 'why is this product ranked here' explanation.
    Returns list of {attribute_name, raw_value, normalized_value, weight, contribution}.
    """
    breakdown = []
    total_score = getattr(product, 'composite_score', 0.0) or 0.0
    for attr in attributes:
        pav = next((v for v in product_attr_values if v.attribute_id == attr.attribute_id), None)
        if pav:
            from .engine import normalize_value
            norm = normalize_value(pav.raw_value, attr.min_value, attr.max_value, attr.lower_is_better)
            contribution = norm * (attr.weight / 100.0)
            contrib_pct = round((contribution / total_score * 100), 1) if total_score > 0 else 0.0
            breakdown.append({
                'attribute_name': attr.name,
                'raw_value': pav.raw_value,
                'min_value': attr.min_value,
                'max_value': attr.max_value,
                'lower_is_better': attr.lower_is_better,
                'normalized_value': round(norm, 4),
                'normalized_pct': round(norm * 100, 1),
                'weight': attr.weight,
                'contribution': round(contribution, 4),
                'contribution_pct': min(100.0, max(0.0, contrib_pct))
            })
    return breakdown


def insert_sponsored_placements(ranked_products: list, sponsored_products: list, slots_per_group: int = 5) -> list:
    """
    Insert sponsored products into capped slots in the ranked results.
    Implements FR-15: One sponsored slot per 'slots_per_group' results.
    
    Sponsored products are placed at positions 1, 1+slots_per_group, 1+2*slots_per_group, ...
    A sponsored product's score is never altered (FR-15).
    
    Args:
        ranked_products: List of Product objects, already sorted by score.
        sponsored_products: List of Product objects that have active sponsorships.
        slots_per_group: Number of results per sponsored slot (default 5, per NFR-5.6).
    
    Returns:
        List of dicts: {'product': Product, 'is_sponsored': bool, 'position': int}
    """
    results = []
    def _slot_sort_key(p):
        try:
            placements = p.sponsored_placements.filter_by(is_active=True).all()
            if placements:
                return min(sp.slot_position for sp in placements)
        except Exception:
            pass
        return getattr(p, 'slot_position', 999999)

    sponsored_queue = sorted(list(sponsored_products), key=_slot_sort_key)
    organic_queue = [p for p in ranked_products if p not in sponsored_products]
    
    sponsor_idx = 0
    organic_idx = 0
    position = 1
    
    while organic_idx < len(organic_queue) or sponsor_idx < len(sponsored_queue):
        # Check if this position is a sponsored slot
        is_sponsor_slot = (position - 1) % slots_per_group == 0
        
        if is_sponsor_slot and sponsor_idx < len(sponsored_queue):
            results.append({
                'product': sponsored_queue[sponsor_idx],
                'is_sponsored': True,
                'position': position
            })
            sponsor_idx += 1
        elif organic_idx < len(organic_queue):
            results.append({
                'product': organic_queue[organic_idx],
                'is_sponsored': False,
                'position': position
            })
            organic_idx += 1
        else:
            # Only sponsors left, append remaining
            if sponsor_idx < len(sponsored_queue):
                results.append({
                    'product': sponsored_queue[sponsor_idx],
                    'is_sponsored': True,
                    'position': position
                })
                sponsor_idx += 1
            else:
                break
        position += 1
    
    return results


def get_active_sponsored_products(category_id, Product, SponsoredPlacement):
    """
    Get products with currently active sponsorships for a category.
    Implements FR-17: Auto-expire past end_date.
    
    Args:
        category_id: Category to check.
        Product, SponsoredPlacement: Model classes.
    
    Returns:
        List of Product objects with active sponsorships ordered by slot_position.
    """
    from datetime import date
    from app import db
    today = date.today()
    
    active_placements = SponsoredPlacement.query.join(Product).filter(
        Product.category_id == category_id,
        SponsoredPlacement.start_date <= today,
        SponsoredPlacement.end_date >= today,
        SponsoredPlacement.is_active == True
    ).order_by(SponsoredPlacement.slot_position.asc()).all()
    
    seen = set()
    ordered_products = []
    for sp in active_placements:
        if sp.product_id not in seen:
            seen.add(sp.product_id)
            prod = sp.product or db.session.get(Product, sp.product_id)
            if prod:
                ordered_products.append(prod)

    # Also include products where is_sponsored attribute is directly enabled
    flagged = Product.query.filter(
        Product.category_id == category_id,
        Product.is_sponsored == True
    ).all()
    for fp in flagged:
        if fp.product_id not in seen:
            seen.add(fp.product_id)
            ordered_products.append(fp)

    return ordered_products


def get_sponsor_status(placement) -> dict:
    """
    Compute detailed status of a sponsored placement (active, scheduled, expired).
    Returns dict with status, label, badge CSS class, and human-friendly message.
    """
    from datetime import date
    today = date.today()
    if not placement.is_active:
        return {
            'status': 'inactive',
            'label': 'Disabled',
            'class': 'badge-secondary',
            'message': 'Manually deactivated'
        }
    if placement.end_date < today:
        days_ago = (today - placement.end_date).days
        return {
            'status': 'expired',
            'label': 'Expired',
            'class': 'badge-danger',
            'message': f'Ended {days_ago}d ago'
        }
    if placement.start_date > today:
        days_until = (placement.start_date - today).days
        return {
            'status': 'scheduled',
            'label': 'Scheduled',
            'class': 'badge-info',
            'message': f'Starts in {days_until}d'
        }
    days_left = (placement.end_date - today).days
    return {
        'status': 'active',
        'label': 'Active Now',
        'class': 'badge-success',
        'message': f'Active · {days_left}d left'
    }


def get_category_stats(category_id: int) -> dict:
    """
    Aggregate key statistics for a category to power the Category Hub & dashboard.
    Returns product count, attribute count, weight total, weight validation status,
    and active sponsor count.
    """
    from app import db
    from app.models import Category, Product, Attribute, SponsoredPlacement
    from datetime import date
    category = db.session.get(Category, category_id)
    if not category:
        return {}
    products = Product.query.filter_by(category_id=category_id).all()
    attributes = Attribute.query.filter_by(category_id=category_id).all()
    active_attrs = [a for a in attributes if a.is_active]
    total_weight = sum(a.weight for a in active_attrs)
    is_weight_valid = abs(total_weight - 100.0) < 0.01

    today = date.today()
    sponsors = SponsoredPlacement.query.join(Product).filter(
        Product.category_id == category_id,
        SponsoredPlacement.start_date <= today,
        SponsoredPlacement.end_date >= today,
        SponsoredPlacement.is_active == True
    ).all()

    avg_score = (sum((p.composite_score or 0.0) for p in products) / len(products)) * 100 if products else 0.0

    return {
        'category_id': category.category_id,
        'name': category.name,
        'product_count': len(products),
        'attribute_count': len(attributes),
        'active_attribute_count': len(active_attrs),
        'total_weight': round(total_weight, 2),
        'is_weight_valid': is_weight_valid,
        'weight_diff': round(100.0 - total_weight, 2),
        'active_sponsor_count': len(sponsors),
        'avg_score': round(avg_score, 1)
    }


def ensure_default_category_attributes(category_id: int, db_session=None):
    """
    Guarantees that default 'Rating' and 'Price' attributes exist for the category.
    If missing Rating, creates Attribute with name='Rating', data_type='numeric',
    min_value=0.0, max_value=5.0, weight=0.0, lower_is_better=False, is_active=True.
    If missing Price, creates Attribute with name='Price (INR)', data_type='numeric',
    min_value=0.0, max_value=50000.0, weight=0.0, lower_is_better=True, is_active=True.
    Also checks existing products in this category:
    - For Rating: if missing PAV, creates PAV with raw_value=4.5, normalized_value=0.9.
    - For Price: if missing PAV, creates PAV with raw_value=1999.0, normalized_value using normalize_value.
    """
    if db_session is None:
        from app import db
        db_session = db.session

    from app.models import Attribute, Product, ProductAttrValue
    from sqlalchemy import func
    from .engine import normalize_value

    # Case-insensitive check for 'Rating'
    rating_attr = db_session.query(Attribute).filter(
        Attribute.category_id == category_id,
        func.lower(Attribute.name) == 'rating'
    ).first()

    if not rating_attr:
        rating_attr = Attribute(
            category_id=category_id,
            name='Rating',
            data_type='numeric',
            min_value=0.0,
            max_value=5.0,
            weight=0.0,
            lower_is_better=False,
            is_active=True
        )
        db_session.add(rating_attr)
        db_session.flush()

    # Case-insensitive check if any attribute contains 'price'
    price_attr = db_session.query(Attribute).filter(
        Attribute.category_id == category_id,
        func.lower(Attribute.name).contains('price')
    ).first()

    if not price_attr:
        price_attr = Attribute(
            category_id=category_id,
            name='Price (INR)',
            data_type='numeric',
            min_value=0.0,
            max_value=50000.0,
            weight=0.0,
            lower_is_better=True,
            is_active=True
        )
        db_session.add(price_attr)
        db_session.flush()

    products = db_session.query(Product).filter_by(category_id=category_id).all()
    for product in products:
        pav_rating = db_session.query(ProductAttrValue).filter_by(
            product_id=product.product_id,
            attribute_id=rating_attr.attribute_id
        ).first()
        if not pav_rating:
            pav_rating = ProductAttrValue(
                product_id=product.product_id,
                attribute_id=rating_attr.attribute_id,
                raw_value=4.5,
                normalized_value=0.9
            )
            db_session.add(pav_rating)

        pav_price = db_session.query(ProductAttrValue).filter_by(
            product_id=product.product_id,
            attribute_id=price_attr.attribute_id
        ).first()
        if not pav_price:
            price_norm = normalize_value(1999.0, price_attr.min_value, price_attr.max_value, price_attr.lower_is_better)
            pav_price = ProductAttrValue(
                product_id=product.product_id,
                attribute_id=price_attr.attribute_id,
                raw_value=1999.0,
                normalized_value=price_norm
            )
            db_session.add(pav_price)

    db_session.commit()
    return rating_attr, price_attr


def is_default_attribute(attr_or_name) -> bool:
    """
    Returns True if name is 'rating' or contains 'price' (case-insensitive).
    """
    if hasattr(attr_or_name, 'name'):
        name = attr_or_name.name
    elif isinstance(attr_or_name, str):
        name = attr_or_name
    else:
        name = str(attr_or_name or '')
    name_clean = name.strip().lower()
    return name_clean == 'rating' or 'price' in name_clean


def ensure_all_categories_have_default_attributes(db_session=None):
    """
    Iterates through all categories in the system and calls ensure_default_category_attributes.
    """
    if db_session is None:
        from app import db
        db_session = db.session

    from app.models import Category
    try:
        categories = db_session.query(Category).all()
        for category in categories:
            ensure_default_category_attributes(category.category_id, db_session=db_session)
    except Exception:
        db_session.rollback()


ensure_all_categories_have_rating = ensure_all_categories_have_default_attributes


