import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///notes.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('notes', lazy=True))

@app.route('/')
def index():
    return redirect('/dashboard') if 'user_id' in session else redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = generate_password_hash(password)
        user = User(username=username, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect('/dashboard')
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        content = request.form['content']
        note = Note(content=content, user_id=session['user_id'])
        db.session.add(note)
        db.session.commit()

    if session.get('is_admin'):
        notes = Note.query.all()
    else:
        notes = Note.query.filter_by(user_id=session['user_id']).all()

    return render_template('dashboard.html', notes=notes, is_admin=session.get('is_admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.cli.command('init-db')
def init_db():
    db.create_all()
    print("Database initialized.")

@app.cli.command('create-admin')
def create_admin():
    from getpass import getpass
    username = input("Admin username: ")
    password = getpass("Admin password: ")
    hashed = generate_password_hash(password)
    admin = User(username=username, password_hash=hashed, is_admin=True)
    db.session.add(admin)
    db.session.commit()
    print("Admin created.")

if __name__ == '__main__':
    app.run(debug=True)
