from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager, bcrypt
from sqlalchemy import text
from app.models import User, NoHitter
from app.forms import LoginForm, RegistrationForm

from app.forms import LoginForm, RegistrationForm  # created form
from app.models import User


bp = Blueprint('routes', __name__)

# Home page
@bp.route('/')
def homepage():
    return render_template('dashboard.html')



# Login route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_banned:
                flash('Your account has been banned. Contact an administrator.', 'danger')
                return redirect(url_for('routes.login'))
            login_user(user)
            return redirect(url_for('routes.dashboard'))  # Redirect to dashboard after login
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)


# Registration route
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username is already taken. Please choose a different one.')
            return redirect(url_for('routes.register'))

        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!", 'success')
        return redirect(url_for('routes.login'))

    return render_template('register.html', form=form)


# Logout route
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))  # Redirect to login page after logout


@bp.route('/trivia')
@login_required 
def trivia_game():
    return render_template('trivia.html')  # you'll make this template


# Dashboard (optional landing page after login)
# Dashboard (optional landing page after login)
@bp.route('/dashboard')
def dashboard():
    result = db.session.execute(text('SELECT DISTINCT team_name, t.teamID FROM teams t RIGHT JOIN nohitter nh ON t.teamID = nh.teamID WHERE team_name IS NOT NULL ORDER BY team_name'))
    teams = [{'name': row.team_name, 'id': row.teamID} for row in result]
    return render_template('dashboard.html', teams=teams)

@bp.route('/nohitters/<team>')
def show_nohitters(team):
    # Use a parameterized query to prevent SQL injection
    nhQuery = text("SELECT pitcher_id, teamID, oppID, date, site, vishome, p_ipouts, p_bfp, p_h, p_hr, p_r, p_er, p_w, p_k, p_hbp, p_wp, p_gs, p_cg, team_win, yearID FROM nohitter WHERE teamID = :teamID")
    result = db.session.execute(nhQuery, {'teamID': team})
    no_hitters_list = result.fetchall()

    teamQuery =  db.session.execute(text('SELECT DISTINCT team_name, t.teamID FROM teams t RIGHT JOIN nohitter nh ON t.teamID = nh.teamID WHERE team_name IS NOT NULL ORDER BY team_name'))
    teams = [{'name': row.team_name, 'id': row.teamID} for row in teamQuery]

    return render_template('nohitters_team.html', no_hitters=no_hitters_list, team=team, teams=teams)

