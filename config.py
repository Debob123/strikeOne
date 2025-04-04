# Configuration settings (DB credentials)  
# config.py
class Config:
    MYSQL = {
        'location': 'localhost',
        'user': 'web',
        'password': 'mypass',
        'database': 'baseball'
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super_secret_key'
