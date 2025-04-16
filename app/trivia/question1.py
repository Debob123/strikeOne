from flask import session
from app import db
from sqlalchemy import text
import random

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

    # Optional: Store values in session if needed for answer validation
    session['trivia_answer_playerID'] = random_player_id
    session['trivia_teamA'] = team_id_1
    session['trivia_teamB'] = team_id_2

    return rendered_text, None
