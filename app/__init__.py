import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Initialize libraries
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_database():
    """Create the database if it doesn't exist."""
    # Create the connection string without the database
    uri_without_db = f"mysql+pymysql://{Config.MYSQL['user']}:{Config.MYSQL['password']}@{Config.MYSQL['location']}"

    # Create the engine
    engine = create_engine(uri_without_db)

    try:
        # Use connect() for proper execution
        with engine.connect() as conn:
            conn.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL['database']}")
            print(f"Database {Config.MYSQL['database']} created or already exists.")
    except OperationalError as e:
        print(f"Error creating database: {e}")

def create_app():
    app = Flask(__name__)

    # Load config
    app.config.from_object(Config)

    # Create the database before setting the SQLALCHEMY_DATABASE_URI
    create_database()

    # Set the SQLALCHEMY_DATABASE_URI with the correct database after it's created
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{Config.MYSQL['user']}:{Config.MYSQL['password']}@{Config.MYSQL['location']}/{Config.MYSQL['database']}"
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'routes.login'

    from app.routes import bp as routes_bp
    from app.models import User
    
    # Import and register blueprint
    app.register_blueprint(routes_bp)

    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
