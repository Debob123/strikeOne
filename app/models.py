 # Authentication handling  

# app/models.py
from app import db

class User(db.Model):
    __tablename__ = 'accounts'

    LoginID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
