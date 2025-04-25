from app import db, login_manager, bcrypt
import random
from sqlalchemy import text, func

# 100-point questions
teams_questions_100 = [
    "Name a team who has won a world series",
    "Name a team who hasn't won a world series",
    "Name a team that is currently in the American League",
    "Name a team that is currently in the National League"
]

team_sql_100 = [
    "SELECT team_name FROM teams WHERE WSwin = 'Y'",
    "SELECT DISTINCT team_name FROM teams WHERE teamID NOT IN (SELECT teamid FROM teams WHERE WSwin = 'Y')",
    "SELECT team_name FROM teams WHERE lgid = 'AL' AND yearid = 2023",
    "SELECT team_name FROM teams WHERE lgid = 'NL' AND yearid = 2023"
]

# 200-point questions
teams_questions_200 = [
    "Name a team that is currently in the Eastern Division",
    "Name a team that is currently in the Central Division",
    "Name a team that is currently in the Western Division"
]

team_sql_200 = [
    "SELECT team_name FROM teams WHERE Divid = 'E' AND yearid = 2023",
    "SELECT team_name FROM teams WHERE Divid = 'C' AND yearid = 2023",
    "SELECT team_name FROM teams WHERE Divid = 'W' AND yearid = 2023"
]

# 300-point questions
teams_questions_300 = [
    "What team won the world series in {yearid}"
]

team_sql_300 = [
    "SELECT team_name FROM teams WHERE yearID = {yearid} AND WSWin = 'Y'"
]

# 400-point questions
teams_questions_400 = [
    "Name a team with total hits of 1500 or more in the year {yearid}",
    "Name a team with total hits of 1400 or more in the year {yearid}",
    "Name a team with more than 85 wins in {yearid}"
]

team_sql_400 = [
    "SELECT team_name FROM teams WHERE yearID = {yearid} AND team_H >= 1500",
    "SELECT team_name FROM teams WHERE yearID = {yearid} AND team_H >= 1400",
    "SELECT team_name FROM teams WHERE yearID = {yearid} AND team_W > 85"
]

# 500-point questions
teams_questions_500 = [
    "What team has the most total Home Runs",
    "What team has the most total Stolen Bases",
    "What team has the most total Wins",
    "What team has the most total Losses",
    "What team has the most total Shutouts",
    "What team has the most total Hits"
]

team_sql_500 = [
    "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_HR) DESC LIMIT 1",
    "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_SB) DESC LIMIT 1",
    "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_W) DESC LIMIT 1",
    "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_L) DESC LIMIT 1",
    "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_SHO) DESC LIMIT 1",
    "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_H) DESC LIMIT 1"
]

# Organized dictionary for easy access
team_data = {
    100: {
        'questions': teams_questions_100,
        'sql': team_sql_100
    },
    200: {
        'questions': teams_questions_200,
        'sql': team_sql_200
    },
    300: {
        'questions': teams_questions_300,
        'sql': team_sql_300
    },
    400: {
        'questions': teams_questions_400,
        'sql': team_sql_400
    },
    500: {
        'questions': teams_questions_500,
        'sql': team_sql_500
    }
}

people_teams_questions_100 = ["A person who plays for {team1} currently(2023)"]
people_teams_sql_100 = [
    """SELECT DISTINCT p.nameFirst || ' ' || p.nameLast 
       FROM batting b
       JOIN people p ON b.playerID = p.playerID
       NATURAL JOIN teams t
       WHERE t.team_name = '{team1}' AND b.yearID = 2023"""
]

people_teams_questions_200 = ["Name a player who played for {team1} in {yearid}"]
people_teams_sql_200 = [
    """SELECT DISTINCT p.nameFirst || ' ' || p.nameLast 
       FROM batting b
       JOIN people p ON b.playerID = p.playerID
       NATURAL JOIN teams t
       WHERE t.team_name = '{team1}' AND b.yearID = {yearid}"""
]

