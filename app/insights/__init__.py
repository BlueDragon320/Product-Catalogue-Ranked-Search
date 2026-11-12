"""
app/insights/__init__.py — Insights & Search Analytics Blueprint
===============================================================
Replaces legacy storefront with interactive search, search analytics,
multi-criteria sensitivity analysis, and anti-bias sponsor metrics.

Author: Dev-A (Vaibhav) | Phase: P7 | Feature: Insights Engine
"""
from flask import Blueprint

insights = Blueprint('insights', __name__)

from . import routes  # noqa: F401
