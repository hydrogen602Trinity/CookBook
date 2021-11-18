from flask_login import LoginManager
from database import db

login_manager = LoginManager()

__has_setup = False
def setup(app):
    from models import User

    global __has_setup, load_user
    if __has_setup:
        raise RuntimeError('Initialized login manager twice')
    __has_setup = True

    @login_manager.user_loader
    def load_user(user_id: str):
        with app.app_context():
            return db.session.query(User).get(int(user_id))
            # q = db.session.query(User).filter(User.email == user_id)
            # if q.count() == 0:
            #     return None
            # return q.one()