people_teams_questions_300 = ["Name a player who played for {team1} and {team2}"]
people_teams_sql_300 = [
    """SELECT DISTINCT p.nameFirst || ' ' || p.nameLast 
       FROM batting a
       JOIN batting b ON a.playerID = b.playerID
       JOIN people p ON a.playerID = p.playerID
       JOIN teams t1 ON a.teamid = t1.teamID AND a.yearid = t1.yearID AND a.yearid >= 1950
       JOIN teams t2 ON b.teamid = t2.teamID AND b.yearid = t2.yearID AND b.yearid >= 1950
       WHERE t1.team_name = '{team1}' AND t2.team_name = '{team2}'"""
]

people_teams_questions_400 = ["Name a player who played for {team1} and {team2} and is still alive"]
people_teams_sql_400 = [
    """SELECT DISTINCT p.nameFirst || ' ' || p.nameLast
       FROM batting a
       JOIN batting b ON a.playerID = b.playerID
       JOIN people p ON a.playerID = p.playerID
       JOIN teams t1 ON a.teamid = t1.teamID AND a.yearid = t1.yearID AND a.yearid >= 1980
       JOIN teams t2 ON b.teamid = t2.teamID AND b.yearid = t2.yearID AND b.yearid >= 1980
       WHERE t1.team_name = '{team1}' AND t2.team_name = '{team2}' 
       AND p.deathYear IS NULL"""
]

people_teams_questions_500 = ["Name a player who played for {team1} and {team2} and {team3}"]
people_teams_sql_500 = [
    """SELECT DISTINCT p.nameFirst || ' ' || p.nameLast 
       FROM batting a
       JOIN batting b ON a.playerID = b.playerID
       JOIN batting c ON a.playerID = c.playerID
       JOIN people p ON a.playerID = p.playerID
       JOIN teams t1 ON a.teamid = t1.teamID AND a.yearid = t1.yearID AND a.yearid >= 1950
       JOIN teams t2 ON b.teamid = t2.teamID AND b.yearid = t2.yearID AND b.yearid >= 1950
       JOIN teams t3 ON c.teamid = t3.teamID AND c.yearid = t3.yearID AND c.yearid >= 1950
       WHERE t1.team_name = '{team1}' AND t2.team_name = '{team2}' AND t3.team_name = '{team3}'"""
]

# Organized dictionary

people_teams_data = {
    100: {
        'questions': people_teams_questions_100,
        'sql': people_teams_sql_100
    },
    200: {
        'questions': people_teams_questions_200,
        'sql': people_teams_sql_200
    },
    300: {
        'questions': people_teams_questions_300,
        'sql': people_teams_sql_300
    },
    400: {
        'questions': people_teams_questions_400,
        'sql': people_teams_sql_400
    },
    500: {
        'questions': people_teams_questions_500,
        'sql': people_teams_sql_500
    }
}

batting_questions_100 = [
    "Name a player who has hit more than 30 home runs in a season",
    "Name a player who has more than 50 stolen bases in a season"
]
batting_sql_100 = [
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}"""
]

batting_questions_200 = [
    "Name a player who has the most Stolen bases in their season",
    "Name a player who has the most Home runs in their season",
    "Name a player who has the most Hits in their season"
]
batting_sql_200 = [
    # Most Stolen Bases in a season (your original query)
    """
       SELECT nameFirst || ' ' || nameLast
       FROM season_stats s1 
       WHERE total_stolen_base = (
           SELECT MAX(total_stolen_base) 
           FROM season_stats s2 
           WHERE s1.yearID = s2.yearID
       )
       ORDER BY yearID""",

    # Most Home Runs in a season
    """SELECT nameFirst || ' ' || nameLast
       FROM season_stats s1 
       WHERE total_home_runs = (
           SELECT MAX(total_home_runs) 
           FROM season_stats s2 
           WHERE s1.yearID = s2.yearID
       )
       ORDER BY yearID""",

    # Most Hits in a season
    """SELECT nameFirst || ' ' || nameLast
       FROM season_stats s1 
       WHERE total_hits = (
           SELECT MAX(total_hits) 
           FROM season_stats s2 
           WHERE s1.yearID = s2.yearID
       )
       ORDER BY yearID"""
]

batting_questions_300 = [
    "Name the player who has the most Stolen bases in a season of all time",
    "Name the player who has the most Home runs in a season of all time",
    "Name the player who has the most Hits in a season of all time"
]
batting_sql_300 = [
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}"""
]

