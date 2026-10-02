import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
print('DB:', db_path)
conn = sqlite3.connect(db_path)
cur = conn.cursor()
for injury in ['Dog Bite', 'Cat Bite', 'Animal Bite', 'Bee Sting', 'Insect Bite', 'Burn', 'Cut', 'Minor Wound']:
    cur.execute('SELECT summary, steps FROM api_firstaidguidance WHERE injury_type = ?', (injury,))
    row = cur.fetchone()
    print('\n===', injury, '===')
    if not row:
        print('MISSING')
        continue
    summary, steps = row
    print('Summary:', summary)
    print('Steps count:', len(steps))
    for i, step in enumerate(steps, 1):
        print(f'{i}. {step}')
conn.close()