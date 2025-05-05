# /routes/auth/login.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from db import  get_db
from models import User
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = get_db()
        try:
            user = db.query(User).filter_by(email=email).first()
            # Inside your login route
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password.', 'error')
        except SQLAlchemyError as e:
            flash('Database error during login.', 'error')
            print(e)

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        # Inside your register route:
        hashed_password = generate_password_hash(password)

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        db = get_db()
        try:
            # Check if email already exists
            existing = db.query(User).filter_by(email=email).first()
            if existing:
                flash('Email already registered.', 'error')
                return render_template('auth/register.html')

            # Create user and save
            new_user = User(email=email, username=username, password=hashed_password)
            db.add(new_user)
            db.commit()

            flash('Registered successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except SQLAlchemyError as e:
            db.rollback()
            flash('Error during registration.', 'error')
            print(e)

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))  # Or 'auth.login'
