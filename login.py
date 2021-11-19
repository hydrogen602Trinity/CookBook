from sys import stderr
from flask_login import LoginManager
from database import db

login_manager = LoginManager()

__has_setup = False
def setup(app):
    from models import User

    global __has_setup, load_user
    if __has_setup:
        print('Initialized login manager twice', file=stderr)
    __has_setup = True

    @login_manager.user_loader
    def load_user(user_id: str):
        with app.app_context():
            return db.session.query(User).get(int(user_id))
