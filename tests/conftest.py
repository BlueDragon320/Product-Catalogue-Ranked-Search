"""
tests/conftest.py — Shared pytest fixtures for all test modules.
Author: Dev-A (Vaibhav) | Phase: P4

Provides the app and client fixtures used across test_models.py,
test_engine.py, test_sponsor.py, and test_routes.py.
"""
import pytest
from app import create_app, db as _db


@pytest.fixture
def app():
    """Create a Flask app configured for testing with an in-memory SQLite DB."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Provide a Flask test client."""
    return app.test_client()
