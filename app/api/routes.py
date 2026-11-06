from datetime import datetime, date, timezone
from flask import jsonify, request
from flask_login import login_required
from sqlalchemy.orm import joinedload
from app import db
from app.models import Company, Category, Attribute, Product, ProductAttrValue, SponsoredPlacement, SearchLog
from app.api import api
from app.ranking.engine import normalize_value, compute_product_score, recompute_category_scores
from app.ranking.helpers import apply_tiebreak_sort, insert_sponsored_placements, get_active_sponsored_products, get_score_breakdown, format_score_display, is_default_attribute

def get_request_company_id():
    """Extract tenant company_id from query params, X-Company-ID header, or JSON body."""
    cid = request.args.get('company_id') or request.headers.get('X-Company-ID')
    if not cid and request.is_json:
        data = request.get_json(silent=True) or {}
        cid = data.get('company_id')
    if cid is not None:
        try:
            return int(cid)
        except (ValueError, TypeError):
            return None
    return None

# -----------------------------------------------------------------------------
# Internal Admin Weight Calibration Endpoints (FR-3, NFR-5.1)
# -----------------------------------------------------------------------------

@api.route('/weight-total/<int:category_id>', methods=['GET'])
@login_required
def weight_total(category_id):
    """
    Returns the current sum of active attribute weights for a category.
    Used by the admin panel's live weight indicator.
    """
    attributes = Attribute.query.filter_by(
        category_id=category_id,
        is_active=True
    ).all()
    total = sum(attr.weight for attr in attributes)
    count = len(attributes)
    is_valid = abs(total - 100.0) < 0.01
    return jsonify({
        'total': round(total, 2),
        'count': count,
        'is_valid': is_valid,
        'message': 'Weights sum to 100%' if is_valid else f'Weights sum to {round(total, 2)}% (must be 100%)'
    })

@api.route('/weight-validate', methods=['POST'])
@login_required
def weight_validate():
    """
    Validates if changing a specific attribute's weight would keep total at 100%.
    Accepts JSON: {category_id, attribute_id (optional), new_weight}
    """
    data = request.get_json()
    category_id = data.get('category_id')
    attribute_id = data.get('attribute_id')
    new_weight = float(data.get('new_weight', 0))
    
    attributes = Attribute.query.filter_by(category_id=category_id, is_active=True).all()
    total = sum(a.weight for a in attributes if a.attribute_id != attribute_id)
    projected_total = total + new_weight
    is_valid = abs(projected_total - 100.0) < 0.01
    
    return jsonify({
        'current_total': round(total, 2),
        'projected_total': round(projected_total, 2),
        'is_valid': is_valid
    })

# -----------------------------------------------------------------------------
# External B2B Search & Ranking REST API (v1)
# -----------------------------------------------------------------------------

