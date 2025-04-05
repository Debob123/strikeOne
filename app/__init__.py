import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
# Initialize libraries
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_database():
    """Ensure the 'StrikeOne' database exists before Flask app starts."""
    try:
        # Connect to MySQL without specifying the database
        connection = pymysql.connect(
            host='localhost',
            user='web',
            password='mypass'
        )
        
        print("Connection successful!")

        # Create the 'StrikeOne' database if it doesn't exist
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS StrikeOne")
            print("Database 'StrikeOne' created or already exists.")

        # Close the connection
        connection.close()

    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")

def create_app():
    """Create and configure the Flask app."""
    # First ensure the database exists
    create_database()

    app = Flask(__name__)

    # Configure the database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://web:mypass@localhost/StrikeOne'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    # Create tables and insert the admin account
    create_tables_and_admin(app)

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

def create_tables_and_admin(app):

    from app.models import User
    """Create tables and insert the admin account if it doesn't already exist."""
    with app.app_context():
        # Create the tables based on existing models if they don't exist
        db.create_all()

        # Check if the admin account already exists
        admin_account = User.query.filter_by(username='admin').first()

        if admin_account is None:
            # If the admin account doesn't exist, create it
            hashed_password = generate_password_hash('adminpassword', method='pbkdf2:sha256')
            new_admin = User(
                username='admin',
                password=hashed_password,
                is_admin=True
            )

            # Add the new admin account to the database
            db.session.add(new_admin)
            db.session.commit()
            print("Admin account created.")
        else:
            print("Admin account already exists.")

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
