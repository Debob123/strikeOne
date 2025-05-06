
first_base = 0
second_base = 0
third_base = 0

team1_score = 0
team2_score = 0

outs = 0

inning = 1

first_base_questions = ["Name a team who has won a world series"
                        "Name a team who hasn't won a world series"
                        "Name a team that is currently in the National League"
                        "Name a team that is currently in the American League"
                        "Name a person who plays for {team1} currently(2023)"
                        "Name a player who has more than 50 stolen bases in a season"
                        "Name a player who has had 200+ strikeouts in a season"
                        "Name a player who has won the Gold Glove"
                        "Name a team that is currently in the Eastern Division"
                        "Name a team that is currently in the Central Division"
                        "Name a team that is currently in the Western Division"
                        "Name a player who played for {team1} in {yearid}"
                        "Name a player who has won the Triple Crown"
                        "Name a player who has won the All Star Game MVP"
                        "Name a player who has won the Pitching Triple Crown"
                        "Name a player who has won the Comeback Player of the Year award"
                        "Name a batter who has the most Stolen bases in their season"
                        "Name a batter who has the most Home runs in their season"
                        "Name a pitcher with 150+ strikeouts in 2023"
                        "Name a pitcher with 100+ walks in a season"
                        "Name a fielding player who played second base"
                        "Name a player who played center field"
                        "Name a player who played left field"
                        "Name a player who played right field"
                        "Name a player who played shortstop"]

first_base_sql = ["SELECT team_name FROM teams WHERE WSwin = 'Y'"
                  "SELECT DISTINCT team_name FROM teams WHERE teamID NOT IN (SELECT teamid FROM teams WHERE WSwin = \'Y\')"
                  "SELECT team_name FROM teams WHERE lgid = \'NL\' AND yearid = 2023"
                  "SELECT team_name FROM teams WHERE lgid = \'AL\' AND yearid = 2023"
                  "SELECT DISTINCT p.nameFirst || ' ' || p.nameLast FROM batting b JOIN people p ON b.playerID = p.playerID NATURAL JOIN teams t WHERE t.team_name = ''{team1}'' AND b.yearID = 2023"
                  "Select name FROM JeopardyValues WHERE type = 'batting_100' AND idx = 1"
                  "SELECT nameFirst || ' ' || nameLast FROM pitching p JOIN people pe ON p.playerID = pe.playerID GROUP BY p.playerID, p.yearID HAVING SUM(p.p_SO) >= 200"
                  "SELECT DISTINCT nameFirst || '  ' || nameLast FROM awards a JOIN people p ON a.playerID = p.playerID WHERE a.awardID = 'Gold Glove'"
                  "SELECT team_name FROM teams WHERE Divid = \'E\' AND yearid = 2023"
                  "SELECT team_name FROM teams WHERE Divid = \'C\' AND yearid = 2023"
                  "SELECT team_name FROM teams WHERE Divid = \'W\' AND yearid = 2023"
                  "SELECT DISTINCT p.nameFirst || ' ' || p.nameLast FROM batting b JOIN people p ON b.playerID = p.playerID NATURAL JOIN teams t WHERE t.team_name = '{team1}'"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM awards a JOIN people p ON a.playerID = p.playerID WHERE a.awardID = 'Triple Crown'"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM awards a JOIN people p ON a.playerID = p.playerID WHERE a.awardID = 'All-Star Game MVP'"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM awards a JOIN people p ON a.playerID = p.playerID WHERE a.awardID = 'Pitching Triple Crown'"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM awards a JOIN people p ON a.playerID = p.playerID WHERE a.awardID = 'Comeback Player of the Year'"
                  "SELECT nameFirst || ' ' || nameLast FROM season_stats s1 WHERE total_stolen_base = (SELECT MAX(total_stolen_base) FROM season_stats s2 WHERE s1.yearID = s2.yearID) ORDER BY yearID"
                  "SELECT nameFirst || ' ' || nameLast FROM season_stats s1 WHERE total_home_runs = (SELECT MAX(total_home_runs) FROM season_stats s2 WHERE s1.yearID = s2.yearID) ORDER BY yearID"
                  "SELECT nameFirst || ' ' || nameLast FROM pitching p JOIN people pe ON p.playerID = pe.playerID WHERE p.yearID = 2023 GROUP BY p.playerID, yearid HAVING SUM(p.p_SO) >= 150"
                  "SELECT nameFirst || ' ' || nameLast FROM pitching p JOIN people pe ON p.playerID = pe.playerID GROUP BY p.playerID, p.yearID HAVING SUM(p.p_BB) >= 100"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM fielding f JOIN people p ON f.playerID = p.playerID WHERE f.position = '2B'"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM fielding f JOIN people p ON f.playerID = p.playerID WHERE f.position = 'CF'"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM fielding f JOIN people p ON f.playerID = p.playerID WHERE f.position = 'LF'"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM fielding f JOIN people p ON f.playerID = p.playerID WHERE f.position = 'RF'"
                  "SELECT DISTINCT nameFirst || ' '  || nameLast FROM fielding f JOIN people p ON f.playerID = p.playerID WHERE f.position = 'SS'"]