batting_questions_400 = [
    "Name a player who has the most Sacrifice hits in their season",
    "Name a player who has the most Strikeouts in their season",
    "Name a player who has the most Sacrifice Flies in their season",
    "Name a player who has the most Hits by Pitch in their season"
]

batting_sql_400 = [
    # Most Sacrifice Hits in a season
    """SELECT nameFirst || ' ' || nameLast
       FROM season_stats s1 
       WHERE total_sacrifice_hits = (
           SELECT MAX(total_sacrifice_hits) 
           FROM season_stats s2 
           WHERE s1.yearID = s2.yearID
       )
       ORDER BY yearID""",

    # Most Strikeouts in a season
    """SELECT nameFirst || ' ' || nameLast
       FROM season_stats s1 
       WHERE total_strikeouts = (
           SELECT MAX(total_strikeouts) 
           FROM season_stats s2 
           WHERE s1.yearID = s2.yearID
       )
       ORDER BY yearID""",

    # Most Sacrifice Flies in a season
    """SELECT nameFirst || ' ' || nameLast
       FROM season_stats s1 
       WHERE total_sacrifice_flies = (
           SELECT MAX(total_sacrifice_flies) 
           FROM season_stats s2 
           WHERE s1.yearID = s2.yearID
       )
       ORDER BY yearID""",

    # Most Hit By Pitch in a season
    """SELECT nameFirst || ' ' || nameLast
       FROM season_stats s1 
       WHERE total_hit_by_pitch = (
           SELECT MAX(total_hit_by_pitch) 
           FROM season_stats s2 
           WHERE s1.yearID = s2.yearID
       )
       ORDER BY yearID"""
]

