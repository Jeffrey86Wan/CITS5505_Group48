# routes/flow.py
from flask import Blueprint, render_template

flow_bp = Blueprint('flow', __name__, url_prefix='/flow')

@flow_bp.route('/')
def index():
    return "<h1>💰 Transactions Page (Coming Soon)</h1>"