@api.route('/v1/search', methods=['GET', 'POST'])
def search_products():
    """
    External multi-tenant product search and ranking endpoint.
    Used by client companies to power search operations with deterministic weighted ranking.
    """
    company_id = get_request_company_id()
    if not company_id:
        return jsonify({
            'status': 'error',
            'error': 'MISSING_COMPANY_ID',
            'message': "Required parameter 'company_id' is missing. Pass it via query string, JSON payload, or 'X-Company-ID' header."
        }), 400

    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({
            'status': 'error',
            'error': 'COMPANY_NOT_FOUND',
            'message': f"Company with ID {company_id} does not exist."
        }), 404

    req_json = request.get_json(silent=True) or {} if request.is_json else {}
    q = (request.args.get('q') or req_json.get('q') or '').strip()
    
    category_id = request.args.get('category_id') or req_json.get('category_id')
    if category_id:
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'error': 'INVALID_CATEGORY_ID', 'message': 'category_id must be an integer.'}), 400

    # FR-21: Attribute Range Filtering query parameters
    filter_attr_id_param = request.args.get('filter_attr_id')
    if filter_attr_id_param is None and req_json:
        filter_attr_id_param = req_json.get('filter_attr_id')

    filter_attr_param = request.args.get('filter_attr')
    if filter_attr_param is None and req_json:
        filter_attr_param = req_json.get('filter_attr')

    filter_min_param = request.args.get('filter_min')
    if filter_min_param is None and req_json:
        filter_min_param = req_json.get('filter_min')

    filter_max_param = request.args.get('filter_max')
    if filter_max_param is None and req_json:
        filter_max_param = req_json.get('filter_max')

    filter_min = None
    if filter_min_param is not None and str(filter_min_param).strip() != '':
        try:
            filter_min = float(filter_min_param)
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'error': 'INVALID_FILTER_MIN',
                'message': 'filter_min must be a numeric value.'
            }), 400

    filter_max = None
    if filter_max_param is not None and str(filter_max_param).strip() != '':
        try:
            filter_max = float(filter_max_param)
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'error': 'INVALID_FILTER_MAX',
                'message': 'filter_max must be a numeric value.'
            }), 400

    try:
        limit = min(int(request.args.get('limit') or req_json.get('limit') or 20), 100)
    except (ValueError, TypeError):
        limit = 20
    try:
        offset = max(int(request.args.get('offset') or req_json.get('offset') or 0), 0)
    except (ValueError, TypeError):
        offset = 0
    
    inc_sponsors_param = request.args.get('include_sponsors')
    if inc_sponsors_param is None:
        inc_sponsors = req_json.get('include_sponsors', True)
    else:
        inc_sponsors = str(inc_sponsors_param).lower() not in ['false', '0', 'no']

    custom_weights = req_json.get('custom_weights') or request.args.get('custom_weights')

    company_cat_ids = [c.category_id for c in Category.query.filter_by(company_id=company_id).all()]
    if category_id and category_id not in company_cat_ids:
        return jsonify({
            'status': 'error',
            'error': 'CATEGORY_NOT_FOUND',
            'message': f"Category ID {category_id} does not belong to company '{company.name}'."
        }), 404

    if not company_cat_ids:
        return jsonify({
            'status': 'success',
            'engine': 'Product Catalogue Ranked Search',
            'company_id': company.company_id,
            'company_name': company.name,
            'query': q,
            'category_id': category_id,
            'category_name': None,
            'display_attr_1': None,
            'display_attr_2': None,
            'display_attributes': [],
            'total_results': 0,
            'offset': offset,
            'limit': limit,
            'results': []
        }), 200

    target_cat_ids = [category_id] if category_id else company_cat_ids

    # Query products with enhanced text sanitization, whitespace tolerance, and typo tolerance
    prod_query = Product.query.filter(Product.category_id.in_(target_cat_ids))
    if q:
        # 1. Exact substring match on product name
        matched_products = prod_query.filter(Product.name.ilike(f'%{q}%')).all()

        if not matched_products:
            import re
            import difflib
            from sqlalchemy import or_
            clean_q = ' '.join(re.sub(r'[^a-zA-Z0-9\s]', ' ', q).lower().split())
            collapsed_q = clean_q.replace(' ', '')

            # 2. Whitespace-collapsed match (e.g. 'head phones' -> 'headphones', 'vs 102' -> 'vs102')
            if collapsed_q != clean_q:
                matched_products = prod_query.filter(Product.name.ilike(f'%{collapsed_q}%')).all()

            # 3. Common electronics category/product synonyms
            if not matched_products:
                SYNONYM_MAP = {
                    'earphone': 'earbuds', 'earphones': 'earbuds', 'ear phone': 'earbuds', 'ear phones': 'earbuds',
                    'earfone': 'earbuds', 'earfones': 'earbuds', 'earpod': 'earbuds', 'earpods': 'earbuds',
                    'ear pod': 'earbuds', 'ear pods': 'earbuds', 'airpod': 'earbuds', 'airpods': 'earbuds',
                    'head phone': 'headphones', 'head phones': 'headphones', 'headfone': 'headphones', 'headfones': 'headphones',
                    'hedphones': 'headphones', 'hedphone': 'headphones',
                    'smart watch': 'smartwatch', 'smart watches': 'smartwatch', 'samrtwatch': 'smartwatch',
                    'neck band': 'neckband', 'neck bands': 'neckband', 'nekband': 'neckband',
                    'sunglasses': 'eyewear', 'sun glasses': 'eyewear', 'sunglases': 'eyewear', 'glasses': 'eyewear'
                }
                syn = SYNONYM_MAP.get(clean_q) or SYNONYM_MAP.get(collapsed_q)
                if syn:
                    matched_products = prod_query.filter(
                        or_(
                            Product.name.ilike(f'%{syn}%'),
                            Product.category.has(Category.name.ilike(f'%{syn}%'))
                        )
                    ).all()

            # 4. Fuzzy typo correction against existing product names and categories in this company
            if not matched_products:
                all_company_prods = Product.query.filter(Product.category_id.in_(target_cat_ids)).all()
                vocab = set()
                for p in all_company_prods:
                    for t in re.sub(r'[^a-zA-Z0-9\s]', ' ', p.name).lower().split():
                        if len(t) >= 3:
                            vocab.add(t)
                for c in Category.query.filter(Category.category_id.in_(target_cat_ids)).all():
                    for t in re.sub(r'[^a-zA-Z0-9\s]', ' ', c.name).lower().split():
                        if len(t) >= 3:
                            vocab.add(t)
                    vocab.add(c.name.lower().replace(' ', ''))

                tokens = clean_q.split()
                corrected_tokens = []
                for t in tokens:
                    if t in vocab:
                        corrected_tokens.append(t)
                    else:
                        matches = difflib.get_close_matches(t, list(vocab), n=1, cutoff=0.72)
                        corrected_tokens.append(matches[0] if matches else t)
                corrected_q = ' '.join(corrected_tokens)
                if corrected_q != clean_q:
                    matched_products = prod_query.filter(
                        or_(
                            Product.name.ilike(f'%{corrected_q}%'),
                            Product.category.has(Category.name.ilike(f'%{corrected_q}%'))
                        )
                    ).all()

            # 5. Category name match
            if not matched_products:
                cat_ids = [c.category_id for c in Category.query.filter(
                    Category.company_id == company_id,
                    or_(Category.name.ilike(f'%{clean_q}%'), Category.name.ilike(f'%{collapsed_q}%'))
                ).all()]
                if cat_ids:
                    matched_products = Product.query.filter(Product.category_id.in_(cat_ids)).all()
    else:
        matched_products = prod_query.all()

    # FR-21: Attribute Range Filtering
    target_attr_ids = set()
    is_filtering = False

    if filter_attr_id_param is not None and str(filter_attr_id_param).strip() != '':
        is_filtering = True
        val_str = str(filter_attr_id_param).strip()
        try:
            aid = int(val_str)
            attr = Attribute.query.filter(
                Attribute.attribute_id == aid,
                Attribute.category_id.in_(target_cat_ids)
            ).first()
            if attr:
                target_attr_ids.add(attr.attribute_id)
        except (ValueError, TypeError):
            matching_attrs = Attribute.query.filter(
                Attribute.category_id.in_(target_cat_ids),
                Attribute.name.ilike(val_str)
            ).all()
            target_attr_ids.update(a.attribute_id for a in matching_attrs)

    elif filter_attr_param is not None and str(filter_attr_param).strip() != '':
        is_filtering = True
        val_str = str(filter_attr_param).strip()
        matching_attrs = Attribute.query.filter(
            Attribute.category_id.in_(target_cat_ids),
            Attribute.name.ilike(val_str)
        ).all()
        target_attr_ids.update(a.attribute_id for a in matching_attrs)

    elif filter_min is not None or filter_max is not None:
        attrs_in_cat = Attribute.query.filter(
            Attribute.category_id.in_(target_cat_ids),
            Attribute.is_active == True
        ).all()
        if len(attrs_in_cat) == 1:
            is_filtering = True
            target_attr_ids.add(attrs_in_cat[0].attribute_id)

    if is_filtering:
        if not target_attr_ids:
            matched_products = []
        else:
            pids = [p.product_id for p in matched_products]
            if not pids:
                matched_products = []
            else:
                pavs = ProductAttrValue.query.filter(
                    ProductAttrValue.product_id.in_(pids),
                    ProductAttrValue.attribute_id.in_(target_attr_ids)
                ).all()
                prod_val_map = {}
                for pav in pavs:
                    if pav.raw_value is not None:
                        prod_val_map[pav.product_id] = pav.raw_value

                filtered_prods = []
                for p in matched_products:
                    if p.product_id in prod_val_map:
                        val = prod_val_map[p.product_id]
                        if filter_min is not None and val < filter_min:
                            continue
                        if filter_max is not None and val > filter_max:
                            continue
                        filtered_prods.append(p)
                matched_products = filtered_prods

    # Dynamic Weight Personalization OR Default Scored Ranking
    if custom_weights and isinstance(custom_weights, dict) and category_id:
        try:
            parsed_weights = {k: float(v) for k, v in custom_weights.items()}
            weight_sum = sum(parsed_weights.values())
            if abs(weight_sum - 100.0) > 0.05:
                return jsonify({
                    'status': 'error',
                    'error': 'INVALID_WEIGHT_SUM',
                    'message': f"Custom weights must sum to 100.0%. Current sum: {weight_sum}%"
                }), 400
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'error': 'INVALID_WEIGHTS', 'message': 'Weights must be numeric values.'}), 400

        cat_attrs = Attribute.query.filter_by(category_id=category_id, is_active=True).all()
        attr_map = {a.name: a for a in cat_attrs}
        attr_id_map = {str(a.attribute_id): a for a in cat_attrs}

        scored_products = []
        for p in matched_products:
            pavs = ProductAttrValue.query.filter_by(product_id=p.product_id).all()
            pav_dict = {v.attribute_id: v.raw_value for v in pavs}
            p_values = []
            for w_key, w_val in parsed_weights.items():
                attr = attr_map.get(w_key) or attr_id_map.get(str(w_key))
                if attr:
                    raw_val = pav_dict.get(attr.attribute_id, 0.0)
                    p_values.append({
                        'raw_value': raw_val,
                        'min_value': attr.min_value,
                        'max_value': attr.max_value,
                        'weight': w_val,
                        'lower_is_better': attr.lower_is_better
                    })
            score = compute_product_score(p_values)
            scored_products.append({
                'product': p,
                'composite_score': score
            })
        scored_products.sort(
            key=lambda item: (
                -item['composite_score'],
                -(item['product'].created_at.timestamp() if item['product'].created_at else 0.0),
                item['product'].product_id
            )
        )
        ranked_items = [item['product'] for item in scored_products]
    else:
        ranked_items = apply_tiebreak_sort(matched_products)

    # Sponsored Placement Interleaving (1:5 Capped Slots)
    final_ranked_results = []
    if inc_sponsors and category_id:
        active_sponsors = get_active_sponsored_products(category_id, Product, SponsoredPlacement)
        if q or is_filtering:
            active_sponsors = [s for s in active_sponsors if s in matched_products]
        
        placed = insert_sponsored_placements(ranked_items, active_sponsors, slots_per_group=5)
        for entry in placed:
            final_ranked_results.append({
                'product': entry['product'],
                'is_sponsored': entry['is_sponsored']
            })
    else:
        today = date.today()
        sponsor_pids = set(
            sp.product_id for sp in SponsoredPlacement.query.join(Product).filter(
                Product.category_id.in_(target_cat_ids),
                SponsoredPlacement.start_date <= today,
                SponsoredPlacement.end_date >= today,
                SponsoredPlacement.is_active == True
            ).all()
        )
        for p in ranked_items:
            final_ranked_results.append({
                'product': p,
                'is_sponsored': (p.product_id in sponsor_pids) or bool(getattr(p, 'is_sponsored', False))
            })

    # When not using 1:5 interleaving, ensure sponsored items partition to the top; if inc_sponsors is False, strip sponsored items
    if not inc_sponsors:
        final_ranked_results = [item for item in final_ranked_results if not item['is_sponsored']]
    elif not category_id:
        sponsors = [item for item in final_ranked_results if item['is_sponsored']]
        organics = [item for item in final_ranked_results if not item['is_sponsored']]
        final_ranked_results = sponsors + organics

    # Telemetry: Track search count & record SearchLog
    for item in final_ranked_results:
        p = item['product']
        p.search_count = (p.search_count or 0) + 1
    
    log_entry = SearchLog(
        query_text=q or "*",
        category_id=category_id,
        results_count=len(final_ranked_results),
        searched_at=datetime.now(timezone.utc)
    )
    db.session.add(log_entry)
    db.session.commit()

    # Pagination slice
    paginated_results = final_ranked_results[offset:offset + limit]

    # Eager load ProductAttrValue and Attribute for the paginated slice
    page_pids = [item['product'].product_id for item in paginated_results]
    pavs_by_pid = {}
    if page_pids:
        all_page_pavs = db.session.scalars(
            db.select(ProductAttrValue)
            .options(joinedload(ProductAttrValue.attribute))
            .filter(ProductAttrValue.product_id.in_(page_pids))
        ).all()
        for pav in all_page_pavs:
            pavs_by_pid.setdefault(pav.product_id, []).append(pav)

    # Build response payload
    results_data = []
    for rank_idx, item in enumerate(paginated_results, start=offset + 1):
        prod = item['product']
        is_sp = item['is_sponsored']
        cat = prod.category
        
        pavs = pavs_by_pid.get(prod.product_id, [])
        attrs_data = {}
        for pav in pavs:
            a = pav.attribute
            if a:
                attrs_data[a.name] = {
                    'attribute_id': a.attribute_id,
                    'data_type': a.data_type,
                    'raw_value': pav.raw_value,
                    'normalized_value': pav.normalized_value,
                    'weight': a.weight,
                    'lower_is_better': a.lower_is_better,
                    'display_value': ("YES" if pav.raw_value == 1.0 else "NO") if a.data_type == 'binary' else pav.raw_value
                }

        # Build display_badges for product
        prod_cat = prod.category or (db.session.get(Category, prod.category_id) if prod.category_id else None)
        target_display_attrs = [a for a in [prod_cat.display_attr_1, prod_cat.display_attr_2] if a] if prod_cat else []
        badges = []
        if target_display_attrs:
            for attr_name in target_display_attrs:
                matched_key = None
                if attr_name in attrs_data:
                    matched_key = attr_name
                else:
                    for k in attrs_data:
                        if k.strip().lower() == attr_name.strip().lower():
                            matched_key = k
                            break
                if matched_key:
                    attr_info = attrs_data[matched_key]
                    badges.append({
                        'name': matched_key,
                        'value': attr_info['display_value'],
                        'raw_value': attr_info['raw_value'],
                        'data_type': attr_info['data_type']
                    })
        else:
            for a_name, a_info in attrs_data.items():
                if not is_default_attribute(a_name):
                    badges.append({
                        'name': a_name,
                        'value': a_info['display_value'],
                        'raw_value': a_info['raw_value'],
                        'data_type': a_info['data_type']
                    })
                    if len(badges) == 2:
                        break

        results_data.append({
            'rank': rank_idx,
            'product_id': prod.product_id,
            'name': prod.name,
            'category_id': prod.category_id,
            'category_name': prod_cat.name if prod_cat else None,
            'composite_score': prod.composite_score,
            'score_pct': format_score_display(prod.composite_score or 0.0),
            'is_sponsored': is_sp,
            'display_badges': badges,
            'attributes': attrs_data
        })

    cat = db.session.get(Category, category_id) if category_id else None
    cat_name = cat.name if cat else None
    return jsonify({
        'status': 'success',
        'engine': 'Product Catalogue Ranked Search',
        'company_id': company.company_id,
        'company_name': company.name,
        'query': q,
        'category_id': category_id,
        'category_name': cat_name,
        'display_attr_1': cat.display_attr_1 if cat else None,
        'display_attr_2': cat.display_attr_2 if cat else None,
        'display_attributes': [a for a in [cat.display_attr_1, cat.display_attr_2] if a] if cat else [],
        'total_results': len(final_ranked_results),
        'offset': offset,
        'limit': limit,
        'results': results_data
    })


