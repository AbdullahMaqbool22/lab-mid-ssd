from flask import Flask, g, render_template, request, redirect, url_for
import sqlite3
import os
from markupsafe import Markup
import bleach

DB_PATH = os.path.join(os.path.dirname(__file__), 'patched_blog.db')
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'prod-patched'

ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li']
ALLOWED_ATTRS = {'a': ['href', 'title', 'rel']}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    posts = db.execute('SELECT id, title FROM posts ORDER BY id DESC').fetchall()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_view(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id=?', (post_id,)).fetchone()
    if not post:
        return 'Not found', 404
    # SAFE: do not render user input as a template.
    # Sanitize allowed HTML and then mark as safe.
    cleaned = bleach.clean(post['content'], tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    safe_content = Markup(cleaned)
    return render_template('post.html', post=post, safe_content=safe_content)

@app.route('/create', methods=('GET','POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db = get_db()
        db.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
        db.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

if __name__ == '__main__':
    app.run(host=0.0.0.0, port=5001, debug=False)
