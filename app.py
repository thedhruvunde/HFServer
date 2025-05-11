from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

# Database initialization
def init_db():
    with sqlite3.connect("users.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
        conn.commit()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = pbkdf2_sha256.hash(request.form['password'])

        with sqlite3.connect("users.db") as conn:
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "User already exists."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username=?", (username,))
            row = cursor.fetchone()
            if row and pbkdf2_sha256.verify(password, row[0]):
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return "Invalid credentials."
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    lights = 'OFF'
    fans = 'OFF'

    if request.method == 'POST':
        lights = request.form.get('lights', 'OFF')
        fans = request.form.get('fans', 'OFF')

    return render_template('dashboard.html', username=session['username'], lights=lights, fans=fans)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
