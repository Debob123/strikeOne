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
    return redirect(url_for('routes.login'))


# Dashboard (optional landing page after login)
# Dashboard (optional landing page after login)
@bp.route('/dashboard')
def dashboard():
    # Fetch the list of teams from the database using raw SQL with text()
    result = db.session.execute(text('SELECT DISTINCT team_name FROM teams ORDER BY team_name'))
    teams = [row[0] for row in result]  # Extract team names from the query result

    # Pass the teams to the dashboard template
    return render_template('dashboard.html', teams=teams)

@bp.route('/nohitters/<team>')
def show_nohitters(team):
    # Here, you can query the database for No-Hitters for this team
    no_hitters = db.session.execute(text(f"SELECT * FROM no_hitters WHERE team_name = :team"), {'team': team})
    no_hitters_list = [row for row in no_hitters]
    return render_template('nohitters.html', no_hitters=no_hitters_list, team=team)
