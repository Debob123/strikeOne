
import random
from sqlalchemy import text
from app import db

# getting a bunch of years so I can randomly put them in questions
YEARS = list(range(2000, 2024))

FEUD_QUERIES = [
    {
        'needs_year': False,
        'question': lambda y=None: "Name a player with the most career home runs",
        'sql': """
            SELECT CONCAT(p.nameFirst, ' ', p.nameLast) AS name
            FROM batting b
            JOIN people p ON b.playerID = p.playerID
            GROUP BY b.playerID
            ORDER BY SUM(b.b_HR) DESC
            LIMIT 10
        """
    },
    {
        'needs_year': False,
        'question': lambda y=None: "Name a player with the least career errors (minimum 500 games)",
        'sql': """
            SELECT CONCAT(p.nameFirst, ' ', p.nameLast) AS name
            FROM fielding f
            JOIN people p ON f.playerID = p.playerID
            GROUP BY f.playerID
            HAVING SUM(f.f_G) >= 500
            ORDER BY SUM(f.f_E) ASC
            LIMIT 10
        """
    },
    {
        'needs_year': True,
        'question': lambda y: f"Name a team with the most wins in {y}",
        'sql': """
            SELECT team_name
            FROM teams
            WHERE yearID = :year
            ORDER BY team_W DESC
            LIMIT 10
        """
    },
    {
        'needs_year': True,
        'question': lambda y: f"Name a team with the most stolen bases in {y}",
        'sql': """
            SELECT team_name
            FROM teams
            WHERE yearID = :year
            ORDER BY team_SB DESC
            LIMIT 10
        """
    },
    {
        'needs_year': True,
        'question': lambda y: f"Name a player with the most hits in {y}",
        'sql': """
            SELECT CONCAT(p.nameFirst, ' ', p.nameLast) AS name
            FROM batting b
            JOIN people p ON b.playerID = p.playerID
            WHERE b.yearID = :year
            GROUP BY b.playerID
            ORDER BY SUM(b.b_H) DESC
            LIMIT 10
        """
    },
    {
        'needs_year': True,
        'question': lambda y: f"Name a pitcher with the most strikeouts in {y}",
        'sql': """
            SELECT CONCAT(pe.nameFirst, ' ', pe.nameLast) AS name
            FROM pitching p
            JOIN people pe ON p.playerID = pe.playerID
            WHERE p.yearID = :year
            GROUP BY p.playerID
            ORDER BY SUM(p.p_SO) DESC
            LIMIT 10
        """
    },
    {
        'needs_year': False,
        'question': lambda y=None: "Name a player with the most career stolen bases",
        'sql': """
            SELECT CONCAT(p.nameFirst, ' ', p.nameLast) AS name
            FROM batting b
            JOIN people p ON b.playerID = p.playerID
            GROUP BY b.playerID
            ORDER BY SUM(b.b_SB) DESC
            LIMIT 10
        """
    },
    {
        'needs_year': False,
        'question': lambda y=None: "Name a pitcher with the most career wins",
        'sql': """
            SELECT CONCAT(pe.nameFirst, ' ', pe.nameLast) AS name
            FROM pitching p
            JOIN people pe ON p.playerID = pe.playerID
            GROUP BY p.playerID
            ORDER BY SUM(p.p_W) DESC
            LIMIT 10
        """
    },
    {
        'needs_year': True,
        'question': lambda y: f"Name a team with the most shutouts in {y}",
        'sql': """
            SELECT team_name
            FROM teams
            WHERE yearID = :year
            ORDER BY team_SHO DESC
            LIMIT 10
        """
    },
    {
        'needs_year': True,
        'question': lambda y: f"Name a player with the highest batting average (min 300 AB) in {y}",
        'sql': """
            SELECT CONCAT(p.nameFirst, ' ', p.nameLast) AS name
            FROM batting b
            JOIN people p ON b.playerID = p.playerID
            WHERE b.yearID = :year AND b.b_AB >= 300
            GROUP BY b.playerID
            ORDER BY (SUM(b.b_H) / SUM(b.b_AB)) DESC
            LIMIT 10
        """
    }
]

POINT_VALUES = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]

current_round = {
    'question': None,
    'answers': []
}


def generate_feud_round():
    # you'll get a random question each time
    entry = random.choice(FEUD_QUERIES)
    # and maybe a random year
    year = random.choice(YEARS) if entry['needs_year'] else None
    question_text = entry['question'](year)

    # execute the query
    params = {'year': year} if entry['needs_year'] else {}
    rows = db.session.execute(text(entry['sql']), params).fetchall()
    answers = [row[0] for row in rows]

    # mapping the answers to how many points they should be worth
    paired = list(zip(answers, POINT_VALUES[:len(answers)]))
    # and putting them in the right order
    paired_sorted = sorted(paired, key=lambda x: x[1], reverse=True)

    current_round['question'] = question_text
    current_round['answers'] = paired_sorted
    return question_text, paired_sorted


def get_current_feud():
    return current_round['question'], current_round['answers']
