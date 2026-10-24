from datetime import datetime, date
from app import db


def normalize_value(raw_value: float, min_value: float, max_value: float, lower_is_better: bool = False) -> float:
    """
    Normalize a raw attribute value to 0-1 scale using min-max scaling.
    Implements FR-9.
    
    Args:
        raw_value: The raw attribute value.
        min_value: The minimum value for this attribute.
        max_value: The maximum value for this attribute.
        lower_is_better: If True, invert the normalized value (1 - norm).
    
    Returns:
        Normalized value between 0.0 and 1.0.
    """
    # Defensive guards for missing or null arguments
    if raw_value is None:
        return 0.0
    if min_value is None:
        min_value = 0.0
    if max_value is None:
        max_value = 1.0

    # Guard: if min == max, return 0.5 (avoid division by zero)
    if max_value == min_value:
        return 0.5
    norm = (raw_value - min_value) / (max_value - min_value)
    # Clamp to [0, 1] in case raw_value is slightly out of range
    norm = max(0.0, min(1.0, norm))
    if lower_is_better:
        norm = 1.0 - norm
    return round(norm, 6)


def compute_product_score(product_values: list[dict]) -> float:
    """
    Compute composite score for a single product.
    Implements FR-10.
    
    Args:
        product_values: List of dicts with keys:
            - 'raw_value': float
            - 'min_value': float  (from attribute)
            - 'max_value': float  (from attribute)
            - 'weight': float     (percentage, 0-100)
            - 'lower_is_better': bool
    
    Returns:
        Composite score as float between 0.0 and 1.0.
    """
    score = 0.0
    for val in product_values:
        norm = normalize_value(
            val['raw_value'], val['min_value'], val['max_value'], val['lower_is_better']
        )
        score += norm * (val['weight'] / 100.0)
    return round(score, 6)


def _get_timestamp(val) -> float:
    """Safely extract float timestamp from datetime, date, str, int, or float."""
    if not val:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, datetime):
        return val.timestamp()
    if isinstance(val, date):
        return datetime.combine(val, datetime.min.time()).timestamp()
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val).timestamp()
        except (ValueError, TypeError):
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
    if hasattr(val, 'timestamp'):
        try:
            return val.timestamp()
        except Exception:
            return 0.0
    return 0.0


def rank_products(products_with_scores: list[dict]) -> list[dict]:
    """
    Sort products by composite score with tie-breaking.
    Implements FR-12, FR-13.
    
    Tie-break rule (FR-13):
      1. Descending composite score
      2. Most recently created first (descending created_at)
      3. Lowest product_id first (ascending product_id)
    
    Args:
        products_with_scores: List of dicts with keys:
            - 'product_id': int
            - 'name': str
            - 'composite_score': float
            - 'created_at': datetime, str, int, or None
    
    Returns:
        Sorted list (highest score first).
    """
    return sorted(
        products_with_scores,
        key=lambda p: (
            0 if p.get('is_sponsored') else 1,
            -(p.get('composite_score') if p.get('composite_score') is not None else 0.0),
            -_get_timestamp(p.get('created_at')),
            p.get('product_id', 0)
        )
    )


def recompute_category_scores(category_id: int, db_session, Product, Attribute, ProductAttrValue):
    """
    Recompute composite scores for ALL products in a category.
    Implements FR-11.
    
    Called when:
      - A product's attribute value changes
      - A category's weight configuration changes
    
    Args:
        category_id: The category to recompute.
        db_session: SQLAlchemy db.session
        Product, Attribute, ProductAttrValue: Model classes (passed to avoid Flask imports)
    """
    active_attrs = db_session.scalars(
        db.select(Attribute).filter_by(category_id=category_id, is_active=True)
    ).all()
    products = db_session.scalars(
        db.select(Product).filter_by(category_id=category_id)
    ).all()
    
    if not products or not active_attrs:
        return

    product_ids = [p.product_id for p in products]
    all_pavs = db_session.scalars(
        db.select(ProductAttrValue).filter(ProductAttrValue.product_id.in_(product_ids))
    ).all()

    # Map (product_id, attribute_id) -> pav
    pav_map = {(pav.product_id, pav.attribute_id): pav for pav in all_pavs}

    for product in products:
        product_values = []
        for attr in active_attrs:
            pav = pav_map.get((product.product_id, attr.attribute_id))
            if pav and pav.raw_value is not None:
                # Update normalized value
                pav.normalized_value = normalize_value(
                    pav.raw_value, attr.min_value, attr.max_value, attr.lower_is_better
                )
                product_values.append({
                    'raw_value': pav.raw_value,
                    'min_value': attr.min_value,
                    'max_value': attr.max_value,
                    'weight': attr.weight,
                    'lower_is_better': attr.lower_is_better
                })
        
        product.composite_score = compute_product_score(product_values)
    
    db_session.commit()
