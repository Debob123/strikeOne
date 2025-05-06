from sqlite3 import Cursor
from flask import session
from app import db
from sqlalchemy import text
from app.trivia import Question
from flask_login import current_user

def generate_question5(question_text):
    # Step 1: Pick a random player
    player_query = text('''
        SELECT playerID, birthCountry
        FROM people
        WHERE birthCountry IS NOT NULL
        ORDER BY RAND()
        LIMIT 1
    ''')
    player_result = db.session.execute(player_query).fetchone()
    if not player_result:
        return None, "No player with birth country found."

    player_id, birth_country = player_result

    # Step 2: Pick a team that player played on
    team_query = text('''
        SELECT DISTINCT t.teamID, t.team_name
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID
        WHERE b.playerID = :player_id
        ORDER BY RAND()
        LIMIT 1
    ''')
    team_result = db.session.execute(team_query, {'player_id': player_id}).fetchone()
    if not team_result:
        return None, "No team found for that player."

    team_id, team_name = team_result

    # Step 3: Find all players who match both the team and birth country
    answer_query = text('''
        SELECT DISTINCT p.nameFirst, p.nameLast
        FROM people p
        JOIN batting b ON p.playerID = b.playerID
        WHERE b.teamID = :team_id AND p.birthCountry = :birth_country
    ''')
    answer_results = db.session.execute(answer_query, {
        'team_id': team_id,
        'birth_country': birth_country
    }).fetchall()
    if not answer_results:
        return None, "No players found for team and birth country combination."

    answers = [f"{row[0]} {row[1]}" for row in answer_results]

    # Step 4: Store session context
    session['trivia_answer_team'] = team_name
    session['trivia_answer_teamID'] = team_id
    session['trivia_birth_country'] = birth_country

    # Step 5: Render and return the question
    rendered_text = question_text.replace("{team}", team_name).replace("{birthPlace}", birth_country)
    trivia_question = Question(rendered_text, answers)
    return trivia_question, None

def check_answer(user_input, correct_answer):
    if not user_input:
        return "You must enter a player's name."
    parts = user_input.strip().lower().split()
    if len(parts) == 2:
        first_name = parts[0]
        last_name = parts[1]

    elif len(parts) == 3:
        # Try combining first two as first name
        first_try = f"{parts[0]} {parts[1]}"
        Cursor.execute("SELECT COUNT(*) FROM people WHERE nameFirst = %s", (first_try,))
        if Cursor.fetchone()[0] > 0:
            first_name = first_try
            last_name = parts[2]
        
        second_try = f"{parts[1]} {parts[2]}"
        Cursor.execute("SELECT COUNT(*) FROM people WHERE nameLast = %s", (second_try,))
        if Cursor.fetchone()[0] > 0:
            last_name = second_try
        
        elif len(parts) == 4:
            first_name = f"{parts[0]} {parts[1]}"
            last_name = f"{parts[2]} {parts[3]}"
        
        else:
             return "Please enter both a first and last name."


    player_query = text('''
        SELECT playerID FROM people
        WHERE LOWER(nameFirst) = :first_name AND LOWER(nameLast) = :last_name
    ''')
    result = db.session.execute(player_query, {
        'first_name': first_name,
        'last_name': last_name
    }).fetchone()
    if not result:
        return f"No player found with the name {first_name.title()} {last_name.title()}."

    submitted_player_id = result[0]

    # Retrieve context
    team_id = session.get('trivia_answer_teamID')
    birth_country = session.get('trivia_birth_country')
    team_name = session.get('trivia_answer_team')

    if not team_id or not birth_country or not team_name:
        return "Session expired or missing question data. Please try again."

    # Check team
    team_check = text('''
        SELECT 1 FROM batting
        WHERE playerID = :player_id AND teamID = :team_id
        LIMIT 1
    ''')
    if not db.session.execute(team_check, {'player_id': submitted_player_id, 'team_id': team_id}).fetchone():
        current_user.question_wrong()
        return f"Incorrect. {correct_answer.title()} was born in {birth_country}, not {first_name.title()} {last_name.title()}."

    # Check birthplace
    country_check = text('''
        SELECT 1 FROM people
        WHERE playerID = :player_id AND birthCountry = :birth_country
        LIMIT 1
    ''')
    if not db.session.execute(country_check, {'player_id': submitted_player_id, 'birth_country': birth_country}).fetchone():
        current_user.question_wrong()
        return f"Incorrect. {correct_answer.title()} was born in {birth_country}, not {first_name.title()} {last_name.title()}."

    # If both conditions met
    current_user.question_right()
    return f"Correct! {first_name.title()}{last_name.title()}played for {team_name} and was born in {birth_country}."

    