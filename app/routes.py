from os import replace
from urllib.parse import unquote
from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager, bcrypt
from sqlalchemy import text, func
from flask import jsonify
import random
from app.jeopardy import generate_questions
from app.jeopardy import stored_answers
from app.models import User, NoHitter, TriviaQuestion
import app.jeopardy
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
from app.trivia import generate_incorrect_answers
@bp.route('/trivia', methods=['GET', 'POST'])
@login_required
def trivia_game():
    # Map question IDs to their respective answer check functions
    check_answer_map = {
        '1': lambda ans: __import__('app.trivia.question1', fromlist=['check_answer']).check_answer(ans),
        '2': lambda ans: __import__('app.trivia.question2', fromlist=['check_answer']).check_answer(ans),
        '3': lambda ans: __import__('app.trivia.question3', fromlist=['check_answer']).check_answer(ans),
        '4': lambda ans: __import__('app.trivia.question4', fromlist=['check_answer']).check_answer(ans),
        '5': lambda ans: __import__('app.trivia.question5', fromlist=['check_answer']).check_answer(ans),
        '6': lambda ans: __import__('app.trivia.question6', fromlist=['check_answer']).check_answer(ans),
    }

    # Handle POST: user submitted an answer
    if request.method == 'POST':
        user_input = request.form.get('answer', '').strip()
        question_id = request.form.get('question_id')

        check_func = check_answer_map.get(question_id)
        if check_func:
            message = check_func(user_input)
        else:
            message = "Invalid question."

        flash(message)
        return redirect(url_for('routes.trivia_game'))

    # Handle GET: keep retrying until a valid question is generated
    generate_question_map = {
        1: lambda q: __import__('app.trivia.question1', fromlist=['generate_question1']).generate_question1(q),
        2: lambda q: __import__('app.trivia.question2', fromlist=['generate_question2']).generate_question2(q),
        3: lambda q: __import__('app.trivia.question3', fromlist=['generate_question3']).generate_question3(q),
        4: lambda q: __import__('app.trivia.question4', fromlist=['generate_question4']).generate_question4(q),
        5: lambda q: __import__('app.trivia.question5', fromlist=['generate_question5']).generate_question5(q),
        6: lambda q: __import__('app.trivia.question6', fromlist=['generate_question6']).generate_question6(q),
    }

    trivia_question = None
    error = None
    question = None

    while True:
        question = db.session.query(TriviaQuestion).order_by(func.random()).first()

        if question is None:
            flash('No trivia questions found in the database!', 'danger')
            return redirect(url_for('routes.dashboard'))

        generate_func = generate_question_map.get(question.question_id)
        if not generate_func:
            continue  # skip invalid ID

        trivia_question, error = generate_func(question.question)

        if not error and trivia_question:
            break  # success

    question_text = trivia_question.question_text
    answers = trivia_question.correct_answers
    correct_answer = random.choice(answers) if answers else None
    incorrect_answers = generate_incorrect_answers(answers)

    if not incorrect_answers:
        flash("Couldn't generate enough incorrect answers.", 'danger')
        return redirect(url_for('routes.dashboard'))

    all_answers = incorrect_answers + [correct_answer]
    random.shuffle(all_answers)

    return render_template(
        'trivia.html',
        question_text=question_text,
        correct_answer=correct_answer,
        incorrect_answers=incorrect_answers,
        all_answers=all_answers,
        question_id=question.question_id
    )
@bp.route('/jeopardy')
@login_required
def jeopardy_loading():
    return render_template('jeopardy_loading.html')

@bp.route('/jeopardy/data')
@login_required
def jeopardy():
    question = ''
    sql = ''
    app.jeopardy.stored_answers = []
    questions_text= generate_questions()

    print(str(questions_text))
    print(str(len(questions_text)))

    category = sorted(set(q['category'] for q in questions_text))
    lookup = {(q['category'], q['points']): q for q in questions_text}

    player1 = 0
    player2 = 0

    return render_template('jeopardy.html', questions_text=questions_text,
                           categories=category, lookup=lookup, player1=player1, player2=player2)




@bp.route('/submitJeopardy')
def submit():
    answer = request.args.get('answer')
    id = request.args.get('sql')
    results = []

    for item in app.jeopardy.stored_answers:
        if id in item:
            print(item)
            print(id)

            results = item[id]  # ➜ ['Hank Aaron', 'Babe Ruth']
            print(results)

    correct = answer.strip().lower() in [str(r).strip().lower() for r in results]

    return jsonify({"result": "Correct" if correct else "Wrong"})