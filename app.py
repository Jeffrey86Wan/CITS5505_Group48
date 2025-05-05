# /app.py
from flask import Flask
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
from routes import register_routes
import os
from db import Base, engine, init_app, get_db
from models import User, Transaction, Upload
from flask import g

load_dotenv()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'

    # Setup login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register routes
    register_routes(app)

    # Setup DB teardown and CLI
    init_app(app)

    # Set g.user for templates
    @app.before_request
    def load_logged_in_user():
        g.user = current_user if current_user.is_authenticated else None

    # Sample home route
    @app.route('/')
    def index():
        return 'Welcome! Go to <a href="/auth/login">Login</a> or <a href="/auth/register">Register</a>'

    return app

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    return db.query(User).get(int(user_id))

# Create DB and tables if not already there
if not os.path.exists("expensemanager.db"):
    print("🔧 Creating database and tables...")
    Base.metadata.create_all(bind=engine)
    
    
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)