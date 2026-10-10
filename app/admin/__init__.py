from flask import Blueprint
admin = Blueprint('admin', __name__)
from . import routes  # noqa: F401, E402