batting_questions_500 = [
    "Name a player who has the most Sacrifice hits in a season of all time",
    "Name a player who has the most Strikeouts in a season of all time",
    "Name a player who has the most Sacrifice Flies in a season of all time",
    "Name a player who has the most Hits by Pitch in a season of all time"
]
batting_sql_500 = [
    # Most Sacrifice Hits single season (all-time)
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",

    # Most Strikeouts single season (all-time)
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",

    # Most Sacrifice Flies single season (all-time)
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",

    # Most Hit By Pitch single season (all-time)
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}"""
]

# Organized dictionary
batting_data = {
    100: {
        'questions': batting_questions_100,
        'sql': batting_sql_100
    },
    200: {
        'questions': batting_questions_200,
        'sql': batting_sql_200
    },
    300: {
        'questions': batting_questions_300,
        'sql': batting_sql_300
    },
    400: {
        'questions': batting_questions_400,
        'sql': batting_sql_400
    },
    500: {
        'questions': batting_questions_500,
        'sql': batting_sql_500
    }
}

pitching_questions_100 = [
    "Name a player who has had 200+ strikeouts in a season",
    "Name a player who has caused a shutout"
]

pitching_sql_100 = [
    # 150+ strikeouts in a season
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       GROUP BY p.playerID, p.yearID
       HAVING SUM(p.p_SO) >= 200""",

    # Thrown a shutout (1 or more in any season)
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       GROUP BY p.playerID, p.yearID
       HAVING SUM(p.p_SHO) >= 1"""
]

pitching_questions_200 = [
    "Name a player who has thrown a no-hitter",
    "Name a player with 150+ strikeouts in 2023",
    "Name a player with 100+ walks in a season"
]

pitching_sql_200 = [
    # Thrown a no-hitter (assuming no-hitters are noted in awards table)
    """SELECT nameFirst || ' ' || nameLast
       FROM awards a
       JOIN people pe ON a.playerID = pe.playerID
       WHERE a.awardID LIKE '%No-Hitter%'""",

    # 150+ strikeouts in 2023
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       WHERE p.yearID = 2023
       GROUP BY p.playerID,yearid
       HAVING SUM(p.p_SO) >= 150""",

    # 100+ walks in a season
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       GROUP BY p.playerID, p.yearID
       HAVING SUM(p.p_BB) >= 100"""
]

pitching_questions_300 = [
    "Name a player with 150+ strikeouts in {yearid}",
    "Name a player who threw a shutout in {yearid}"
]

pitching_sql_300 = [
    # 150+ strikeouts in {yearid}
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       WHERE p.yearID = {yearid}
       GROUP BY p.playerID,yearid
       HAVING SUM(p.p_SO) >= 150""",

    # Threw a shutout in {yearid}
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       WHERE p.yearID = {yearid}
       GROUP BY p.playerID,yearid
       HAVING SUM(p.p_SHO) >= 1"""
]

pitching_questions_400 = [
    "Name the person who has the most strikeouts in a season of all time ",
    "Name the person with the most wins in a season of all time"
]

pitching_sql_400 = [
    # Most strikeouts in a season of all time
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       GROUP BY p.playerID, p.yearID
       ORDER BY SUM(p.p_SO) DESC
       LIMIT 1""",

    # Most wins in a season of all time
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       GROUP BY p.playerID, p.yearID
       ORDER BY SUM(p.p_W)  DESC
       LIMIT 1"""
]

pitching_questions_500 = [
    "Name the person with the most hit-by-pitch in a season of all time",
    "Name a player with 2+ no-hitters",
    "Name the player with the most pitching stints"
]


pitching_sql_500 = [
    # Most hit-by-pitch in a season of all time
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       GROUP BY p.playerID, p.yearID
       ORDER BY SUM(p.p_HBP) DESC
       LIMIT 1""",

    # 2+ no-hitters (again assuming award table logs them, or approximate)
    """SELECT nameFirst || ' ' || nameLast
       FROM awards a
       JOIN people pe ON a.playerID = pe.playerID
       WHERE a.awardID LIKE '%No-Hitter%'
       GROUP BY a.playerID
       HAVING COUNT(*) >= 2""",

    # Most pitching stints (i.e. most seasons with at least 1 pitching appearance)
    """SELECT nameFirst || ' ' || nameLast
       FROM pitching p
       JOIN people pe ON p.playerID = pe.playerID
       GROUP BY p.playerID
       ORDER BY COUNT(DISTINCT p.yearID) DESC
       LIMIT 1"""
]

# Combine into dictionary
pitching_data = {
    100: {
        'questions': pitching_questions_100,
        'sql': pitching_sql_100
    },
    200: {
        'questions': pitching_questions_200,
        'sql': pitching_sql_200
    },
    300: {
        'questions': pitching_questions_300,
        'sql': pitching_sql_300
    },
    400: {
        'questions': pitching_questions_400,
        'sql': pitching_sql_400
    },
    500: {
        'questions': pitching_questions_500,
        'sql': pitching_sql_500
    }
}

fielding_questions_100 = [
    "Name a player who played catcher",
    "Name a player who played first base",
    "Name a player who played third base",
    "Name a player who played outfield"
]

fielding_sql_100 = [
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.position = 'C'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.position = '1B'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.position = '3B'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.position = 'OF'"""
]

fielding_questions_200 = ["Name a player who played second base",
                          "Name a player who played center field",
                          "Name a player who played left field",
                          "Name a player who played right field",
                          "Name a player who played shortstop"]

fielding_sql_200 = [
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.position = '2B'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.position = 'CF'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.position = 'LF'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.position = 'RF'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.position = 'SS'"""
]

fielding_questions_300 = ["Name a player who has more than 1500 put outs in a season",
                          "Name a player who has started more than 300 games in a season",
                          "Name a player who has caused more than 150 double plays in a season"]

