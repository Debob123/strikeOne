from sqlite3 import Cursor
from flask import session
from app import db
from sqlalchemy import text, func
import random
from app.models import User
from app.trivia import Question
from flask_login import current_user



def generate_question1(question_text):
    # Step 1: Find a player who played for at least two different teams
    query = text('''
        SELECT playerID
        FROM batting
        GROUP BY playerID
        HAVING COUNT(DISTINCT teamID) >= 2
    ''')
    result = db.session.execute(query)
    players = result.fetchall()

    if not players:
        print("Error: Couldn't find a suitable player.")
        return None, "Couldn't find a suitable player."

    # Step 2: Randomly select one such player
    random_player_id = random.choice(players)[0]

    # Step 3: Get two distinct teamIDs the player played for
    query = text('''
        SELECT DISTINCT teamID
        FROM batting
        WHERE playerID = :player_id
        ORDER BY RAND()
        LIMIT 2
    ''')
    result = db.session.execute(query, {'player_id': random_player_id})
    team_ids = result.fetchall()

    if len(team_ids) < 2:
        print("Error: Couldn't find two distinct teams for the player.")
        return None, "Couldn't find two distinct teams for the player."

    team_id_1, team_id_2 = team_ids[0][0], team_ids[1][0]

    # Step 4: Lookup team names from Teams table
    query = text('''
        SELECT team_name
        FROM teams
        WHERE teamID = :team_id
    ''')
    result1 = db.session.execute(query, {'team_id': team_id_1})
    result2 = db.session.execute(query, {'team_id': team_id_2})

    team_name_1 = result1.fetchone()
    team_name_2 = result2.fetchone()

    if not team_name_1 or not team_name_2:
        print("Error: Team name lookup failed.")
        return None, "Team name lookup failed."

    team_name_1 = team_name_1[0]
    team_name_2 = team_name_2[0]

    # Step 5: Substitute into question text
    rendered_text = question_text.replace("{teamA}", team_name_1).replace("{teamB}", team_name_2)

    # Step 6: Get players who played for both teams
    query = text('''
        SELECT nameFirst, nameLast
        FROM people
        WHERE playerID IN (
            SELECT playerID
            FROM batting
            WHERE teamID IN (:team_id_1, :team_id_2)
            GROUP BY playerID
            HAVING COUNT(DISTINCT teamID) = 2
        )
    ''')
    result = db.session.execute(query, {'team_id_1': team_id_1, 'team_id_2': team_id_2})
    player_names = result.fetchall()

    # Step 7: Prepare answers list
    answers = [f"{first} {last}" for first, last in player_names]

    # Step 8: Create and return the Question object
    trivia_question = Question(rendered_text, answers)

    # Optional: Store values in session if needed for answer validation
    session['trivia_answer_playerID'] = random_player_id
    session['trivia_teamA'] = team_id_1
    session['trivia_teamB'] = team_id_2

    return trivia_question, None



def check_answer(user_input, correct_answer):
    if not user_input:
        return "You must enter a player's name."
    
    user = current_user
    # Split first and last name
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


    # Step 1: Find the playerID that matches the given name
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

    # Step 2: Get the teamIDs from the session
    teamA = session.get('trivia_teamA')
    teamB = session.get('trivia_teamB')

    if not teamA or not teamB:
        return "Session expired or invalid question context. Please try again."

    # Step 3: Check if player played for both teams
    query = text('''
        SELECT DISTINCT teamID
        FROM batting
        WHERE playerID = :player_id
    ''')
    result = db.session.execute(query, {'player_id': submitted_player_id})
    teams_played_for = {row[0] for row in result.fetchall()}

    if teamA in teams_played_for and teamB in teams_played_for:
        current_user.question_right()
        return f"Correct! {first_name.title()} {last_name.title()} played for both teams."
    else:
        current_user.question_wrong()
        return f"Incorrect. {correct_answer.title()} played for both teams, not {first_name.title()} {last_name.title()}."