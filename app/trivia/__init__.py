import csv
import os
from app import db                # Lazy import to avoid circular import
from app.models import TriviaQuestion  # Lazy import to avoid circular import

# Define the base directory for file paths
basedir = os.path.abspath(os.path.dirname(__file__))

def import_trivia_questions_from_csv(csv_path=os.path.join(basedir, 'static', 'trivia_questions.csv')):
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
