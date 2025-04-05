# config.py

class Config:
    # Database configuration
    MYSQL = {
        'location': 'localhost',
        'user': 'web',
        'password': 'mypass',
        'database': 'StrikeOne'
    }

    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL['user']}:{MYSQL['password']}@{MYSQL['location']}/{MYSQL['database']}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable Flask-SQLAlchemy modification tracking

    # Secret key for sessions and other encryption needs
    SECRET_KEY = 'super_secret_key'
