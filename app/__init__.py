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

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    
    # Configure database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://web:mypass@localhost/StrikeOne'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app
    db.init_app(app)

    # Create database and tables
    create_database(app)

    return app

def create_database(app):
    """Create the database and tables if they don't exist."""
    try:
        # Connect to MySQL without specifying a database to allow database creation
        connection = pymysql.connect(
            host='localhost',
            user='web',
            password='mypass',
        )
        
        print("Connection successful!")

        # Create the database if it doesn't exist
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS StrikeOne")
            print("Database 'StrikeOne' created or already exists.")

        # Now connect to the newly created database
        connection.select_db('StrikeOne')

        # Define the accounts table with required attributes
        with app.app_context():
            class Account(db.Model):
                __tablename__ = 'accounts'

                LoginID = db.Column(db.Integer, primary_key=True)
                Username = db.Column(db.String(100), unique=True, nullable=False)
                Password = db.Column(db.String(100), nullable=False)
                is_admin = db.Column(db.Boolean, default=False)  # False for regular users

            # Create the table (if it doesn't exist)
            db.create_all()

        print("Accounts table created or already exists.")

        # Close the connection after all operations are done
        connection.close()

    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
