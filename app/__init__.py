"""
app/__init__.py — Flask Application Factory
=============================================
Creates and configures the Flask app instance.
Initializes extensions (SQLAlchemy, Migrate, LoginManager).
Registers application blueprints as they are implemented.
"""
import os
from flask import Flask, Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# ---------------------------------------------------------------------------
# Extension instances (created at module level, bound to app inside factory)
# ---------------------------------------------------------------------------
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# ---------------------------------------------------------------------------
# Main blueprint — serves the index / home page
# ---------------------------------------------------------------------------
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route. Returns the landing page template."""
    return render_template('index.html')


def create_app(config_name: str = 'development') -> Flask:
    """
    Factory function to create and configure the Flask application.

    Args:
        config_name: One of 'development', 'testing', 'production'.

    Returns:
        Configured Flask app instance.
    """
    app = Flask(__name__)

    # Import config here to avoid circular imports
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import config
    app.config.from_object(config[config_name])

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register the main (index) blueprint
    app.register_blueprint(main_bp)

    # Register feature blueprints dynamically (for subsequent phases)
    try:
        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
    except (ImportError, AttributeError):
        pass

    try:
        from .admin import admin as admin_blueprint
        app.register_blueprint(admin_blueprint, url_prefix='/admin')
    except (ImportError, AttributeError):
        pass

    try:
        from .insights import insights as insights_blueprint
        app.register_blueprint(insights_blueprint, url_prefix='/insights')
    except (ImportError, AttributeError):
        pass

    try:
        from .api import api as api_blueprint
        app.register_blueprint(api_blueprint, url_prefix='/api')
    except (ImportError, AttributeError):
        pass

    # Create all tables within app context
    with app.app_context():
        from . import models  # noqa: F401 — ensures models are registered
        db.create_all()

    return app
