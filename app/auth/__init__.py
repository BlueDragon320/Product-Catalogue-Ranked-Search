"""
Auth Blueprint initialization.
Implements FR: Setup Auth Blueprint.
"""
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes  # noqa: F401, E402
