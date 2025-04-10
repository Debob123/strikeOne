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

def copy_baseball_tables():
    """Copy all tables and data from 'baseball' into 'StrikeOne' if they don't exist."""
    try:
        source_conn = pymysql.connect(host='localhost', user='web', password='mypass', database='baseball')
        target_conn = pymysql.connect(host='localhost', user='web', password='mypass', database='StrikeOne')

        with source_conn.cursor() as src_cursor, target_conn.cursor() as tgt_cursor:
            # Disable foreign key checks temporarily
            tgt_cursor.execute("SET foreign_key_checks = 0")

            src_cursor.execute("SHOW TABLES")
            tables = [row[0] for row in src_cursor.fetchall()]

            for table in tables:
                # Check if the table already exists in StrikeOne
                tgt_cursor.execute(f"SHOW TABLES LIKE '{table}'")
                exists = tgt_cursor.fetchone()
                if not exists:
                    print(f"Copying table: {table}")
                    # Create the table structure
                    src_cursor.execute(f"SHOW CREATE TABLE {table}")
                    create_stmt = src_cursor.fetchone()[1]
                    tgt_cursor.execute(create_stmt)

                    # Copy over the data
                    src_cursor.execute(f"SELECT * FROM {table}")
                    rows = src_cursor.fetchall()

                    if rows:
                        src_cursor.execute(f"SHOW COLUMNS FROM {table}")
                        columns = [col[0] for col in src_cursor.fetchall()]
                        columns_str = ", ".join(f"`{col}`" for col in columns)
                        values_placeholder = ", ".join(["%s"] * len(columns))
                        insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({values_placeholder})"
                        tgt_cursor.executemany(insert_query, rows)
                        print(f"Inserted {len(rows)} rows into {table}")

            # Re-enable foreign key checks
            tgt_cursor.execute("SET foreign_key_checks = 1")
        
        target_conn.commit()
        print("Baseball tables copied into StrikeOne!")

    except pymysql.MySQLError as e:
        print(f"Error during baseball DB sync: {e}")

    finally:
        source_conn.close()
        target_conn.close()



def create_app():
    """Create and configure the Flask app."""
    # First ensure the database exists
    create_database()

    app = Flask(__name__)

    # Configure the database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://web:mypass@localhost/StrikeOne'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'super_secret_key'

    # Initialize the database with the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'routes.login'

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
             hashed_password = bcrypt.generate_password_hash('adminpassword').decode('utf-8')  # Use bcrypt here
             new_admin = User(
                  username='admin',
                  password=hashed_password,
                  is_admin=True,
                  is_banned=False
            )
             db.session.add(new_admin)
             db.session.commit()
             print("Admin account created.")
        else:
            print("Admin account already exists.")
        
        print ("copying baseball tables")
        copy_baseball_tables()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
