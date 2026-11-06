from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager

class Company(db.Model):
    """
    Represents a company/tenant using the platform.
    """
    __tablename__ = 'companies'
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='company', lazy='dynamic')
    categories = db.relationship('Category', backref='company', lazy='dynamic')

    def __repr__(self):
        return f"<Company {self.name}>"

class User(UserMixin, db.Model):
    """
    Represents an authenticated user (admin or standard) within a company.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), index=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_superadmin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """Sets the user password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies the user password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

@login_manager.user_loader
def load_user(user_id):
    """Loads user for Flask-Login."""
    return User.query.get(int(user_id))

class Category(db.Model):
    """
    Product categories belonging to a specific company.
    """
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attributes = db.relationship('Attribute', backref='category', lazy='dynamic')
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return f"<Category {self.name}>"

class Attribute(db.Model):
    """
    Attributes defined for a category, used in scoring.
    """
    __tablename__ = 'attributes'
    attribute_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), index=True)
    name = db.Column(db.String(100), nullable=False)
    data_type = db.Column(db.String(50), default='numeric')
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    weight = db.Column(db.Float, default=1.0)
    lower_is_better = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Attribute {self.name}>"

class Product(db.Model):
    """
    Products belonging to a category, to be ranked.
    """
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), index=True)
    name = db.Column(db.String(200), nullable=False)
    composite_score = db.Column(db.Float, default=0.0)
    search_count = db.Column(db.Integer, default=0)
    is_sponsored = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attribute_values = db.relationship('ProductAttrValue', backref='product', lazy='dynamic')
    sponsored_placements = db.relationship('SponsoredPlacement', backref='product', lazy='dynamic')

    def __repr__(self):
        return f"<Product {self.name}>"

class ProductAttrValue(db.Model):
    """
    Stores raw and normalized values for a specific attribute of a product.
    """
    __tablename__ = 'product_attr_values'
    pav_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), index=True)
    attribute_id = db.Column(db.Integer, db.ForeignKey('attributes.attribute_id'), index=True)
    raw_value = db.Column(db.Float)
    normalized_value = db.Column(db.Float)

    attribute = db.relationship('Attribute', backref='attr_values')

    __table_args__ = (db.UniqueConstraint('product_id', 'attribute_id', name='_product_attr_uc'),)

    def __repr__(self):
        return f"<ProductAttrValue Product:{self.product_id} Attr:{self.attribute_id}>"

class SponsoredPlacement(db.Model):
    """
    Defines explicit placement overrides for products.
    """
    __tablename__ = 'sponsored_placements'
    placement_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), index=True)
    slot_position = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<SponsoredPlacement Product:{self.product_id} Slot:{self.slot_position}>"

class SearchLog(db.Model):
    """
    Tracks search queries, matched categories, and result yields for insights analytics.
    """
    __tablename__ = 'search_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)
    results_count = db.Column(db.Integer, default=0)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', backref='search_logs')

    def __repr__(self):
        return f"<SearchLog query='{self.query_text}' results={self.results_count}>"
