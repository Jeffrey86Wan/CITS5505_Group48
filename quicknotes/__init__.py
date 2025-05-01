import os
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta


def create_app(test_config=None):
    # Create and configure the application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'suishouji.sqlite'),
        # Set session expiration time to 30 days
        PERMANENT_SESSION_LIFETIME=timedelta(days=30)
    )

    if test_config is None:
        # Load instance configuration (if it exists)
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load test configuration
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    from db import init_app as init_db_app
    init_db_app(app)

    # Register authentication blueprint
    from auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # Register transaction record blueprint
    from record import bp as record_bp
    app.register_blueprint(record_bp)

    # Register transaction flow blueprint
    from flow import bp as flow_bp
    app.register_blueprint(flow_bp)


    # Global request hook, protect routes that require login
    @app.before_request
    def require_login():
        # Paths that can be accessed without login
        allowed_routes = ['index', 'auth.login', 'auth.register', 'static', 'public_sharing']
        
        # Check if user is logged in and if the current route allows unauthenticated access
        if (not session.get('user_id') and 
            request.endpoint not in allowed_routes and
            not (request.endpoint and (request.endpoint.startswith('auth.') or request.path.startswith('/static')))):
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))

    # Register home page route
    @app.route('/')
    def index():
        return render_template('main/index.html')
        
    # Transaction record page route
    @app.route('/record')
    def transaction_record():
        # Ensure user is logged in
        if not session.get('user_id'):
            flash('Please login before adding transactions', 'error')
            return redirect(url_for('auth.login'))
        return render_template('main/record.html', active_page='record')
        
    # Transaction flow page route
    @app.route('/flow')
    def transaction_flow():
        # Ensure user is logged in
        if not session.get('user_id'):
            flash('Please login to view transaction history', 'error')
            return redirect(url_for('auth.login'))
        return render_template('main/flow.html', active_page='flow')
        
    # Report page route
    @app.route('/report')
    def financial_report():
        # Ensure user is logged in
        if not session.get('user_id'):
            flash('Please login to view reports', 'error')
            return redirect(url_for('auth.login'))
        return render_template('main/report.html', active_page='report')
        
    # Public sharing area page route
    @app.route('/public')
    def public_sharing():
        return render_template('main/public.html')

    return app
