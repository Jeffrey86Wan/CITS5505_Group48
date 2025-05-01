import sqlite3
import click
import os
from flask import current_app, g
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

def get_db():
    if 'db' not in g:
        engine = create_engine(f'sqlite:///{current_app.config["DATABASE"]}')
        g.db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        g.engine = engine
        Base.query = g.db.query_property()
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    # Ensure database file exists
    db_path = current_app.config["DATABASE"]
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # First create an empty SQLite database file
    if not os.path.exists(db_path):
        # Create empty database
        conn = sqlite3.connect(db_path)
        conn.close()
        print(f"Database file created: {db_path}")
    
    # Create tables
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Import all models
    from models import User, Transaction, Blog, Category
    # Or simply: from .models import *
    
    # Drop all tables and recreate
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Add default categories
    db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    
    # Default expense categories
    default_categories = [
        # Expense categories
        Category(id=1, name='Dining', type='expense', icon='fa-utensils', color='#FEE2E2', is_default=True, created_at=datetime.now()),
        Category(id=2, name='Shopping', type='expense', icon='fa-shopping-bag', color='#EDE9FE', is_default=True, created_at=datetime.now()),
        Category(id=3, name='Transportation', type='expense', icon='fa-subway', color='#FEF3C7', is_default=True, created_at=datetime.now()),
        Category(id=4, name='Housing', type='expense', icon='fa-home', color='#D1FAE5', is_default=True, created_at=datetime.now()),
        # Income categories
        Category(id=5, name='Salary', type='income', icon='fa-money-bill-wave', color='#DBEAFE', is_default=True, created_at=datetime.now()),
        Category(id=6, name='Bonus', type='income', icon='fa-gift', color='#E0E7FF', is_default=True, created_at=datetime.now()),
        Category(id=7, name='Investment', type='income', icon='fa-chart-line', color='#DCFCE7', is_default=True, created_at=datetime.now()),
        Category(id=8, name='Other', type='income', icon='fa-wallet', color='#F3E8FF', is_default=True, created_at=datetime.now())
    ]
    
    for category in default_categories:
        db.add(category)
    
    db.commit()
    db.close()
    
    print(f"Database initialization completed, location: {db_path}")

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Database initialization completed.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)