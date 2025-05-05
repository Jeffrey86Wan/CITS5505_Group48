# /routes/public.py
from flask import Blueprint, render_template

public_bp = Blueprint('public', __name__, url_prefix='/public')

@public_bp.route('/sharing')
def public_sharing():
    return "<h1>📢 Public Sharing Area (Coming Soon)</h1>"
