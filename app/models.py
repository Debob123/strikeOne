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
    question = db.Column(db.String(255), nullable=False)
    query = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<TriviaQuestion {self.question_id}>'

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
    

class Batting(db.Model):
    __tablename__ = 'batting'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(16), nullable=False)    # Player ID
    year_id = db.Column(db.Integer, nullable=False)          # Year
    team_id = db.Column(db.String(8), nullable=False)        # Team ID
    games_played = db.Column(db.Integer, nullable=False)     # Games played
    at_bats = db.Column(db.Integer, nullable=False)          # At-bats
    runs = db.Column(db.Integer, nullable=False)             # Runs
    hits = db.Column(db.Integer, nullable=False)             # Hits
    doubles = db.Column(db.Integer, nullable=False)          # Doubles
    triples = db.Column(db.Integer, nullable=False)          # Triples
    home_runs = db.Column(db.Integer, nullable=False)        # Home runs
    rbi = db.Column(db.Integer, nullable=False)              # Runs batted in
    walks = db.Column(db.Integer, nullable=False)            # Walks
    strikeouts = db.Column(db.Integer, nullable=False)       # Strikeouts
    stolen_bases = db.Column(db.Integer, nullable=False)     # Stolen bases
    caught_stealing = db.Column(db.Integer, nullable=False)  # Caught stealing
    hbp = db.Column(db.Integer, nullable=False)              # Hit by pitch
    sac_fly = db.Column(db.Integer, nullable=False)          # Sacrifice flies

    def __repr__(self):
        return f'<Batting {self.player_id} - {self.year_id}>'




class Team(db.Model):
    __tablename__ = 'teams'

    teams_id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(3), nullable=False)  # Team ID (e.g., "BOS", "NYM")
    year_id = db.Column(db.SmallInteger, nullable=False)  # Year (e.g., 2023)
    lg_id = db.Column(db.String(2), nullable=True)  # League ID (e.g., "AL", "NL")
    div_id = db.Column(db.String(1), nullable=True)  # Division ID (e.g., "E", "W", "C")
    franch_id = db.Column(db.String(3), nullable=True)  # Franchise ID (e.g., "BOS", "NYM")
    team_name = db.Column(db.String(50), nullable=True)  # Team name (e.g., "Red Sox")
    team_rank = db.Column(db.SmallInteger, nullable=True)  # Team rank in division
    team_games = db.Column(db.SmallInteger, nullable=True)  # Games played
    team_wins = db.Column(db.SmallInteger, nullable=True)  # Wins
    team_losses = db.Column(db.SmallInteger, nullable=True)  # Losses
    team_run = db.Column(db.SmallInteger, nullable=True)  # Runs scored
    team_ab = db.Column(db.SmallInteger, nullable=True)  # At-bats
    team_hits = db.Column(db.SmallInteger, nullable=True)  # Hits
    team_2b = db.Column(db.SmallInteger, nullable=True)  # Doubles
    team_3b = db.Column(db.SmallInteger, nullable=True)  # Triples
    team_hr = db.Column(db.SmallInteger, nullable=True)  # Home runs
    team_bb = db.Column(db.SmallInteger, nullable=True)  # Walks
    team_so = db.Column(db.SmallInteger, nullable=True)  # Strikeouts
    team_sb = db.Column(db.SmallInteger, nullable=True)  # Stolen bases
    team_cs = db.Column(db.SmallInteger, nullable=True)  # Caught stealing
    team_hbp = db.Column(db.SmallInteger, nullable=True)  # Hit by pitch
    team_sac_fly = db.Column(db.SmallInteger, nullable=True)  # Sacrifice flies
    team_era = db.Column(db.Float, nullable=True)  # Earned Run Average
    team_cg = db.Column(db.SmallInteger, nullable=True)  # Complete games
    team_sho = db.Column(db.SmallInteger, nullable=True)  # Shutouts
    team_sv = db.Column(db.SmallInteger, nullable=True)  # Saves
    team_ipouts = db.Column(db.Integer, nullable=True)  # Innings pitched (outs)
    team_ha = db.Column(db.SmallInteger, nullable=True)  # Hits allowed
    team_hra = db.Column(db.SmallInteger, nullable=True)  # Home runs allowed
    team_bba = db.Column(db.SmallInteger, nullable=True)  # Walks allowed
    team_soa = db.Column(db.SmallInteger, nullable=True)  # Strikeouts allowed
    team_e = db.Column(db.SmallInteger, nullable=True)  # Errors
    team_dp = db.Column(db.SmallInteger, nullable=True)  # Double plays
    team_fp = db.Column(db.Float, nullable=True)  # Fielding percentage
    park_name = db.Column(db.String(50), nullable=True)  # Park name
    team_attendance = db.Column(db.Integer, nullable=True)  # Attendance
    team_bpf = db.Column(db.SmallInteger, nullable=True)  # Batting park factor
    team_ppf = db.Column(db.SmallInteger, nullable=True)  # Pitching park factor
    team_proj_w = db.Column(db.SmallInteger, nullable=True)  # Projected wins
    team_proj_l = db.Column(db.SmallInteger, nullable=True)  # Projected losses

    def __repr__(self):
        return f'<Team {self.team_name} ({self.year_id})>'
