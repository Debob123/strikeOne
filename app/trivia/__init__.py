import csv
import os
import random

from sqlalchemy import text
from app import db                # Lazy import to avoid circular import
from app.models import TriviaQuestion  # Lazy import to avoid circular import

class Question:
    def __init__(self, question_text, correct_answers):
        self.question_text = question_text  # The trivia question
        self.correct_answers = correct_answers  # List of correct answers (e.g., ["Answer1", "Answer2"])

    def add_correct_answer(self, answer):
        if answer not in self.correct_answers:
            self.correct_answers.append(answer)

    def is_correct_answer(self, answer):
        return answer in self.correct_answers

    def __repr__(self):
        return f"<TriviaQuestion(question_text={self.question_text}, correct_answers={self.correct_answers})>"

# Define the base directory for file paths
def import_trivia_questions_from_csv(csv_path):
    try:
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    trivia_question = TriviaQuestion(
                        question_id=int(row['question_id']),
                        question=row['question'],
                        query=row['query']
                    )

                    # Add trivia question to the session
                    db.session.add(trivia_question)
                except Exception as e:
                    print(f"Skipping row due to error: {e}\nRow: {row}")
            
            # Commit the changes to the database
            db.session.commit()
            print("Trivia question data import complete.")

    except FileNotFoundError:
        print(f"CSV file not found: {csv_path}")
    except Exception as e:
        print(f"An error occurred while importing data: {e}")
        
def generate_incorrect_answers(correct_answers):
    """
    Generate three incorrect answers by selecting players who are not in the correct answers list.

    Args:
        correct_answers (list): A list of correct player names (first and last name).

    Returns:
        list: A list of three incorrect player names.
    """
    # Step 1: Prepare the correct names in a format suitable for comparison (lowercase)
    correct_names_set = set([name.lower() for name in correct_answers])

    # Step 2: Query the database to find players whose names are not in the correct answers list
    query = text('''
        SELECT nameFirst, nameLast
        FROM people
        WHERE CONCAT(nameFirst, ' ',nameLast) NOT IN :correct_names
    ''')

    result = db.session.execute(query, {'correct_names': tuple(correct_names_set)})
    all_players = result.fetchall()

    if len(all_players) < 3:
        print("Error: Not enough distinct players to generate incorrect answers.")
        return None

    # Step 3: Randomly select 3 distinct incorrect players
    incorrect_players = random.sample(all_players, 3)

    # Step 4: Format the incorrect players as "First Last" names
    incorrect_answers = [f"{first} {last}" for first, last in incorrect_players]

    return incorrect_answers
