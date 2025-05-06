from app import db
from sqlalchemy import text

first_base = 0
second_base = 0
third_base = 0

team1_score = 0
team2_score = 0

outs = 0
teamUp = "Team 1"

inning = 1

questions = {
    'first_base': {
        "question" : "",
        "answers" : [],
    },
    'second_base':  {
        "question" : "",
        "answers" : [],
    },
    'third_base': {
        "question" : "",
        "answers" : [],
    },
    'home_run': {
        "question" : "",
        "answers" : [],
    },
}

baseball_questions = {
        'first_base': {
            'questions': [],
            'sql': []
        },
        'second_base': {
            'questions': [],
            'sql': []
        },
        'third_base': {
            'questions': [],
            'sql': []
        },
        'home_run': {
            'questions': [],
            'sql': []
        }
    }

def store_question_answers():
    stored_baseball_questions = {
        'first_base': {
            'questions': [],
            'sql': []
        },
        'second_base': {
            'questions': [],
            'sql': []
        },
        'third_base': {
            'questions': [],
            'sql': []
        },
        'home_run': {
            'questions': [],
            'sql': []
        }
    }
    for base in ['first_base', 'second_base', 'third_base', 'home_run']:
        sql = f"SELECT * FROM BaseballGameQuestions WHERE BaseId = '{base}' ORDER BY BaseNum ASC"
        results = db.session.execute(text(sql)).fetchall()

        stored_questions = [row.BaseQuestion for row in results]
        sql_statements = [row.BaseSQL for row in results]

        stored_baseball_questions[base] = {
            'questions': stored_questions,
            'sql': sql_statements
        }

    return stored_baseball_questions
