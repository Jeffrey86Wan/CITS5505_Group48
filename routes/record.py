# routes/record.py
from flask import Blueprint

record_bp = Blueprint('record', __name__, url_prefix='/record')

@record_bp.route('/')
def index():
    return "<h1>📘 Add Record Page (Coming Soon)</h1>"
