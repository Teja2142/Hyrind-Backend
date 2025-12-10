import sqlite3, json, os
DB='db.sqlite3'
if not os.path.exists(DB):
    print('NO_DB')
else:
    c=sqlite3.connect(DB)
    cur=c.cursor()
    cur.execute("PRAGMA table_info('recruiters_recruiter')")
    rows=cur.fetchall()
    print(json.dumps(rows, indent=2))