@api.route('/v1/categories', methods=['GET'])
def get_categories():
    """
    Get all categories and their attribute configurations for a tenant company.
    Parameters:
      - company_id: (required) Tenant company ID
    """
    company_id = get_request_company_id()
    if not company_id:
        return jsonify({'status': 'error', 'error': 'MISSING_COMPANY_ID', 'message': "Required parameter 'company_id' is missing."}), 400

    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({'status': 'error', 'error': 'COMPANY_NOT_FOUND', 'message': f"Company with ID {company_id} does not exist."}), 404

    categories = Category.query.filter_by(company_id=company_id).all()
    data = []
    for cat in categories:
        attrs = Attribute.query.filter_by(category_id=cat.category_id, is_active=True).all()
        prod_count = Product.query.filter_by(category_id=cat.category_id).count()
        data.append({
            'category_id': cat.category_id,
            'name': cat.name,
            'product_count': prod_count,
            'display_attr_1': cat.display_attr_1,
            'display_attr_2': cat.display_attr_2,
            'display_attributes': [a for a in [cat.display_attr_1, cat.display_attr_2] if a],
            'attributes': [
                {
                    'attribute_id': a.attribute_id,
                    'name': a.name,
                    'data_type': a.data_type,
                    'weight': a.weight,
                    'min_value': a.min_value,
                    'max_value': a.max_value,
                    'lower_is_better': a.lower_is_better
                } for a in attrs
            ]
        })

    return jsonify({
        'status': 'success',
        'company_id': company.company_id,
        'company_name': company.name,
        'categories': data
    })


