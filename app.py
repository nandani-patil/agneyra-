from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "mysecretkey"

# ---------------- DATABASE FUNCTION ----------------
def get_db():
    return sqlite3.connect('users.db')

# ---------------- CREATE TABLE ----------------
conn = get_db()
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
''')
conn.commit()
conn.close()

# ---------------- HASH PASSWORD ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM users WHERE username=? AND password=?',
            (username, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            conn.commit()
            conn.close()

            session['user'] = username
            return redirect('/dashboard')
        except:
            error = 'User already exists'

    return render_template('register.html', error=error)

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html', user=session['user'])

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)
