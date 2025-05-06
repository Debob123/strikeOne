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
from app.family_feud import generate_feud_round
import app.baseball
from app.baseball import baseball_questions, first_base, team1_score

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
            if user.is_admin:
                return redirect(url_for('routes.admin_dashboard'))
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
    for team in teams:
        print(f"Team: {team['name']}")

    return render_template('dashboard.html', teams=teams)

@bp.route('/nohitters/<team>')
def show_nohitters(team):
    # Query for won no-hitters with the number of pitchers involved
    nhQueryWon = text("""
    SELECT DISTINCT 
        DATE_FORMAT(STR_TO_DATE(n.date, '%Y%m%d'), '%m/%d/%Y') AS game_date,
        opp.team_name AS opponent_team,
        COUNT(DISTINCT n.pitcher_id) AS pitchers_involved
    FROM nohitter n
    JOIN teams opp ON n.oppID = opp.teamID
    WHERE n.teamID = :teamID AND n.team_win = 1
    GROUP BY n.date, opp.team_name
    ORDER BY n.date;
    """)

    # Query for lost no-hitters with the number of pitchers involved
    nhQueryLost = text("""
    SELECT DISTINCT 
        DATE_FORMAT(STR_TO_DATE(n.date, '%Y%m%d'), '%m/%d/%Y') AS game_date,
        opp.team_name AS opponent_team,
        COUNT(DISTINCT n.pitcher_id) AS pitchers_involved
    FROM nohitter n
    JOIN teams opp ON n.oppID = opp.teamID
    WHERE n.teamID = :teamID AND n.team_win = 0
    GROUP BY n.date, opp.team_name
    ORDER BY n.date;
    """)

    # Execute both queries
    resultWon = db.session.execute(nhQueryWon, {'teamID': team})
    no_hitters_won = resultWon.fetchall()

    resultLost = db.session.execute(nhQueryLost, {'teamID': team})
    no_hitters_lost = resultLost.fetchall()

    # Fetch the team name for display
    teamQuery = db.session.execute(
        text("SELECT team_name FROM teams WHERE teamID = :teamID"), {'teamID': team})
    team_name = teamQuery.fetchone()[0]

    # Fetch all teams for the dropdown or other display
    teamQueryAll = db.session.execute(
        text('SELECT DISTINCT team_name, teamID FROM teams ORDER BY team_name'))
    teams = [{'name': row.team_name, 'id': row.teamID} for row in teamQueryAll]

    return render_template('nohitters_team.html', 
                           no_hitters_won=no_hitters_won, 
                           no_hitters_lost=no_hitters_lost, 
                           team=team, 
                           teams=teams, 
                           name=team_name)




# Route to display a random trivia question
import random
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.sql import func
from app import db
from app.models import TriviaQuestion
from app.trivia import (
    generate_incorrect_answers,
    question1, question2, question3, question4,
    question5, question6, question7, question8
)
from app.routes import bp