second_base_questions = ["What team won the world series in {yearid}"
                         "Name a player who played for {team1} and {team2}"
                         "Name a pitcher with 150+ strikeouts in {yearid}"
                         "Name a pitcher who threw a shutout in {yearid}"
                         "Name a player who has won the {award1} award"]
second_base_sql = ["SELECT team_name FROM teams WHERE yearID = {yearid} AND WSWin = \'Y\'"
                   "SELECT DISTINCT p.nameFirst || ' ' || p.nameLast FROM batting a JOIN batting b ON a.playerID = b.playerID JOIN people p ON a.playerID = p.playerID JOIN teams t1 ON a.teamid = t1.teamID AND a.yearid = t1.yearID AND a.yearid >= 1950 JOIN teams t2 ON b.teamid = t2.teamID AND b.yearid = t2.yearID AND b.yearid >= 1950 WHERE t1.team_name = '{team1}' AND t2.team_name = '{team2}'"
                   "SELECT nameFirst || ' ' || nameLast FROM pitching p JOIN people pe ON p.playerID = pe.playerID WHERE p.yearID = {yearid} GROUP BY p.playerID, yearid HAVING SUM(p.p_SO) >= 150"
                   "SELECT nameFirst || ' ' || nameLast FROM pitching p JOIN people pe ON p.playerID = pe.playerID WHERE p.yearID = {yearid} GROUP BY p.playerID, yearid HAVING SUM(p.p_SHO) >= 1"
                   "SELECT DISTINCT nameFirst || ' ' || nameLast FROM awards a JOIN people p ON a.playerID = p.playerID WHERE a.awardID = '{award1}'"]

third_base_questions = ["Name a team with total hits of 1500 or more in the year {yearid}"
                        "Name a team with total hits of 1400 or more in the year {yearid}"
                        "Name a team with more than 85 wins in {yearid}"
                        "Name a player who played for {team1} and {team2} and is still alive"
                        "Name a fielding player who has started more than 300 games in the year {yearid}"
                        "Name a fielding player who has caused more than 100 double plays in the year {yearid}"
                        "Name a fielding player who has more than 1000 putouts in the year {yearid}"
                        ]
third_base_sql = ["SELECT team_name FROM teams WHERE yearID = {yearid} AND team_H >= 1500"
                  "SELECT team_name FROM teams WHERE yearID = {yearid} AND team_H >= 1400"
                  "SELECT team_name FROM teams WHERE yearID = {yearid} AND team_W > 85"
                  "SELECT DISTINCT p.nameFirst || ' ' || p.nameLast FROM batting a JOIN batting b ON a.playerID = b.playerID JOIN people p ON a.playerID = p.playerID JOIN teams t1 ON a.teamid = t1.teamID AND a.yearid = t1.yearID AND a.yearid >= 1980 JOIN teams t2 ON b.teamid = t2.teamID AND b.yearid = t2.yearID AND b.yearid >= 1980 WHERE t1.team_name = ''{team1}'' AND t2.team_name = ''{team2}'' AND p.deathYear IS NULL"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM fielding f JOIN people p ON f.playerID = p.playerID WHERE f.yearID = {yearid} GROUP BY f.playerID, f.yearID HAVING SUM(f.f_GS) > 300"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM fielding f JOIN people p ON f.playerID = p.playerID WHERE f.yearID = {yearid} GROUP BY f.playerID, f.yearID HAVING SUM(f.f_DP) > 100"
                  "SELECT DISTINCT nameFirst || ' ' || nameLast FROM fielding f JOIN people p ON f.playerID = p.playerID WHERE f.yearID = {yearid} GROUP BY f.playerID, f.yearID HAVING SUM(f.f_PO) > 1000"
                  ]

