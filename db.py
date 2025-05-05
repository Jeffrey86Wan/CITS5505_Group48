# models/db.py
import os
import click
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from flask import g
from flask.cli import with_appcontext

# Define your DB URL (SQLite in this case)
DATABASE_URL = "sqlite:///expensemanager.db"

# Create engine (the connection to the DB)
engine = create_engine(DATABASE_URL, echo=True)

# Create base model class for all ORM models to inherit
Base = declarative_base()

# Create a session factory (for querying, inserting)
SessionLocal = scoped_session(sessionmaker(bind=engine))

# Session getter for use in routes
def get_db():
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

# Teardown function to close session per request
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing DB and create new tables (dev only)."""
    flask_env = os.environ.get('FLASK_ENV')

    if flask_env == 'development':
        click.echo('⚠️  Dropping all tables (development mode)...')
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    click.echo('✅ Database initialized.')
    
@click.command('delete-db')
@with_appcontext
def delete_db_command():
    """Delete the SQLite database file."""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_path):
        os.remove(db_path)
        click.echo(f"🗑️ Deleted database: {db_path}")
    else:
        click.echo("⚠️ Database file not found.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(delete_db_command)
    