@bp.route('/trivia', methods=['GET', 'POST'])
@login_required
def trivia_game():
    check_answer_map = {
        '1': question1.check_answer,
        '2': question2.check_answer,
        '3': question3.check_answer,
        '4': question4.check_answer,
        '5': question5.check_answer,
        '6': question6.check_answer,
        '7': question7.check_answer,
        '8': question8.check_answer,
    }

    generate_question_map = {
        1: question1.generate_question1,
        2: question2.generate_question2,
        3: question3.generate_question3,
        4: question4.generate_question4,
        5: question5.generate_question5,
        6: question6.generate_question6,
        7: question7.generate_question7,
        8: question8.generate_question8,
    }

    if request.method == 'POST':
        user_input = request.form.get('answer', '').strip()
        question_id = request.form.get('question_id')
        correct_answer = request.form.get('correct_answer', '').strip()

        if not correct_answer or not question_id:
            flash("Missing form data.", "danger")
            return redirect(url_for('routes.trivia_game'))

        check_func = check_answer_map.get(question_id)
        if not check_func:
            flash("Invalid question.", "danger")
            return redirect(url_for('routes.trivia_game'))

        message = check_func(user_input, correct_answer)
        flash(message)
        return redirect(url_for('routes.trivia_game'))

    # GET request: fetch a valid question
    for _ in range(10):  # retry a few times in case of invalid/missing questions
        question = db.session.query(TriviaQuestion).order_by(func.random()).first()

        if not question:
            flash('No trivia questions found in the database!', 'danger')
            return redirect(url_for('routes.dashboard'))

        generate_func = generate_question_map.get(question.question_id)
        if not generate_func:
            continue

        trivia_question, error = generate_func(question.question)
        if not error and trivia_question:
            break
    else:
        flash('Failed to generate a trivia question.', 'danger')
        return redirect(url_for('routes.dashboard'))

    question_text = trivia_question.question_text
    answers = trivia_question.correct_answers
    correct_answer = random.choice(answers) if answers else None
    incorrect_answers = generate_incorrect_answers(answers)

    if not incorrect_answers or not correct_answer:
        flash("Couldn't generate enough incorrect answers.", 'danger')
        return redirect(url_for('routes.dashboard'))

    all_answers = incorrect_answers + [correct_answer]
    random.shuffle(all_answers)

    return render_template(
        'trivia.html',
        question_text=question_text,
        correct_answer=correct_answer,  # passed into form as hidden input
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
    app.jeopardy.categories =  app.jeopardy.store_question_answers()
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
def submitJeopardy():
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


@bp.route('/familyFeud')
@login_required
def family_feud():
    question, answers = generate_feud_round()
    return render_template(
        'family_feud.html',
        question=question,
        answers=answers
    )

@bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('routes.dashboard'))

    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@bp.route('/admin/ban/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('routes.dashboard'))

    user = User.query.get(user_id)
    if user.is_admin:
        flash('Cannot ban an admin.', 'danger')
    else:
        user.is_banned = True
        db.session.commit()
        flash(f"Banned user: {user.username}", 'success')

    return redirect(url_for('routes.admin_dashboard'))


@bp.route('/submitBaseball')
def submitBaseball():
    answer = request.args.get('answer')
    type = request.args.get('type')
    results = []

    for item in app.baseball.questions:
        if type in item:

            results = app.baseball.questions[type]['answers']


    correct = answer.strip().lower() in [str(r).strip().lower() for r in results]

    # You could add more feedback here
    if correct:
        response = {"result": "Correct", "correct_answer": None}  # No need to show the correct answer if they're right
    else:
        response = {"result": "Wrong", "correct_answer": results[0]}  # Show the first correct answer if they're wrong

    return jsonify(response)


@bp.route('/baseball/get_questions', methods=['GET'])
@login_required
def baseball_get_question():
    questions = {
        'first_base': {
            "question": "",
            "answers": [],
        },
        'second_base': {
            "question": "",
            "answers": [],
        },
        'third_base': {
            "question": "",
            "answers": [],
        },
        'home_run': {
            "question": "",
            "answers": [],
        },
    }

    baseball_questions = app.baseball.baseball_questions
    for base in app.baseball.baseball_questions:
        print(base)
        if base == 'first_base':
            question = ""
            # print(questions['first_base'])
            fortnite = []
            while not fortnite:
                gen = len(baseball_questions[base]['questions'])
                index = random.randint(0, gen - 1)

                yearid = 2000 + random.randint(1, 23)
                teams = db.session.execute(
                    text(
                        "SELECT distinct team_name FROM teams WHERE yearid = {yearid}".format(yearid=yearid))).fetchall()

                teams = [team[0] for team in teams]

                team1 = random.choice(teams)

                question = baseball_questions[base]['questions'][index].format(yearid=yearid,team1 =team1)
                sql = baseball_questions[base]['sql'][index].format(yearid=yearid,team1 =team1)

                fortnite = db.session.execute(text(sql)).fetchall()
                fortnite = [row[0] for row in fortnite if row[0] is not None]


            questions['first_base']['question'] = question
            questions['first_base']['answers'] = fortnite


        elif base == 'second_base':
            question = ""
            fortnite = []
            gen = len(baseball_questions['second_base']['questions'])
            index = random.randint(0, gen - 1)
            while not fortnite:


                yearid = 2000 + random.randint(1, 23)

                teams = db.session.execute(
                    text(
                        "SELECT distinct team_name FROM teams".format(
                            yearid=yearid))).fetchall()

                teams = [team[0] for team in teams]
                team1 = random.choice(teams)
                team2 = team1
                while team1 == team2:
                    team2 = random.choice(teams)

                team1 = team1.replace("'", "''")
                team2 = team2.replace("'", "''")
                sql = 'Select distinct awardid from awards;'
                awardid = db.session.execute(text(sql)).fetchall()
                awardid = [awardid[0] for awardid in awardid]

                award1 = random.choice(awardid)

                question = baseball_questions['second_base']['questions'][index].format(yearid=yearid, team1=team1,
                                                                                        team2=team2, award1=award1)
                sql = baseball_questions['second_base']['sql'][index].format(yearid=yearid, team1=team1, team2=team2,
                                                                             award1=award1)

                fortnite = db.session.execute(text(sql)).fetchall()
                fortnite = [row[0] for row in fortnite if row[0] is not None]

            questions['second_base']['question'] = question
            questions['second_base']['answers'] = fortnite
        elif base == 'third_base':
            question = ""
            fortnite = []
            gen = len(baseball_questions['third_base']['questions'])
            index = random.randint(0, gen - 1)
            while not fortnite:


                yearid = 2000 + random.randint(1, 23)

                teams = db.session.execute(
                    text(
                        "SELECT distinct team_name FROM teams".format(
                            yearid=yearid))).fetchall()

                teams = [team[0] for team in teams]
                team1 = random.choice(teams)
                team2 = team1
                while team1 == team2:
                    team2 = random.choice(teams)

                team1 = team1.replace("'", "''")
                team2 = team2.replace("'", "''")

                question = baseball_questions['third_base']['questions'][index].format(yearid=yearid, team1=team1,
                                                                                       team2=team2)
                sql = baseball_questions['third_base']['sql'][index].format(yearid=yearid, team1=team1, team2=team2)

                fortnite = db.session.execute(text(sql)).fetchall()
                fortnite = [row[0] for row in fortnite if row[0] is not None]

            questions['third_base']['question'] = question
            questions['third_base']['answers'] = fortnite
        elif base == 'home_run':
            question = ""
            fortnite = []
            gen = len(baseball_questions[base]['questions'])
            index = random.randint(0, gen - 1)
            while not fortnite:
                yearid = 2000 + random.randint(1, 23)

                teams = db.session.execute(
                    text(
                        "SELECT distinct team_name FROM teams".format(
                            yearid=yearid))).fetchall()

                teams = [team[0] for team in teams]
                team1 = random.choice(teams)
                team2 = team1
                team3 = team1
                while team1 == team2 or team2 == team3 or team1 == team3:
                    team2 = random.choice(teams)
                    team3 = random.choice(teams)

                team1 = team1.replace("'", "''")
                team2 = team2.replace("'", "''")
                team3 = team3.replace("'", "''")

                sql = 'Select distinct awardid from awards;'
                awardid = db.session.execute(text(sql)).fetchall()
                awardid = [awardid[0] for awardid in awardid]

                award1 = random.choice(awardid)

                award2 = award1
                while award1 == award2:
                    award2 = random.choice(awardid)


                question = baseball_questions['home_run']['questions'][index].format(yearid=yearid, team1=team1,
                                                                                    team2=team2, team3=team3,
                                                                                    award1=award1,
                                                                                    award2=award2)
                sql = baseball_questions['home_run']['sql'][index].format(yearid=yearid, team1=team1, team2=team2,
                                                                         team3=team3, award1=award1, award2=award2)

                fortnite = db.session.execute(text(sql)).fetchall()
                fortnite = [row[0] for row in fortnite if row[0] is not None]

            questions['home_run']['question'] = question
            questions['home_run']['answers'] = fortnite


    app.baseball.questions = questions
    questions = {
        'first_base': "",
        'second_base': "",
        'third_base': "",
        'home_run': "",
    }
    for question in app.baseball.questions:
        questions[question] = app.baseball.questions[question]['question']

    print(str(app.baseball.questions))
    return jsonify({'questions': questions})


@bp.route('/baseball')
@login_required
def baseball():
    app.baseball.first_base = 0
    app.baseball.second_base = 0
    app.baseball.third_base = 0

    app.baseball.team1_score = 0
    app.baseball.team2_score = 0

    app.baseball.outs = 0

    app.baseball.inning = 1

    app.baseball.teamUp = "Team 1"

    video_name = "hitThird_loadedNone"  # or dynamically pass a value
    video_url = url_for('static', filename=f'videos/{video_name}.mov')
    app.baseball.baseball_questions = app.baseball.store_question_answers()

    return render_template('baseball.html',first_base=0, second_base=0, third_base=0,team1_score=0, team2_score=0, outs=0, inning=1,video_url=video_url)


