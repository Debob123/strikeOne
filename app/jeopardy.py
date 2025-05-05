from app import db, login_manager, bcrypt
import random


from sqlalchemy import text, func


categories = {}
stored_answers = []

def store_question_answers():

    team_data = {}
    people_teams_data = {}
    batting_data = {}
    pitching_data = {}
    fielding_data = {}
    awards_data = {}


    for level in [100, 200, 300, 400, 500]:
        sql = f"Select * from jeopardyquestions WHERE JeoId = 'teams_{level}' Order BY JeoNum ASC"
        fortnite = db.session.execute(text(sql)).fetchall()

        # Initialize the lists for the current level
        current_questions = []
        current_sql = []

        # Populate the lists for current level
        for fort in fortnite:
            current_questions.append(fort.JeoQuestion)
            current_sql.append(fort.JeoSQL)

        # Assign the lists to the main data structure
        team_data[level] = {
            'questions': current_questions,
            'sql': current_sql
        }





    for level in [100, 200, 300, 400, 500]:
        sql = f"Select * from jeopardyquestions WHERE JeoId = 'people_teams_{level}' Order BY JeoNum ASC"
        fortnite = db.session.execute(text(sql)).fetchall()

        # Initialize the lists for the current level
        current_questions = []
        current_sql = []

        # Populate the lists for current level
        for fort in fortnite:
            current_questions.append(fort.JeoQuestion)
            current_sql.append(fort.JeoSQL)

        # Assign the lists to the main data structure
        people_teams_data[level] = {
            'questions': current_questions,
            'sql': current_sql
        }


    for level in [100, 200, 300, 400, 500]:
        sql = f"Select * from jeopardyquestions WHERE JeoId = 'batting_{level}' Order BY JeoNum ASC"
        fortnite = db.session.execute(text(sql)).fetchall()

        # Initialize the lists for the current level
        current_questions = []
        current_sql = []

        # Populate the lists for current level
        for fort in fortnite:
            current_questions.append(fort.JeoQuestion)
            current_sql.append(fort.JeoSQL)

        # Assign the lists to the main data structure
        batting_data[level] = {
            'questions': current_questions,
            'sql': current_sql
        }



    for level in [100, 200, 300, 400, 500]:
        sql = f"Select * from jeopardyquestions WHERE JeoId = 'pitching_{level}' Order BY JeoNum ASC"
        fortnite = db.session.execute(text(sql)).fetchall()

        # Initialize the lists for the current level
        current_questions = []
        current_sql = []

        # Populate the lists for current level
        for fort in fortnite:
            current_questions.append(fort.JeoQuestion)
            current_sql.append(fort.JeoSQL)

        # Assign the lists to the main data structure
        pitching_data[level] = {
            'questions': current_questions,
            'sql': current_sql
        }


    for level in [100, 200, 300, 400, 500]:
        sql = f"Select * from jeopardyquestions WHERE JeoId = 'fielding_{level}' Order BY JeoNum ASC"
        fortnite = db.session.execute(text(sql)).fetchall()

        # Initialize the lists for the current level
        current_questions = []
        current_sql = []

        # Populate the lists for current level
        for fort in fortnite:
            current_questions.append(fort.JeoQuestion)
            current_sql.append(fort.JeoSQL)

        # Assign the lists to the main data structure
        fielding_data[level] = {
            'questions': current_questions,
            'sql': current_sql
        }


    for level in [100, 200, 300, 400, 500]:
        sql = f"Select * from jeopardyquestions WHERE JeoId = 'awards_{level}' Order BY JeoNum ASC"
        fortnite = db.session.execute(text(sql)).fetchall()

        # Initialize the lists for the current level
        current_questions = []
        current_sql = []

        # Populate the lists for current level
        for fort in fortnite:
            current_questions.append(fort.JeoQuestion)
            current_sql.append(fort.JeoSQL)

        # Assign the lists to the main data structure
        awards_data[level] = {
            'questions': current_questions,
            'sql': current_sql
        }


    categories = {
        "Teams": team_data,
        "People_Teams": people_teams_data,
        "Batting": batting_data,
        "Pitching": pitching_data,
        "Fielding": fielding_data,
        "Awards": awards_data
    }

    return categories


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