# routes/auth/oauth.py

from flask import Blueprint
from routes.auth.login import auth_bp

@auth_bp.route("/google")
def login_with_google():
    return "OAuth login coming soon!"
