import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sqlalchemy import func
from app.csi3335 import mysql
from app.csv_import import import_nohitters_from_csv
import os
from werkzeug.security import generate_password_hash
from app import csi3335
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
            host=mysql['host'],
            user=mysql['user'],
            password=mysql['password']
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
        source_conn = pymysql.connect(host=mysql['host'], user=mysql['user'], password=mysql['password'],database='baseball')
        target_conn = pymysql.connect(host=mysql['host'], user=mysql['user'], password=mysql['password'],database='StrikeOne')

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


def set_divisions_extended():
    # Database connection
    target_conn = pymysql.connect(
        host=mysql['host'],
        user=mysql['user'],
        password=mysql['password'],
        database='StrikeOne',
        autocommit=True  # Important for executing multiple statements
    )

    cursor = target_conn.cursor()

    file_path = './app/static/divisionsExtended.txt'

    try:
        with open(file_path, 'r') as file:
            # Read the entire file content
            sql_script = file.read()

            # Split the script into individual statements (semicolon separated)
            sql_commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]

            # Execute each command
            for command in sql_commands:
                try:
                    cursor.execute(command)
                except pymysql.Error as e:
                    print(f"Error executing command: {command[:50]}...")
                    print(f"Database error: {e}")


    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close connections
        cursor.close()
        target_conn.close()


def create_app():
    """Create and configure the Flask app."""
    # First ensure the database exists
    create_database()

    app = Flask(__name__)

    # Configure the database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + mysql['user'] + ':' + mysql['password'] +'@localhost/StrikeOne'
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
    from app.models import User, NoHitter, TriviaQuestion  
    """Create tables and insert the admin account if it doesn't already exist."""
    with app.app_context():
        db.create_all()

        # Admin account setup
        admin_account = User.query.filter_by(username='admin').first()
        if admin_account is None:
            hashed_password = bcrypt.generate_password_hash('adminpassword').decode('utf-8')
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
        
        print("Copying baseball tables")
        copy_baseball_tables()
        set_divisions_extended()

        # NoHitter table CSV import
        if NoHitter.query.count() == 0:
            csv_path = os.path.join(os.path.dirname(__file__), 'static', 'NoHitters-Pitching.csv')
            import_nohitters_from_csv(csv_path)
        else:
            print("NoHitter table already contains data.")

        # TriviaQuestion CSV import
        if db.session.query(func.count(TriviaQuestion.question_id)).scalar() == 0:
            csv_path = os.path.join(os.path.dirname(__file__), 'static', 'triviaQuestions.csv')
            from app.trivia import import_trivia_questions_from_csv
            import_trivia_questions_from_csv(csv_path)
        else:
            print("TriviaQuestion table already contains data.")


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
