# routes/report.py
from flask import Blueprint

report_bp = Blueprint('report', __name__)

@report_bp.route('/report')
def financial_report():
    return "<h1>📊 Financial Report Page (Coming Soon)</h1>"