fielding_sql_300 = [
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",

    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",

    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}"""
]

fielding_questions_400 = ["Name a player who has started more than 300 games in the year {yearid}",
                          "Name a player who has caused more than 100 double plays in the year {yearid}",
                          "Name a player who has more than 1000 putouts in the year {yearid}"]

fielding_sql_400 = [
    """SELECT DISTINCT nameFirst || ' ' || nameLast
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.yearID = {yearid}
       GROUP BY f.playerID, f.yearID 
       HAVING SUM(f.f_GS) > 300""",

    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.yearID = {yearid}
       GROUP BY f.playerID, f.yearID 
       HAVING SUM(f.f_DP) > 100""",

    """SELECT DISTINCT nameFirst || ' ' || nameLast
       FROM fielding f
       JOIN people p ON f.playerID = p.playerID
       WHERE f.yearID = {yearid}
       GROUP BY f.playerID, f.yearID 
       HAVING SUM(f.f_PO) > 1000"""
]

fielding_questions_500 = ["Name the player with the most putouts in a season of all time",
                          "Name the player who has the most caught stealing in a season of all time",
                          "Name a player with more than 100 errors in a season"]

fielding_sql_500 = [
    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",

    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}""",

    """Select name FROM JeopardyValues WHERE type = '{type}' AND idx = {index}"""
]


fielding_data = {
    100: {
        'questions': fielding_questions_100,
        'sql': fielding_sql_100
    },
    200: {
        'questions': fielding_questions_200,
        'sql': fielding_sql_200
    },
    300: {
        'questions': fielding_questions_300,
        'sql': fielding_sql_300
    },
    400: {
        'questions': fielding_questions_400,
        'sql': fielding_sql_400
    },
    500: {
        'questions': fielding_questions_500,
        'sql': fielding_sql_500
    }
}

awards_questions_100 = [
    "Name a person who has won the Gold Glove",
    "Name a person who has won the Silver Slugger",
    "Name a person who has won the Most Valuable Player",
    "Name a person who has won the World Series MVP",
    "Name a person who has won the Platinum Glove"
]

awards_sql_100 = [
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM awards a
       JOIN people p ON a.playerID = p.playerID
       WHERE a.awardID = 'Gold Glove'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast
       FROM awards a
       JOIN people p ON a.playerID = p.playerID
       WHERE a.awardID = 'Silver Slugger'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM awards a
       JOIN people p ON a.playerID = p.playerID
       WHERE a.awardID = 'Most Valuable Player'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM awards a
       JOIN people p ON a.playerID = p.playerID
       WHERE a.awardID = 'World Series MVP'""",
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM awards a
       JOIN people p ON a.playerID = p.playerID
       WHERE a.awardID = 'Platinum Glove'"""
]

awards_questions_200 = ["Name a player who has won the Triple Crown",
                        "Name a player who has won the All Star Game MVP",
                        "Name a player who has won the Pitching Triple Crown",
                        "Name a player who has won the Comeback Player of the Year award"]

awards_sql_200 = [
    # Triple Crown
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM awards a
       JOIN people p ON a.playerID = p.playerID
       WHERE a.awardID = 'Triple Crown'""",

    # All Star Game MVP
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM awards a
       JOIN people p ON a.playerID = p.playerID
       WHERE a.awardID = 'All-Star Game MVP'""",

    # Pitching Triple Crown
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM awards a
       JOIN people p ON a.playerID = p.playerID
       WHERE a.awardID = 'Pitching Triple Crown'""",

    # Comeback Player of the Year
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM awards a
       JOIN people p ON a.playerID = p.playerID
       WHERE a.awardID = 'Comeback Player of the Year'"""
]


awards_questions_300 = ["Name a player who has won the {award1} award"]

awards_sql_300 = [
    """SELECT DISTINCT nameFirst || ' ' || nameLast
       FROM awards a 
       JOIN people p ON a.playerID = p.playerID 
       WHERE a.awardID = '{award1}'"""
]


awards_questions_400 = ["Name a player who has won both the Gold Glove and Silver Slugger awards",
                        "Name a player who has won both the Most Valuable Player and World Series MVP awards",
                        "Name a player who has won both the Triple Crown and All Star Game MVP awards"]

awards_sql_400 = [
    # Gold Glove and Silver Slugger
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM people p 
       JOIN awards a1 ON p.playerID = a1.playerID AND a1.awardID = 'Gold Glove' 
       JOIN awards a2 ON p.playerID = a2.playerID AND a2.awardID = 'Silver Slugger'""",

    # MVP and WS MVP
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM people p 
       JOIN awards a1 ON p.playerID = a1.playerID AND a1.awardID = 'Most Valuable Player' 
       JOIN awards a2 ON p.playerID = a2.playerID AND a2.awardID = 'World Series MVP'""",

    # Triple Crown and All Star Game MVP
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM people p 
       JOIN awards a1 ON p.playerID = a1.playerID AND a1.awardID = 'Triple Crown' 
       JOIN awards a2 ON p.playerID = a2.playerID AND a2.awardID = 'All-Star Game MVP'"""
]


