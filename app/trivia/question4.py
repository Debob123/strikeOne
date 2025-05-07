from flask import session
from app import db
from sqlalchemy import text
from app.trivia import Question
from flask_login import current_user

def generate_question4(question_text):
    # Step 1: Pick a random award
    award_query = text('''
        SELECT DISTINCT awardID FROM awards
        ORDER BY RAND()
        LIMIT 1
    ''')
    award_result = db.session.execute(award_query).fetchone()
    if not award_result:
        return None, "No awards found."

    award_name = award_result[0]

    # Step 2: Pick a random player who won that award
    player_query = text('''
        SELECT a.playerID, p.nameFirst, p.nameLast
        FROM awards a
        JOIN people p ON a.playerID = p.playerID
        WHERE a.awardID = :award_name
        ORDER BY RAND()
        LIMIT 1
    ''')
    player_result = db.session.execute(player_query, {'award_name': award_name}).fetchone()
    if not player_result:
        return None, "No player found who won that award."

    player_id, first_name, last_name = player_result

    # Step 3: Pick a team that the player played on
    team_query = text('''
        SELECT DISTINCT teamID FROM batting
        WHERE playerID = :player_id
        ORDER BY RAND()
        LIMIT 1
    ''')
    team_result = db.session.execute(team_query, {'player_id': player_id}).fetchone()
    if not team_result:
        return None, "No team found for that player."

    team_id = team_result[0]

    # Step 4: Convert team ID to team name (corrected column name here)
    team_name_query = text('''
        SELECT team_name FROM teams
        WHERE teamID = :team_id
        ORDER BY yearID DESC
        LIMIT 1
    ''')
    team_name_result = db.session.execute(team_name_query, {'team_id': team_id}).fetchone()
    if not team_name_result:
        return None, "Team name not found."

    team_name = team_name_result[0]

    # Step 5: Build list of all players who won that award and played on that team
    all_answers_query = text('''
        SELECT DISTINCT p.nameFirst, p.nameLast
        FROM people p
        JOIN awards a ON a.playerID = p.playerID
        JOIN batting b ON b.playerID = p.playerID
        WHERE a.awardID = :award_name AND b.teamID = :team_id
    ''')
    answer_results = db.session.execute(all_answers_query, {'award_name': award_name, 'team_id': team_id}).fetchall()
    if not answer_results:
        return None, "No players matched for answer choices."

    answers = [f"{row[0]} {row[1]}" for row in answer_results]

    # Step 6: Store correct answer context
    session['trivia_answer_award'] = award_name
    session['trivia_answer_team'] = team_name
    session['trivia_answer_teamID'] = team_id

    # Step 7: Render and return the question
    rendered_text = question_text.replace("{award}", award_name).replace("{team}", team_name)
    trivia_question = Question(rendered_text, answers)
    return trivia_question, None


def check_answer(user_input, correct_answer):
    if not user_input:
        return "You must enter a player's name."

    parts = user_input.strip().lower().split()
    if len(parts) != 2:
        return "Please enter both a first and last name."

    first_name, last_name = parts

    # Step 1: Get playerID
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

    # Step 2: Get question context
    award_name = session.get('trivia_answer_award')
    team_id = session.get('trivia_answer_teamID')
    team_name = session.get('trivia_answer_team')

    if not award_name or not team_id or not team_name:
        return "Session expired or missing question data. Please try again."

    # Step 3: Verify player won the award
    award_check_query = text('''
        SELECT 1 FROM awards
        WHERE playerID = :player_id AND awardID = :award_name
        LIMIT 1
    ''')
    award_check = db.session.execute(award_check_query, {
        'player_id': submitted_player_id,
        'award_name': award_name
    }).fetchone()
    if not award_check:
        current_user.question_wrong()
        return f"Incorrect. {correct_answer.title()} played for the {team_name} and won the {award_name}, not {first_name.title()} {last_name.title()}."

    # Step 4: Verify player played for the team
    team_check_query = text('''
        SELECT 1 FROM batting
        WHERE playerID = :player_id AND teamID = :team_id
        LIMIT 1
    ''')
    team_check = db.session.execute(team_check_query, {
        'player_id': submitted_player_id,
        'team_id': team_id
    }).fetchone()
    if not team_check:
        current_user.question_wrong()
        return f"Incorrect. {correct_answer.title()} played for the {team_name} and won the {award_name}, not {first_name.title()} {last_name.title()}."

    # Step 5: If both match, correct
    current_user.question_right()
    return f"Correct! {first_name.title()} {last_name.title()} won the {award_name} while playing for {team_name}."