from flask import Flask, render_template, request
from os import getenv

from database import db
from models import Note
import views


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # default collides with Vue.js
        variable_end_string='%%',
    ))

app = CustomFlask(__name__)

app.register_blueprint(views.core)
app.register_blueprint(views.api, url_prefix='/api/v1')

SQLALCHEMY_DATABASE_URI = "sqlite:///{dbfile}".format(
    dbfile='test.db'
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
# app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def setup_database(app):
    with app.app_context():
        db.create_all()
    
        note = Note('Test a b c')
        db.session.add(note)
        db.session.commit()


init_db = getenv('INIT_DB')
if init_db and init_db.strip() == '1':
    setup_database(app) 


print(app.url_map)
