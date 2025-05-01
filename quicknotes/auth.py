import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db
from models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        db = get_db()
        error = None

        if not username:
            error = 'Username cannot be empty'
        elif not password:
            error = 'Password cannot be empty'
        elif password != confirm_password:
            error = 'The passwords do not match'
        elif db.query(User).filter(User.username == username).first() is not None:
            error = f'User {username} is already registered'

        if error is None:
            user = User(
                username=username,
                password=generate_password_hash(password)
            )
            db.add(user)
            db.commit()
            flash('Registration successful, please login', 'success')
            return redirect(url_for('auth.login'))

        flash(error, 'error')

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.query(User).filter(User.username == username).first()

        if user is None:
            error = 'Username does not exist'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session.permanent = True
            session['user_id'] = user.id
            flash('Login successful', 'success')
            return redirect(url_for('index'))

        flash(error, 'error')

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().query(User).filter(User.id == user_id).first()

@bp.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out', 'success')
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Please login first', 'error')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
