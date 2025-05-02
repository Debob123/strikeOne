import random
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


def check_answer(user_input):
    # Retrieve the year threshold from session
    year_threshold = session.get("question8_year_threshold")
    if year_threshold is None:
        return "Missing question context."

    # Clean and format user input
    user_input = user_input.strip().lower()
    if not user_input:
        return "Please enter a name."

    name_parts = user_input.split()
    if len(name_parts) < 2:
        return "Please enter both first and last name."

    # Extract first and last name
    first_name = name_parts[0]
    last_name = name_parts[-1]

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
        return "Correct!"
    return f"Incorrect. That player either played fewer than {year_threshold} years or made an All-Star appearance."
