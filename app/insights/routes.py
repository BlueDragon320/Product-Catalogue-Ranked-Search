"""
app/insights/routes.py — Insights & Search Analytics Engine
==========================================================
Provides search intelligence, top-searched products leaderboard, category
traffic breakdown, weight sensitivity analysis, and anti-bias policy checks.
Supports multi-tenant isolation so company operators only inspect their own data.

Author: Dev-A (Vaibhav) | Phase: P8/P9 | Feature: Insights Engine & Multi-Tenancy
"""
from datetime import date, datetime, timezone
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Category, Product, Attribute, ProductAttrValue, SponsoredPlacement, SearchLog, Company
from app.ranking.helpers import apply_tiebreak_sort, format_score_display
from app.insights import insights

@insights.route('/')
@login_required
def index():
    """
    Unified Insights & Search Intelligence Dashboard.
    Supports interactive querying, search frequency tracking,
    leaderboards, weight sensitivity metrics, and sponsor integrity audits.
    Enforces multi-tenant data isolation when accessed by company managers or inspecting superadmins.
    """
    search_query = request.args.get('q', '').strip()
    selected_category_id = request.args.get('category_id', type=int)
    today = date.today()

    # Determine tenant scoping
    scoped_company_id = None
    scoped_company = None
    if current_user.is_authenticated:
        if current_user.is_superadmin:
            inspect_id = session.get('inspect_company_id')
            if inspect_id:
                scoped_company_id = inspect_id
                scoped_company = db.session.get(Company, inspect_id)
        else:
            scoped_company_id = current_user.company_id
            scoped_company = current_user.company

    if scoped_company_id is not None:
        all_categories = Category.query.filter_by(company_id=scoped_company_id).order_by(Category.name.asc()).all()
        scoped_cat_ids = [c.category_id for c in all_categories]
    else:
        all_categories = Category.query.order_by(Category.name.asc()).all()
        scoped_cat_ids = [c.category_id for c in all_categories]

    # If category filter requested, verify it is within scope
    if selected_category_id and scoped_company_id is not None:
        if selected_category_id not in scoped_cat_ids:
            selected_category_id = None

    # Handle completely empty tenant catalog (e.g. user deleted all categories/products)
    if scoped_company_id is not None and not scoped_cat_ids:
        return render_template(
            'insights/index.html',
            search_query=search_query,
            selected_category_id=None,
            filter_attr_id=None,
            filter_min=None,
            filter_max=None,
            available_attributes=[],
            search_results=[],
            all_categories=[],
            top_searched_products=[],
            category_insights=[],
            attributes_by_weight=[],
            active_sponsorships=[],
            active_sponsor_count=0,
            total_products_count=0,
            current_sponsor_ratio=0.0,
            is_cap_compliant=True,
            recent_queries=[],
            scoped_company=scoped_company,
            format_score=format_score_display
        )

    # Available category attributes for filtering UI
    if selected_category_id:
        available_attributes = Attribute.query.filter_by(
            category_id=selected_category_id,
            is_active=True
        ).order_by(Attribute.name.asc()).all()
    elif scoped_cat_ids:
        available_attributes = Attribute.query.filter(
            Attribute.category_id.in_(scoped_cat_ids),
            Attribute.is_active == True
        ).order_by(Attribute.name.asc()).all()
    else:
        available_attributes = []

    # FR-21: Attribute Range Filtering query parameters
    filter_attr_id_param = request.args.get('filter_attr_id')
    filter_attr_param = request.args.get('filter_attr')
    filter_min_param = request.args.get('filter_min')
    filter_max_param = request.args.get('filter_max')

    filter_min = None
    if filter_min_param is not None and str(filter_min_param).strip() != '':
        try:
            filter_min = float(str(filter_min_param).strip())
        except (ValueError, TypeError):
            filter_min = None

    filter_max = None
    if filter_max_param is not None and str(filter_max_param).strip() != '':
        try:
            filter_max = float(str(filter_max_param).strip())
        except (ValueError, TypeError):
            filter_max = None

    filter_attr_id = None
    target_attr_ids = set()

    if filter_attr_id_param is not None and str(filter_attr_id_param).strip() != '':
        val_str = str(filter_attr_id_param).strip()
        try:
            aid = int(val_str)
            attr = Attribute.query.filter(
                Attribute.attribute_id == aid,
                Attribute.category_id.in_(scoped_cat_ids)
            ).first()
            if attr:
                target_attr_ids.add(attr.attribute_id)
                filter_attr_id = attr.attribute_id
        except (ValueError, TypeError):
            matching_attrs = Attribute.query.filter(
                Attribute.category_id.in_(scoped_cat_ids),
                Attribute.name.ilike(val_str)
            ).all()
            for a in matching_attrs:
                target_attr_ids.add(a.attribute_id)
            if matching_attrs:
                filter_attr_id = matching_attrs[0].attribute_id

    elif filter_attr_param is not None and str(filter_attr_param).strip() != '':
        val_str = str(filter_attr_param).strip()
        matching_attrs = Attribute.query.filter(
            Attribute.category_id.in_(scoped_cat_ids),
            Attribute.name.ilike(val_str)
        ).all()
        for a in matching_attrs:
            target_attr_ids.add(a.attribute_id)
        if matching_attrs:
            filter_attr_id = matching_attrs[0].attribute_id

    elif filter_min is not None or filter_max is not None:
        if len(available_attributes) == 1:
            target_attr_ids.add(available_attributes[0].attribute_id)
            filter_attr_id = available_attributes[0].attribute_id

    is_filtering = bool(target_attr_ids or filter_attr_id_param or filter_attr_param or (filter_min is not None and target_attr_ids) or (filter_max is not None and target_attr_ids))

    # -------------------------------------------------------------------------
    # 1. Interactive Product Search & Dynamic Weighted Ranking
    # -------------------------------------------------------------------------
    search_results = []
    if search_query or is_filtering:
        if search_query:
            query_filter = Product.name.ilike(f'%{search_query}%')
            if scoped_company_id is not None:
                query_filter = query_filter & (Product.category_id.in_(scoped_cat_ids))

            if selected_category_id:
                query_filter = query_filter & (Product.category_id == selected_category_id)

            matched_products = Product.query.filter(query_filter).all()

            # If no direct product name match, check category name match within scope
            if not matched_products and not selected_category_id:
                cat_query = Category.name.ilike(f'%{search_query}%')
                if scoped_company_id is not None:
                    cat_query = cat_query & (Category.company_id == scoped_company_id)
                matched_cats = Category.query.filter(cat_query).all()
                if matched_cats:
                    match_cat_ids = [c.category_id for c in matched_cats]
                    matched_products = Product.query.filter(Product.category_id.in_(match_cat_ids)).all()
        else:
            base_query = Product.query
            if scoped_company_id is not None:
                base_query = base_query.filter(Product.category_id.in_(scoped_cat_ids))
            if selected_category_id:
                base_query = base_query.filter(Product.category_id == selected_category_id)
            matched_products = base_query.all()

        # Attribute Range Filtering (FR-21)
        if is_filtering:
            if not target_attr_ids:
                matched_products = []
            else:
                pids = [p.product_id for p in matched_products]
                if pids:
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
                else:
                    matched_products = []

        # Rank matched products using engine's multi-criteria scoring & tie-break
        ranked_matches = apply_tiebreak_sort(matched_products)

        # Active sponsored product IDs within scope
        sponsor_q = SponsoredPlacement.query.join(Product).filter(
            SponsoredPlacement.start_date <= today,
            SponsoredPlacement.end_date >= today,
            SponsoredPlacement.is_active == True
        )
        if scoped_company_id is not None:
            sponsor_q = sponsor_q.filter(Product.category_id.in_(scoped_cat_ids))
        active_sponsors = sponsor_q.all()
        sponsored_pids = {sp.product_id for sp in active_sponsors}

        # Track search hit count on matched products and log query
        for rank_idx, prod in enumerate(ranked_matches, start=1):
            prod.search_count = (prod.search_count or 0) + 1
            search_results.append({
                'product': prod,
                'rank': rank_idx,
                'is_sponsored': (prod.product_id in sponsored_pids) or bool(getattr(prod, 'is_sponsored', False))
            })

        # Record in SearchLog
        log_entry = SearchLog(
            query_text=search_query or (f"[Filter:attr={filter_attr_id}]" if filter_attr_id else "*"),
            category_id=selected_category_id,
            results_count=len(search_results),
            searched_at=datetime.now(timezone.utc)
        )
        db.session.add(log_entry)
        db.session.commit()

    # -------------------------------------------------------------------------
    # 2. Most Searched Products Leaderboard (Scoped to Company)
    # -------------------------------------------------------------------------
    top_prod_query = Product.query
    if scoped_company_id is not None:
        top_prod_query = top_prod_query.filter(Product.category_id.in_(scoped_cat_ids))

    top_searched_products = top_prod_query.filter(Product.search_count > 0)\
        .order_by(Product.search_count.desc(), Product.composite_score.desc())\
        .limit(8).all()

    # Fallback to highest ranked products if search volume is fresh
    if not top_searched_products:
        top_searched_products = top_prod_query.order_by(Product.composite_score.desc()).limit(8).all()

    # -------------------------------------------------------------------------
    # 3. Category Search Volume & Popularity Distribution
    # -------------------------------------------------------------------------
    category_insights = []
    if scoped_company_id is not None:
        total_searches_logged = SearchLog.query.filter(SearchLog.category_id.in_(scoped_cat_ids)).count()
    else:
        total_searches_logged = SearchLog.query.count()

    for cat in all_categories:
        cat_search_count = SearchLog.query.filter_by(category_id=cat.category_id).count()
        cat_products_search_sum = db.session.query(func.coalesce(func.sum(Product.search_count), 0))\
            .filter(Product.category_id == cat.category_id).scalar()
        
        share_pct = round((cat_search_count / total_searches_logged * 100), 1) if total_searches_logged > 0 else 0

        scores = [p.composite_score for p in cat.products.all() if p.composite_score is not None]
        avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0
        max_score = round(max(scores), 3) if scores else 0.0
        min_score = round(min(scores), 3) if scores else 0.0

        category_insights.append({
            'category': cat,
            'direct_searches': cat_search_count,
            'product_hits': int(cat_products_search_sum),
            'share_pct': share_pct,
            'product_count': cat.products.count(),
            'avg_score': avg_score,
            'max_score': max_score,
            'min_score': min_score
        })

    category_insights.sort(key=lambda x: (x['product_hits'] + x['direct_searches']), reverse=True)

    # -------------------------------------------------------------------------
    # 4. Multi-Criteria Weight Sensitivity & Criteria Distribution
    # -------------------------------------------------------------------------
    attr_query = Attribute.query.filter_by(is_active=True)
    if scoped_company_id is not None:
        attr_query = attr_query.filter(Attribute.category_id.in_(scoped_cat_ids))

    attributes_by_weight = attr_query.order_by(Attribute.weight.desc()).limit(10).all()

    # -------------------------------------------------------------------------
    # 5. Sponsored Placement Policy & Anti-Bias Integrity Audit
    # -------------------------------------------------------------------------
    sponsor_audit_q = SponsoredPlacement.query.join(Product).filter(
        SponsoredPlacement.start_date <= today,
        SponsoredPlacement.end_date >= today,
        SponsoredPlacement.is_active == True
    )
    product_count_q = Product.query
    if scoped_company_id is not None:
        sponsor_audit_q = sponsor_audit_q.filter(Product.category_id.in_(scoped_cat_ids))
        product_count_q = product_count_q.filter(Product.category_id.in_(scoped_cat_ids))

    active_sponsorships = sponsor_audit_q.all()
    total_products_count = product_count_q.count()
    active_sponsor_count = len(active_sponsorships)

    current_sponsor_ratio = round((active_sponsor_count / total_products_count * 100), 1) if total_products_count > 0 else 0
    is_cap_compliant = current_sponsor_ratio <= 20.0

    # -------------------------------------------------------------------------
    # 6. Recent Search Queries Stream
    # -------------------------------------------------------------------------
    recent_query_q = SearchLog.query
    if scoped_company_id is not None:
        recent_query_q = recent_query_q.filter(SearchLog.category_id.in_(scoped_cat_ids))
    recent_queries = recent_query_q.order_by(SearchLog.searched_at.desc()).limit(10).all()

    return render_template(
        'insights/index.html',
        search_query=search_query,
        selected_category_id=selected_category_id,
        filter_attr_id=filter_attr_id,
        filter_min=filter_min,
        filter_max=filter_max,
        available_attributes=available_attributes,
        search_results=search_results,
        all_categories=all_categories,
        top_searched_products=top_searched_products,
        category_insights=category_insights,
        attributes_by_weight=attributes_by_weight,
        active_sponsorships=active_sponsorships,
        active_sponsor_count=active_sponsor_count,
        total_products_count=total_products_count,
        current_sponsor_ratio=current_sponsor_ratio,
        is_cap_compliant=is_cap_compliant,
        recent_queries=recent_queries,
        scoped_company=scoped_company,
        format_score=format_score_display
    )
