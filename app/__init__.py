import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
import pymysql

# Initialize libraries
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to MySQL without specifying a database to allow database creation
        connection = pymysql.connect(
            host=Config.MYSQL['location'],
            user=Config.MYSQL['user'],
            password=Config.MYSQL['password'],
        )
        
        print("Connection successful!")

        # Create the database if it doesn't exist
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL['database']}")
            print(f"Database '{Config.MYSQL['database']}' created or already exists.")

        # Now connect to the newly created database
        connection.select_db(Config.MYSQL['database'])

        # Close the connection after all operations are done
        connection.close()

    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")

def create_app():
    # Create the database before app initialization
    create_database()

    # Initialize Flask app
    app = Flask(__name__)

    # Load config
    app.config.from_object(Config)

    # Set the SQLALCHEMY_DATABASE_URI after ensuring the database exists
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{Config.MYSQL['user']}:{Config.MYSQL['password']}@{Config.MYSQL['location']}/{Config.MYSQL['database']}"
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'routes.login'

    # Import and register blueprint
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