awards_questions_500 = ["Name a player who has won the {award1} award and the {award2} award"]


awards_sql_500 = [
    """SELECT DISTINCT nameFirst || ' ' || nameLast 
       FROM people p 
       JOIN awards a1 ON p.playerID = a1.playerID AND a1.awardID = '{award1}' 
       JOIN awards a2 ON p.playerID = a2.playerID AND a2.awardID = '{award2}'"""
]

awards_data = {
    100: {
        'questions': awards_questions_100,
        'sql': awards_sql_100
    },
    200: {
        'questions': awards_questions_200,
        'sql': awards_sql_200
    },
    300: {
        'questions': awards_questions_300,
        'sql': awards_sql_300
    },
    400: {
        'questions': awards_questions_400,
        'sql': awards_sql_400
    },
    500: {
        'questions': awards_questions_500,
        'sql': awards_sql_500
    }
}


# Optional: You might want to create dictionaries to organize the questions by category
categories = {
    "Teams": team_data,
    "People_Teams": people_teams_data,
    "Batting": batting_data,
    "Pitching": pitching_data,
    "Fielding": fielding_data,
    "Awards": awards_data
}


stored_answers = []

def generate_questions():
    questions_text = []
    for category in categories:
        print(str(category))
        if category == 'Teams':

            for number in categories[category]:
                fortnite = []
                while not fortnite:

                    gen = len(categories[category][number]['questions'])
                    print(str(number))
                    yearid = 2000 + random.randint(1, 23)

                    index = random.randint(0, gen - 1)
                    question = categories[category][number]['questions'][index].format(yearid=yearid)
                    sql = categories[category][number]['sql'][index].format(yearid=yearid)

                    fortnite = db.session.execute(text(sql)).fetchall()
                    fortnite = [row[0] for row in fortnite if row[0] is not None]
                    stored_answers.append({"q_" + str(category) + "_" + str(number): fortnite})

                questions_text.append({
                    'category': category,
                    'points': number,
                    'question': question
                })

            print("ROBLOX")
        elif category == 'People_Teams':

            for number in categories[category]:
                fortnite = []
                count = 0
                while not fortnite:
                    team1 = 'team1'
                    team2 = 'team2'
                    team3 = 'team3'
                    gen = len(categories[category][number]['questions'])
                    print(str(number))
                    yearid = 2000 + random.randint(1, 23)

                    if number == 200 or number == 100:
                        print("fortnite")
                        teams = db.session.execute(
                            text(
                                "SELECT team_name FROM teams WHERE yearid = {yearid}".format(yearid=yearid))).fetchall()

                        teams = [team[0] for team in teams]

                        team1 = random.choice(teams)
                    else:
                        teams = db.session.execute(
                            text("SELECT distinct team_name FROM teams")).fetchall()
                        teams = [team[0] for team in teams]
                        team1 = random.choice(teams)
                        team2 = team1
                        team3 = team1
                        while team2 == team1 or team3 == team1 or team3 == team2:
                            team2 = random.choice(teams)
                            team3 = random.choice(teams)

                    team1 = team1.replace("'", "''")
                    team2 = team2.replace("'", "''")
                    team3 = team3.replace("'", "''")
                    index = random.randint(0, gen - 1)
                    question = categories[category][number]['questions'][index].format(yearid=yearid, team1=team1,
                                                                                       team2=team2, team3=team3)
                    sql = categories[category][number]['sql'][index].format(yearid=yearid, team1=team1, team2=team2,
                                                                            team3=team3)

                    # print(text(sql))
                    fortnite = db.session.execute(text(sql)).fetchall()
                    fortnite = [row[0] for row in fortnite if row[0] is not None]
                    stored_answers.append({"q_" + str(category) + "_" + str(number): fortnite})
                    print("FORtnTE")
                    print(fortnite)

                    count = count + 1

                questions_text.append({
                    'category': category,
                    'points': number,
                    'question': question
                })

                print("COUNT: " + str(count))

        elif category == 'Batting':
            for number in categories[category]:
                fortnite = []
                count = 0
                while not fortnite:

                    gen = len(categories[category][number]['questions'])
                    print(str(number))


                    index = random.randint(0, gen - 1)
                    type = 'batting_' + str(number)
                    question = categories[category][number]['questions'][index].format(index=index,type=type)
                    sql = categories[category][number]['sql'][index].format(index=index,type=type)

                    # print(text(sql))
                    fortnite = db.session.execute(text(sql)).fetchall()
                    fortnite = [row[0] for row in fortnite if row[0] is not None]
                    stored_answers.append({"q_" + str(category) + "_" + str(number): fortnite})



                questions_text.append({
                    'category': category,
                    'points': number,
                    'question': question
                })

        elif category == 'Pitching':
            for number in categories[category]:
                fortnite = []

                gen = len(categories[category][number]['questions'])
                print(str(number))
                yearid = 2000 + random.randint(1, 23)

                index = random.randint(0, gen - 1)

                question = categories[category][number]['questions'][index].format(yearid=yearid)
                sql = categories[category][number]['sql'][index].format(yearid=yearid)

                #print(text(question))
                #print(text(sql))
                fortnite = db.session.execute(text(sql)).fetchall()
                fortnite = [row[0] for row in fortnite if row[0] is not None]
                stored_answers.append({"q_" + str(category) + "_" + str(number): fortnite})
                #print(str(fortnite))


                questions_text.append({
                    'category': category,
                    'points': number,
                    'question': question
                })
        elif category == 'Fielding':
            for number in categories[category]:
                fortnite = []

                while not fortnite:
                    gen = len(categories[category][number]['questions'])
                    print(str(number))
                    yearid = 2000 + random.randint(1, 23)

                    index = random.randint(0, gen - 1)
                    type = 'fielding_' + str(number)
                    question = categories[category][number]['questions'][index].format(yearid=yearid,index=index,type=type)
                    sql = categories[category][number]['sql'][index].format(yearid=yearid,index=index,type=type)

                    #print(text(question))
                    #print(text(sql))
                    fortnite = db.session.execute(text(sql)).fetchall()
                    fortnite = [row[0] for row in fortnite if row[0] is not None]
                    stored_answers.append({"q_" + str(category) + "_" + str(number): fortnite})
                    #print(str(fortnite))

                questions_text.append({
                    'category': category,
                    'points': number,
                    'question': question
                })
        elif category == 'Awards':
            for number in categories[category]:
                fortnite = []
                while not fortnite:
                    gen = len(categories[category][number]['questions'])
                    print(str(number))
                    yearid = 2000 + random.randint(1, 23)
                    sql = 'Select distinct awardid from awards;'
                    awardid = db.session.execute(text(sql)).fetchall()
                    awardid = [awardid[0] for awardid in awardid]

                    award1 = random.choice(awardid)
                    award2 = award1

                    while award2 == award1:
                        award2 = random.choice(awardid)

                    # print("THE AWARDS: ")
                    # print(str(awardid))


                    index = random.randint(0, gen - 1)

                    question = categories[category][number]['questions'][index].format(yearid=yearid, award1=award1, award2=award2)
                    sql = categories[category][number]['sql'][index].format(yearid=yearid, award1=award1, award2=award2)

                    #print(text(question))
                    #print(text(sql))
                    fortnite = db.session.execute(text(sql)).fetchall()
                    fortnite = [row[0] for row in fortnite if row[0] is not None]
                    stored_answers.append({"q_" + str(category) + "_" + str(number): fortnite})
                    #print(str(fortnite))

                questions_text.append({
                    'category': category,
                    'points': number,
                    'question': question
                })
    return questions_text