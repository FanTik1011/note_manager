from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # заміни на випадковий рядок
DATABASE = 'users.db'

# --- Ініціалізація бази даних ---
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# --- Отримати з'єднання з БД ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Головна сторінка ---
@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', username=session['username'])

# --- Реєстрація ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            db = get_db()
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Ім’я користувача вже зайняте!"
    return render_template('register.html')

# --- Логін ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Якщо адмін
        if username == 'vovk1011' and password == 'wertyalnuu':
            session['username'] = username
            session['is_admin'] = True
            return redirect(url_for('admin'))

        # Якщо звичайний користувач
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
            session['username'] = username
            session['is_admin'] = False
            return redirect(url_for('home'))
        else:
            return "Невірний логін або пароль"
    return render_template('login.html')

# --- Адмін-панель ---
@app.route('/admin')
def admin():
    if 'username' in session and session.get('is_admin'):
        db = get_db()
        users = db.execute("SELECT id, username FROM users").fetchall()
        return render_template('admin.html', users=users)
    return redirect(url_for('login'))

# --- Вихід ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Запуск ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
