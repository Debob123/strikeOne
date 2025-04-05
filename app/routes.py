from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db, login_manager
from app.forms import LoginForm  # created form

bp = Blueprint('routes', __name__)

@bp.route('/')
def homepage():
    return render_template('homepage.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_banned:
                flash('Your account has been banned.')
                return redirect(url_for('routes.login'))
            login_user(user)
            return redirect(url_for('routes.homepage'))  # Redirect to homepage after login
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))  # Redirect to login page after logout
