"""Ranking engine module — pure Python, no Flask dependency."""
from .engine import normalize_value, compute_product_score, rank_products, recompute_category_scores
