 # Authentication handling  

# app/models.py
from app import db
from app import bcrypt

class User(db.Model):
    __tablename__ = 'accounts'

    LoginID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # or False based on your use case
    is_authenticated = db.Column(db.Boolean, default=True)  # Default to True if authenticated
    is_anonymous = db.Column(db.Boolean, default=False)  # Default to False for non-anonymous users
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    
    def get_id(self):
        return str(self.LoginID) 
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash the password and store it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password, password)
    

# --------------------------
# No-Hitter Model
# --------------------------
class NoHitter(db.Model):
    __tablename__ = 'nohitter'

    id = db.Column(db.Integer, primary_key=True)
    winning_team = db.Column(db.String(64), nullable=False)
    losing_team = db.Column(db.String(64), nullable=False)
    winning_pitchers = db.Column(db.Integer, nullable=False)
    losing_pitchers = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<NoHitter {self.id}: {self.winning_team} vs {self.losing_team}>'
