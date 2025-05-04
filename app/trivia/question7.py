from flask import session
from app import db
from sqlalchemy import text
from app.trivia import Question
from flask_login import current_user

def generate_question7(question_text):
    # Step 1: Select a random year from salaries table
    year_result = db.session.execute(text("SELECT DISTINCT yearId FROM salaries ORDER BY RAND() LIMIT 1"))
    year_row = year_result.fetchone()
    if not year_row:
        return None, "No years found in salaries table."

    year = year_row[0]

    # Step 2: Select a random salary from that year
    salary_result = db.session.execute(
        text("SELECT DISTINCT salary FROM salaries WHERE yearId = :year ORDER BY RAND() LIMIT 1"),
        {"year": year}
    )
    salary_row = salary_result.fetchone()
    if not salary_row:
        return None, f"No salaries found for year {year}."

    salary = int(salary_row[0])  # Cast to int to avoid decimals in question

    # Step 3: Get all players with that salary in that year
    player_result = db.session.execute(
        text("""
            SELECT people.nameFirst, people.nameLast
            FROM salaries
            JOIN people ON salaries.playerID = people.playerID
            WHERE salaries.yearId = :year AND salaries.salary = :salary
        """),
        {"year": year, "salary": salary}
    )

    players = [f"{row[0]} {row[1]}" for row in player_result]

    if not players:
        return None, f"No players found with salary ${salary} in {year}."

    # Step 4: Format the question with salary and year
    formatted_question = question_text.format(salary=salary, yearID=year)

    # Step 5: Store correct answers and return Question object
    session["correct_answers"] = players
    session["expected_salary"] = salary
    session["expected_year"] = year
    return Question(question_text=formatted_question, correct_answers=players), None

def check_answer(user_input):
    expected_salary = session.get("expected_salary")
    year = session.get("expected_year")

    if expected_salary is None or year is None:
        return "Cannot verify answer: missing context."

    user_input = user_input.strip().lower()
    if not user_input:
        return "Please enter a name."

    name_parts = user_input.split()
    if len(name_parts) < 2:
        return "Please provide both first and last name."

    first_name = name_parts[0]
    last_name = name_parts[-1]

    result = db.session.execute(
        text("""
            SELECT salary
            FROM salaries
            JOIN people ON salaries.playerID = people.playerID
            WHERE LOWER(people.nameFirst) = :first_name
              AND LOWER(people.nameLast) = :last_name
              AND salaries.yearId = :year
        """),
        {"first_name": first_name, "last_name": last_name, "year": year}
    )

    for row in result:
        salary = int(row[0])
        if salary == expected_salary:
            return "Correct!"

    return f"Incorrect. That player did not earn ${expected_salary} in {year}."