@api.route('/v1/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get full ranking details and attribute breakdown for a single product.
    Parameters:
      - company_id: (required) Tenant company ID
    """
    company_id = get_request_company_id()
    if not company_id:
        return jsonify({'status': 'error', 'error': 'MISSING_COMPANY_ID', 'message': "Required parameter 'company_id' is missing."}), 400

    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({'status': 'error', 'error': 'COMPANY_NOT_FOUND', 'message': f"Company with ID {company_id} does not exist."}), 404

    product = db.session.get(Product, product_id)
    if not product or product.category.company_id != company_id:
        return jsonify({'status': 'error', 'error': 'PRODUCT_NOT_FOUND', 'message': f"Product with ID {product_id} not found under company '{company.name}'."}), 404

    category = product.category
    attributes = Attribute.query.filter_by(category_id=category.category_id, is_active=True).all()
    pavs = ProductAttrValue.query.filter_by(product_id=product.product_id).all()
    breakdown = get_score_breakdown(product, attributes, pavs)

    today = date.today()
    is_sponsored = (
        bool(getattr(product, 'is_sponsored', False)) or
        SponsoredPlacement.query.filter(
            SponsoredPlacement.product_id == product.product_id,
            SponsoredPlacement.start_date <= today,
            SponsoredPlacement.end_date >= today,
            SponsoredPlacement.is_active == True
        ).first() is not None
    )

    return jsonify({
        'status': 'success',
        'product_id': product.product_id,
        'name': product.name,
        'company_id': company.company_id,
        'company_name': company.name,
        'category_id': category.category_id,
        'category_name': category.name,
        'composite_score': product.composite_score,
        'score_pct': format_score_display(product.composite_score or 0.0),
        'search_count': product.search_count or 0,
        'is_sponsored': is_sponsored,
        'score_breakdown': breakdown
    })


@api.route('/v1/product/<int:product_id>', methods=['POST', 'PUT', 'PATCH'])
def update_product(product_id):
    """
    Update a product's price, rating, name, and/or attribute values, and trigger score recomputation.
    Parameters:
      - company_id: (required) Tenant company ID passed via query string, header, or body.
    """
    company_id = get_request_company_id()
    if not company_id:
        return jsonify({
            'status': 'error',
            'error': 'MISSING_COMPANY_ID',
            'message': "Required parameter 'company_id' is missing."
        }), 400

    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({
            'status': 'error',
            'error': 'COMPANY_NOT_FOUND',
            'message': f"Company with ID {company_id} does not exist."
        }), 404

    product = db.session.get(Product, product_id)
    if not product or not product.category or product.category.company_id != company_id:
        return jsonify({
            'status': 'error',
            'error': 'PRODUCT_NOT_FOUND',
            'message': f"Product with ID {product_id} not found under company '{company.name}'."
        }), 404

    req_data = None
    if request.is_json:
        req_data = request.get_json(silent=True)
    if req_data is None:
        req_data = request.form.to_dict() if request.form else {}
    if not req_data:
        req_data = request.get_json(force=True, silent=True) or {}

    # Update product name if provided
    if 'name' in req_data and req_data['name'] is not None:
        new_name = str(req_data['name']).strip()
        if new_name:
            product.name = new_name

    category_attrs = Attribute.query.filter_by(category_id=product.category_id).all()
    updates = {}

    # Handle direct 'price' field: updates attribute where attr.name has 'price' case-insensitive
    if 'price' in req_data and req_data['price'] is not None:
        try:
            p_val = float(req_data['price'])
            price_attr = next((a for a in category_attrs if 'price' in a.name.lower()), None)
            if price_attr:
                updates[price_attr] = p_val
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'error': 'INVALID_PRICE',
                'message': 'Price must be a valid numeric value.'
            }), 400

    # Handle direct 'rating' field: updates attribute where attr.name is 'Rating'
    if 'rating' in req_data and req_data['rating'] is not None:
        try:
            r_val = float(req_data['rating'])
            rating_attr = next((a for a in category_attrs if a.name.strip().lower() == 'rating'), None)
            if not rating_attr:
                rating_attr = next((a for a in category_attrs if 'rating' in a.name.lower()), None)
            if rating_attr:
                updates[rating_attr] = r_val
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'error': 'INVALID_RATING',
                'message': 'Rating must be a valid numeric value.'
            }), 400

    # Handle direct 'attributes' dictionary: {attribute_name: value}
    if 'attributes' in req_data and isinstance(req_data['attributes'], dict):
        for a_name, a_val in req_data['attributes'].items():
            if a_val is None:
                continue
            try:
                val = float(a_val)
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'error': 'INVALID_ATTRIBUTE_VALUE',
                    'message': f"Attribute value for '{a_name}' must be numeric."
                }), 400

            matched_attr = next((a for a in category_attrs if a.name == a_name), None)
            if not matched_attr:
                matched_attr = next((a for a in category_attrs if a.name.strip().lower() == str(a_name).strip().lower()), None)
            if not matched_attr and str(a_name).isdigit():
                matched_attr = next((a for a in category_attrs if a.attribute_id == int(a_name)), None)
            if not matched_attr and 'price' in str(a_name).lower():
                matched_attr = next((a for a in category_attrs if 'price' in a.name.lower()), None)
            if not matched_attr and 'rating' in str(a_name).lower():
                matched_attr = next((a for a in category_attrs if 'rating' in a.name.lower()), None)
            if matched_attr:
                updates[matched_attr] = val

    # Handle attribute names present as top-level keys
    for a in category_attrs:
        if a not in updates and a.name in req_data and req_data[a.name] is not None:
            try:
                updates[a] = float(req_data[a.name])
            except (ValueError, TypeError):
                pass

    # Update or create ProductAttrValue records and normalize
    for attr, val in updates.items():
        pav = ProductAttrValue.query.filter_by(
            product_id=product.product_id,
            attribute_id=attr.attribute_id
        ).first()
        if not pav:
            pav = ProductAttrValue(
                product_id=product.product_id,
                attribute_id=attr.attribute_id
            )
            db.session.add(pav)
        pav.raw_value = float(val)
        pav.normalized_value = normalize_value(
            pav.raw_value, attr.min_value, attr.max_value, attr.lower_is_better
        )

    product.updated_at = datetime.now(timezone.utc)
    db.session.flush()

    # Recompute category scores
    recompute_category_scores(product.category_id, db.session, Product, Attribute, ProductAttrValue)
    db.session.commit()
    db.session.refresh(product)

    return jsonify({
        'status': 'success',
        'message': 'Product updated and re-ranked successfully',
        'product_id': product.product_id,
        'name': product.name,
        'category_id': product.category_id,
        'composite_score': product.composite_score,
        'score_pct': format_score_display(product.composite_score or 0.0)
    }), 200

