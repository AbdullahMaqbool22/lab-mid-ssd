import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'vuln_blog.db')
if os.path.exists(DB_PATH):
    print('DB exists — delete to recreate')
    raise SystemExit

with sqlite3.connect(DB_PATH) as conn:
    conn.executescript('''
    CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    );
    INSERT INTO posts (title, content) VALUES
      ('Welcome', 'This is an intentionally vulnerable blog. Try posting {{7*7}}'),
      ('About', 'Demonstration only.');
    ''')
print('DB created at', DB_PATH)