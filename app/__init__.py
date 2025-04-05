# app/__init__.py
import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from app.routes import bp as routes_bp
from app.models import User

# Initialize libraries
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

     # Print BEFORE setting config from class
    print("Before config:", app.config.get('SQLALCHEMY_DATABASE_URI'))

    app.config.from_object(Config)  # Loads MYSQL dict and SECRET_KEY, etc.

    # Print AFTER
    print("After config:", app.config.get('SQLALCHEMY_DATABASE_URI'))

    # Optional: Print full MYSQL dict
    print("MYSQL Settings:", Config.MYSQL)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{Config.MYSQL['user']}:{Config.MYSQL['password']}@{Config.MYSQL['location']}/{Config.MYSQL['database']}"
    )

    print("Final DB URI:", app.config['SQLALCHEMY_DATABASE_URI'])

    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'routes.login'

    # Import and register blueprint
    app.register_blueprint(routes_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
