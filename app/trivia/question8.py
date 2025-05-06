import random
from sqlite3 import Cursor
from flask import session
from app import db
from sqlalchemy import text
from app.trivia import Question


def generate_question8(question_text):
    # Step 1: Select a random year threshold (multiple of 5 between 10 and 25)
    year_threshold = random.choice([10, 15, 20, 25])

    # Step 2: Find players who are:
    # - in `people`
    # - not in `allstarfull`
    # - have appeared in >= `year_threshold` distinct seasons
    query = text("""
        SELECT p.nameFirst, p.nameLast
    FROM people p
    JOIN (
        SELECT b.playerID
        FROM batting b
        WHERE b.playerID NOT IN (SELECT playerID FROM allstarfull)
        GROUP BY b.playerID
        HAVING COUNT(DISTINCT b.yearID) >= :threshold
    ) AS eligible ON p.playerID = eligible.playerID
    ORDER BY RAND()  -- Changed to RAND() for MySQL
    LIMIT 1  -- Limit to one result
    """)

    result = db.session.execute(query, {"threshold": year_threshold}).fetchall()

    if not result:
        return None, f"No eligible players found with at least {year_threshold} seasons and no All-Star appearances."

    # Format full names
    players = [f"{row[0]} {row[1]}" for row in result]

    # Step 3: Format the question (make sure the placeholder {years} is in question_text)
    formatted_question = question_text.format(years=year_threshold)

    # Step 4: Store the correct answers and context
    session["question8_year_threshold"] = year_threshold
    session["correct_answers"] = players

    return Question(question_text=formatted_question, correct_answers=players), None


def check_answer(user_input, correct_answer):
    # Retrieve the year threshold from session
    year_threshold = session.get("question8_year_threshold")
    if year_threshold is None:
        return "Missing question context."
    
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

    # Query to check if the player matches the criteria
    query = text("""
        SELECT p.playerID
        FROM people p
        WHERE LOWER(p.nameFirst) = :first
          AND LOWER(p.nameLast) = :last
          AND p.playerID NOT IN (SELECT playerID FROM allstarfull)
          AND (
              SELECT COUNT(DISTINCT b.yearID)
              FROM batting b
              WHERE b.playerID = p.playerID
          ) >= :threshold
    """)

    # Execute the query and get result
    result = db.session.execute(query, {
        "first": first_name,
        "last": last_name,
        "threshold": year_threshold
    }).fetchone()

    # Return appropriate feedback based on result
    if result:
        return f"Correct! {user_input} played more than {year_threshold} and never made an All-Star game."
    
    return f"Incorrect. {correct_answer} played more than {year_threshold} and never made an All-Star game, not {user_input}."
