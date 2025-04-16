from flask import session
from app import db
from sqlalchemy import func

def generate_question1(question_text):
    # Step 1: Find a player who played for at least two different teams
    subquery = (
        db.session.query(Batting.playerID)
        .group_by(Batting.playerID)
        .having(func.count(func.distinct(Batting.teamID)) >= 2)
        .subquery()
    )

    # Step 2: Randomly select one such player
    random_player_id = db.session.query(subquery).order_by(func.random()).first()
    if not random_player_id:
        return None, "Couldn't find a suitable player."

    random_player_id = random_player_id[0]

    # Step 3: Get two distinct teamIDs the player played for
    team_ids = (
        db.session.query(Batting.teamID)
        .filter(Batting.playerID == random_player_id)
        .distinct()
        .order_by(func.random())
        .limit(2)
        .all()
    )

    if len(team_ids) < 2:
        return None, "Couldn't find two distinct teams for the player."

    team_id_1, team_id_2 = team_ids[0][0], team_ids[1][0]

    # Step 4: Lookup team names from Teams table
    team1 = db.session.query(Teams.team_name).filter(Teams.teamID == team_id_1).first()
    team2 = db.session.query(Teams.team_name).filter(Teams.teamID == team_id_2).first()

    if not team1 or not team2:
        return None, "Team name lookup failed."

    team_name_1 = team1[0]
    team_name_2 = team2[0]

    # Step 5: Substitute into question text
    rendered_text = question_text.replace("{teamA}", team_name_1).replace("{teamB}", team_name_2)

    # Optional: Store values in session if needed for answer validation
    session['trivia_answer_playerID'] = random_player_id
    session['trivia_teamA'] = team_id_1
    session['trivia_teamB'] = team_id_2

    return rendered_text, None
