import unittest
from flask import Flask, redirect, url_for, request, g
from flask_login import LoginManager, current_user
from db import Base, engine, init_app, get_db
from models import User, Transaction
from sqlalchemy.exc import SQLAlchemyError

print("Flask and SQLAlchemy are ready!")

class TestApp(unittest.TestCase):
    def test_create_app(self):
        app = Flask(__name__)
        self.assertIsNotNone(app)
        self.assertEqual(app.name, 'test_imports')

    def test_user_authentication(self):
        app = Flask(__name__)
        login_manager = LoginManager()
        login_manager.init_app(app)
        self.assertIsNotNone(login_manager)
        self.assertEqual(login_manager.login_view, None)

    def test_database_connection(self):
        app = Flask(__name__)
        init_app(app)
        with app.app_context():
            db = get_db()
            self.assertIsNotNone(db)
            try:
                db.query(User).first()
            except SQLAlchemyError as e:
                self.fail(f"Database query failed: {e}")

    def test_redirect_to_login(self):
        app = Flask(__name__)
        @app.route('/')
        def index():
            return redirect(url_for('auth.login'))
        client = app.test_client()
        response = client.get('/')
        self.assertEqual(response.status_code, 500)

    def test_no_cache_headers(self):
        app = Flask(__name__)
        @app.after_request
        def add_no_cache_headers(response):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            return response
        client = app.test_client()
        response = client.get('/')
        self.assertIn('no-store', response.headers['Cache-Control'])

    def test_user_model(self):
        user = User(username='testuser', email='test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_transaction_model(self):
        transaction = Transaction(amount=100, description='Test transaction')
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.description, 'Test transaction')

if __name__ == '__main__':
    unittest.main()
