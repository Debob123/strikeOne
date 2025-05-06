from flask import session
from app import db
from sqlalchemy import text
from app.trivia import Question
from flask_login import current_user

def generate_question6(question_text):
    max_attempts = 20  # prevent infinite loops
    attempts = 0

    while attempts < max_attempts:
        # 1. Randomly select a player with a full birthdate
        player_query = text('''
            SELECT nameFirst, nameLast, birthMonth, birthDay, birthYear
            FROM people
            WHERE birthMonth IS NOT NULL AND birthDay IS NOT NULL AND birthYear IS NOT NULL
            ORDER BY RAND()
            LIMIT 1
        ''')
        result = db.session.execute(player_query).fetchone()

        if not result:
            attempts += 1
            continue  # try again

        name_first, name_last, birth_month, birth_day, birth_year = result
        player_name = f"{name_first} {name_last}"

        # 2. Check for other players with the same birthday
        match_query = text('''
            SELECT nameFirst, nameLast
            FROM people
            WHERE birthMonth = :month AND birthDay = :day AND birthYear = :year
              AND NOT (nameFirst = :first AND nameLast = :last)
        ''')
        rows = db.session.execute(match_query, {
            'month': birth_month,
            'day': birth_day,
            'year': birth_year,
            'first': name_first,
            'last': name_last
        }).fetchall()

        if rows:
            # 3. Store info in session
            session['trivia_birthday_month'] = birth_month
            session['trivia_birthday_day'] = birth_day
            session['trivia_birthday_year'] = birth_year
            session['trivia_reference_player'] = player_name

            # 4. Generate question and answer list
            rendered_question = question_text.replace("{player}", player_name)
            answers = [f"{row[0]} {row[1]}" for row in rows]
            return Question(rendered_question, answers), None

        attempts += 1

    return None, "Failed to find a player with a shared birthday after multiple attempts."

def check_answer(user_input, correct_answer):
    # Get reference birthday from session
    birth_month = session.get('trivia_birthday_month')
    birth_day = session.get('trivia_birthday_day')
    birth_year = session.get('trivia_birthday_year')

    if not (birth_month and birth_day and birth_year):
        return "No reference birthday found in session."

    # Find the selected player's birthday
    player_query = text('''
        SELECT birthMonth, birthDay, birthYear
        FROM people
        WHERE CONCAT(nameFirst, ' ', nameLast) = :name
    ''')
    result = db.session.execute(player_query, {'name': user_input}).fetchone()

    if not result:
        current_user.question_wrong()
        return f"Incorrect. '{user_input}' is not a valid player."

    user_month, user_day, user_year = result

    # Compare birthday
    if (user_month, user_day, user_year) == (birth_month, birth_day, birth_year):
        current_user.question_right()
        return f"Correct! {user_input} has the same birthday."
    else:
        current_user.question_wrong()
        ref_name = session.get('trivia_reference_player', 'the reference player')
        return f"Incorrect. {correct_answer} shares a birthday with {ref_name}, not {user_input}."