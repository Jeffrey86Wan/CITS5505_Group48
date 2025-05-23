# routes/__init__.py

from flask import Blueprint
from .home import home_bp
from .auth import auth_bp
from .upload import upload_bp
from .record import record_bp
from .flow import flow_bp
from .report import report_bp
from .api import api_bp


def register_routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(record_bp)
    app.register_blueprint(flow_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(api_bp)

