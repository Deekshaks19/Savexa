import os
import sqlite3
import json

injuries = [
    'Dog Bite', 'Cat Bite', 'Animal Bite', 'Bee Sting', 'Insect Bite',
    'Burn', '1st Degree Burn', '2nd Degree Burn', '3rd Degree Burn',
    'Cut', 'Minor Cut', 'Deep Cut', 'Minor Fracture', 'Fracture',
    'Sprain', 'Swelling', 'Nosebleed', 'Eye Irritation', 'Skin Infection'
]

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(root, 'db.sqlite3')
print('DB path:', db_path)
conn = sqlite3.connect(db_path)
cur = conn.cursor()
for injury in injuries:
    print('\n===', injury, '===')
    cur.execute('SELECT summary, steps FROM api_firstaidguidance WHERE injury_type = ?', (injury,))
    row = cur.fetchone()
    if not row:
        print('MISSING')
        continue
    summary, steps = row
    try:
        steps = json.loads(steps)
    except Exception:
        steps = steps
    print('Summary:', summary)
    print('First step:', steps[0] if steps else 'None')
    print('Total steps:', len(steps) if isinstance(steps, list) else 'unknown')
conn.close()