from flask import Flask
from flask_login import LoginManager
from heroku_flask_auth_app.models import db, User
from heroku_flask_auth_app.routes import bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(bp)

with app.app_context():
    db.create_all()
