from flask import session
from app import db
from sqlalchemy import text
from app.trivia import Question
from flask_login import current_user

def generate_question4(question_text):
    # Step 1: Pick a random player who won an award and played for a team in a specific year
    query = text('''
        SELECT DISTINCT p.playerID, p.nameFirst, p.nameLast, a.awardID, t.team_Name, a.yearID
        FROM people p
        JOIN awards a ON p.playerID = a.playerID
        JOIN batting b ON p.playerID = b.playerID
        JOIN teams t ON b.teamID = t.teamID AND b.yearID = a.yearID
        WHERE a.yearID = b.yearID
        ORDER BY RAND()
        LIMIT 1;
    ''')

    result = db.session.execute(query)
    data = result.fetchone()

    if not data:
        print("Error: Couldn't find a player with an award and a team.")
        return None, "Couldn't find a player with an award and a team."

    player_id, first_name, last_name, award_id, team_name, year_id = data

    # Step 2: Fill in the question template
    rendered_text = question_text.replace("{team}", team_name).replace("{award}", award_id)

    # Step 3: Create answers list
    answers = [f"{first_name} {last_name}"]

    # Step 4: Create Question object
    trivia_question = Question(rendered_text, answers)

    # Step 5: Store correct player in session
    session['trivia_answer_playerID'] = player_id

    return trivia_question, None


def check_answer(user_input):
    if not user_input:
        return "You must enter a player's name."

    parts = user_input.strip().lower().split()
    if len(parts) != 2:
        return "Please enter both a first and last name."

    first_name, last_name = parts

    # Step 1: Look up player ID
    query = text('''
        SELECT playerID
        FROM people
        WHERE LOWER(nameFirst) = :first_name AND LOWER(nameLast) = :last_name
    ''')
    result = db.session.execute(query, {'first_name': first_name, 'last_name': last_name})
    row = result.fetchone()

    if not row:
        return f"No player found with the name {first_name.title()} {last_name.title()}."

    submitted_player_id = row[0]

    # Step 2: Get correct answer from session
    correct_player_id = session.get('trivia_answer_playerID')

    if not correct_player_id:
        return "Session expired or invalid question context. Please try again."

    # Step 3: Compare
    if submitted_player_id == correct_player_id:
        current_user.question_right()
        return f"Correct! {first_name.title()} {last_name.title()} won the {award_id} award while playing for {team_name} in {year_id}."
    else:
        current_user.question_wrong()
        return f"Incorrect. {first_name.title()} {last_name.title()} was not the award-winning player in question."



def check_answer(user_input):
    if not user_input:
        return "You must enter a player's name."

    parts = user_input.strip().lower().split()
    if len(parts) != 2:
        return "Please enter both a first and last name."

    first_name, last_name = parts

    # Step 1: Look up player ID
    query = text('''
        SELECT playerID, nameFirst, nameLast
        FROM people
        WHERE LOWER(nameFirst) = :first_name AND LOWER(nameLast) = :last_name
    ''')
    result = db.session.execute(query, {'first_name': first_name, 'last_name': last_name})
    row = result.fetchone()

    if not row:
        return f"No player found with the name {first_name.title()} {last_name.title()}."

    submitted_player_id, db_first_name, db_last_name = row

    # Step 2: Get correct answer details from session
    correct_answer = session.get('trivia_answer')
    
    if not correct_answer:
        return "Session expired or invalid question context. Please try again."

    correct_player_id = correct_answer.get('player_id')
    correct_award = correct_answer.get('award')
    correct_team = correct_answer.get('team')

    if not correct_player_id or not correct_award or not correct_team:
        return "Session expired or invalid question context. Please try again."

    # Step 3: Compare player ID and award/team
    if submitted_player_id == correct_player_id:
        current_user.question_right()
        return f"Correct! {db_first_name.title()} {db_last_name.title()} won the {correct_award} award while playing for {correct_team}."
    else:
        current_user.question_wrong()
        return f"Incorrect. {db_first_name.title()} {db_last_name.title()} was not the award-winning player in question."
