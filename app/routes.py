# app/routes.py
from flask import Blueprint, current_app

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return 'Welcome :)'

@bp.route('/test-db')
def test_db():
    try:
        db = current_app.extensions['sqlalchemy'].db
        result = db.session.execute('SELECT 1').scalar()
        return f'Database connection test successful. Result: {result}'
    except Exception as e:
        return f'Database connection failed: {str(e)}'
