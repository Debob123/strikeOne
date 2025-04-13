import csv
from app import db
from app.models import NoHitter  # or wherever your model is
from datetime import datetime

def str_to_bool(s):
    return s.strip() == '1'

with open('pitching.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            nohitter = NoHitter(
                gid=row['gid'],
                pitcher_id=row['id'],
                team=row['team'],
                opp=row['opp'],
                date=row['date'],
                site=row['site'] or None,
                vishome=row['vishome'],

                p_ipouts=int(row['p_ipouts']) if row['p_ipouts'] else 0,
                p_bfp=int(row['p_bfp']) if row['p_bfp'] else None,
                p_h=int(row['p_h']) if row['p_h'] else 0,
                p_hr=int(row['p_hr']) if row['p_hr'] else 0,
                p_r=int(row['p_r']) if row['p_r'] else 0,
                p_er=int(row['p_er']) if row['p_er'] else 0,
                p_w=int(row['p_w']) if row['p_w'] else 0,
                p_k=int(row['p_k']) if row['p_k'] else 0,
                p_hbp=int(row['p_hbp']) if row['p_hbp'] else 0,
                p_wp=int(row['p_wp']) if row['p_wp'] else 0,
                p_gs=int(row['p_gs']) if row['p_gs'] else 0,
                p_cg=int(row['p_cg']) if row['p_cg'] else 0,

                team_win=str_to_bool(row['win']),
            )

            db.session.add(nohitter)
        except Exception as e:
            print(f"Skipping row due to error: {e}\nRow: {row}")

    db.session.commit()
    print("Data import complete.")
