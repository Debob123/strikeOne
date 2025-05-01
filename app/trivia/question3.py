from flask import session
from app import db
from sqlalchemy import text
from app.trivia import Question
from flask_login import current_user
import random

def generate_question3(question_text):
    # Step 1: Pick a random team and year from the database
    query = text('''
        SELECT DISTINCT team_name, yearID
        FROM teams
        ORDER BY RAND()
        LIMIT 1;
    ''')

    result = db.session.execute(query)
    team_data = result.fetchone()

    if not team_data:
        print("Error: Couldn't find a team and year.")
        return None, "Couldn't find a team and year."

    team_name, yearID = team_data

    # Step 2: Find the player with the most home runs for that team and year
    query = text('''
        SELECT playerID, b_HR 
        FROM batting 
        JOIN teams ON batting.teamID = teams.teamID 
        WHERE teams.team_name = :team
        AND batting.yearID = :yearID
        ORDER BY b_HR DESC
        LIMIT 1;
    ''')
    result = db.session.execute(query, {'team': team_name, 'yearID': yearID})
    player_data = result.fetchone()

    if not player_data:
        print("Error: Couldn't find a player with the most home runs.")
        return None, "Couldn't find a player with the most home runs."

    player_id = player_data[0]
    home_runs = player_data[1]

    # Step 3: Get the player's name
    query = text('''
        SELECT nameFirst, nameLast
        FROM people
        WHERE playerID = :player_id
    ''')
    result = db.session.execute(query, {'player_id': player_id})
    player_name = result.fetchone()

    if not player_name:
        print("Error: Player name lookup failed.")
        return None, "Player name lookup failed."

    first_name, last_name = player_name

    # Step 4: Substitute into question text
    rendered_text = question_text.replace("{team}", team_name).replace("{yearID}", str(yearID))

    # Step 5: Prepare answers list
    answers = [f"{first_name} {last_name}"]

    # Step 6: Create and return the Question object
    trivia_question = Question(rendered_text, answers)

    # Optional: Store playerID in session for answer validation
    session['trivia_answer_playerID'] = player_id

    return trivia_question, None


def check_answer(user_input):
    if not user_input:
        return "You must enter a player's name."

    # Split first and last name
    parts = user_input.strip().lower().split()
    if len(parts) != 2:
        return "Please enter both a first and last name."

    first_name, last_name = parts

    # Step 1: Find playerID for the submitted answer
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

    # Step 2: Retrieve correct playerID from session
    correct_player_id = session.get('trivia_answer_playerID')

    if not correct_player_id:
        return "Session expired or invalid question context. Please try again."

    # Step 3: Compare playerIDs
    if submitted_player_id == correct_player_id:
        current_user.question_right()
        return f"Correct! {first_name.title()} {last_name.title()} hit the most home runs for the team in the selected year."
    else:
        current_user.question_wrong()
        return f"Incorrect. {first_name.title()} {last_name.title()} did not hit the most home runs."

