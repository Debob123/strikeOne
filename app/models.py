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
    


class TriviaQuestion(db.Model):
    __tablename__ = 'trivia_questions'

    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    query = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<TriviaQuestion {self.question_id}: {self.question[:50]}...>'

# --------------------------
# No-Hitter Model
# --------------------------
class NoHitter(db.Model):
    __tablename__ = 'nohitter'

    id = db.Column(db.Integer, primary_key=True)
    gid = db.Column(db.String(16), nullable=False)           # Game ID
    pitcher_id = db.Column(db.String(16), nullable=False)
    teamID = db.Column(db.String(8), nullable=False)
    oppID = db.Column(db.String(8), nullable=False)
    date = db.Column(db.String(16), nullable=False)
    site = db.Column(db.String(16), nullable=True)
    vishome = db.Column(db.String(1), nullable=False)        # v = visitor, h = home

    p_ipouts = db.Column(db.Integer, nullable=False)         # Pitching outs recorded
    p_bfp = db.Column(db.Integer, nullable=True)             # Batters faced
    p_h = db.Column(db.Integer, nullable=False)              # Hits allowed (0 in a no-hitter)
    p_hr = db.Column(db.Integer, nullable=True)              # Home runs allowed
    p_r = db.Column(db.Integer, nullable=True)               # Runs allowed
    p_er = db.Column(db.Integer, nullable=True)              # Earned runs
    p_w = db.Column(db.Integer, nullable=True)               # Walks
    p_k = db.Column(db.Integer, nullable=True)               # Strikeouts
    p_hbp = db.Column(db.Integer, nullable=True)             # Hit by pitch
    p_wp = db.Column(db.Integer, nullable=True)              # Wild pitches
    p_gs = db.Column(db.Integer, nullable=True)              # Game started
    p_cg = db.Column(db.Integer, nullable=True)              # Complete game
    team_win = db.Column(db.Boolean, nullable=False)         # True if pitcher's team won
    yearID = db.Column(db.Integer, nullable = True)


    def __repr__(self):
        return f'<NoHitter {self.id}: {self.pitcher_id} ({self.team}) vs {self.opp} on {self.date}>'
    

class TriviaQuestion(db.Model):
    __tablename__ = 'trivia_questions'

    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    query = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<TriviaQuestion {self.question_id}: {self.question[:50]}...>'

