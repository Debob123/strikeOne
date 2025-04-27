from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager, bcrypt
from sqlalchemy import text, func
from app.models import User, NoHitter, TriviaQuestion
from app.forms import LoginForm, RegistrationForm

from app.forms import LoginForm, RegistrationForm  # created form
from app.models import User
import random


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


# Route to display a random trivia question
import random

@bp.route('/trivia', methods=['GET', 'POST'])
@login_required
def trivia_game():
    from app.trivia import Question, generate_incorrect_answers

    if request.method == 'POST':
        # Handle answer submission
        user_input = request.form.get('answer', '').strip()

        from app.trivia.question1 import check_answer as check_answer_1
        from app.trivia.question2 import check_answer as check_answer_2

        # Assuming we are checking for questionID 1 or 2
        question_id = request.form.get('question_id')  # Get the question_id from the form or session

        if question_id == '1':
            message = check_answer_1(user_input)
        elif question_id == '2':
            message = check_answer_2(user_input)
        else:
            message = "Invalid question."

        flash(message)
        return redirect(url_for('routes.trivia_game'))

    # Otherwise, show a question
    question = db.session.query(TriviaQuestion).order_by(func.random()).first()

    if question is None:
        flash('No trivia questions found in the database!', 'danger')
        return redirect(url_for('routes.dashboard'))

    # Generate question based on questionID
    if question.question_id == 1:
        from app.trivia.question1 import generate_question1
        trivia_question, error = generate_question1(question.question)
        
        if error:
            flash(error, 'danger')
            return redirect(url_for('routes.dashboard'))
        
        question_text = trivia_question.question_text
        answers = trivia_question.correct_answers

    elif question.question_id == 2:
        from app.trivia.question2 import generate_question2
        trivia_question, error = generate_question2(question.question)
        
        if error:
            flash(error, 'danger')
            return redirect(url_for('routes.dashboard'))
        
        question_text = trivia_question.question_text
        answers = trivia_question.correct_answers
    else:
        trivia_question = question.question
        answers = []

    if answers:
        correct_answer = random.choice(answers)
    else:
        correct_answer = None

    incorrect_answers = generate_incorrect_answers(answers)
    if not incorrect_answers:
        flash("Couldn't generate enough incorrect answers.", 'danger')
        return redirect(url_for('routes.dashboard'))

    # Shuffle the answers
    all_answers = incorrect_answers + [correct_answer]  # Combine incorrect answers with correct answer
    random.shuffle(all_answers)  # Shuffle the combined list

    return render_template('trivia.html', question_text=question_text, correct_answer=correct_answer, incorrect_answers=incorrect_answers, all_answers=all_answers, question_id=question.question_id)