home_run_questions = ["Name a player who played for {team1} and {team2} and {team3}"
                      "What team has the most total Home Runs"
                      "What team has the most total Stolen Bases"
                      "What team has the most total Wins"
                      "What team has the most total Losses"
                      "What team has the most total Shutouts"
                      "What team has the most total Hits"
                      "Name the batter who has the most Sacrifice hits in a season of all time"
                      "Name the batter who has the most Strikeouts in a season of all time"
                      "Name the batter who has the most Sacrifice Flies in a season of all time"
                      "Name the batter who has the most Hits by Pitch in a season of all time"
                      "Name the pither with the most hit-by-pitch in a season of all time"
                      "Name the pitcher with the most pitching stints"
                      "Name the fielding player with the most putouts in a season of all time"
                      "Name the fielding player who has the most caught stealing in a season of all time"
                      "Name the fielding player with more than 100 errors in a season"
                      "Name a player who has won the {award1} award and the {award2} award"
                    ]
home_run_sql = ["SELECT DISTINCT p.nameFirst || ' ' || p.nameLast FROM batting a JOIN batting b ON a.playerID = b.playerID JOIN batting c ON a.playerID = c.playerID JOIN people p ON a.playerID = p.playerID JOIN teams t1 ON a.teamid = t1.teamID AND a.yearid = t1.yearID AND a.yearid >= 1950 JOIN teams t2 ON b.teamid = t2.teamID AND b.yearid = t2.yearID AND b.yearid >= 1950 JOIN teams t3 ON c.teamid = t3.teamID AND c.yearid = t3.yearID AND c.yearid >= 1950 WHERE t1.team_name = '{team1}' AND t2.team_name = '{team2}' AND t3.team_name = '{team3}'"
                "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_HR) DESC LIMIT 1"
                "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_SB) DESC LIMIT 1"
                "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_W) DESC LIMIT 1"
                "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_L) DESC LIMIT 1"
                "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_SHO) DESC LIMIT 1"
                "SELECT team_name FROM teams GROUP BY teamid ORDER BY SUM(team_H) DESC LIMIT 1"
                "Select name FROM JeopardyValues WHERE type = 'batting_500' AND idx = 0"
                "Select name FROM JeopardyValues WHERE type = 'batting_500' AND idx = 1"
                "Select name FROM JeopardyValues WHERE type = 'batting_500' AND idx = 2"
                "Select name FROM JeopardyValues WHERE type = 'batting_500' AND idx = 3"
                "SELECT nameFirst || ' ' || nameLast FROM pitching p JOIN people pe ON p.playerID = pe.playerID GROUP BY p.playerID, p.yearID ORDER BY SUM(p.p_HBP) DESC LIMIT 1"
                "SELECT nameFirst || ' ' || nameLast FROM pitching p JOIN people pe ON p.playerID = pe.playerID GROUP BY p.playerID ORDER BY COUNT(DISTINCT p.yearID) DESC LIMIT 1"
                "Select name FROM JeopardyValues WHERE type = 'fielding_500' AND idx = 0"
                "Select name FROM JeopardyValues WHERE type = 'fielding_500' AND idx = 1"
                "Select name FROM JeopardyValues WHERE type = 'fielding_500' AND idx = 2"
                "SELECT DISTINCT nameFirst || ' ' || nameLast FROM people p JOIN awards a1 ON p.playerID = a1.playerID AND a1.awardID = '{award1}' JOIN awards a2 ON p.playerID = a2.playerID AND a2.awardID = '{award2}'"
]

baseball_questions = {
    'first_base': {
        'questions': first_base_questions,
        'sql': first_base_sql
    },
    'second_base': {
        'questions': second_base_questions,
        'sql': second_base_sql
    },
    'third_base': {
        'questions': third_base_questions,
        'sql': third_base_sql
    },
    'home_run': {
        'questions': home_run_questions,
        'sql': home_run_sql
    }
}

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
        'HomeRun': {
            "question" : "",
            "answers" : [],
        },
    }