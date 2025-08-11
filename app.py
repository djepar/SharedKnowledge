from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_FILE = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user' in session:
        return render_template('home.html', name=session['user'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE name=? AND password=?", (name, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = name
            return redirect(url_for('index'))
        else:
            return "Login Failed"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/dashboard')
def dashboard():
    # to change was just place holder information
    data = {
        'user_count': 150,
        'sales_today': 1250.50,
        'active_sessions': 23
    }
    return render_template('dashboard.html', **data)
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)
