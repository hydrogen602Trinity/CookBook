from models.note import Ingredient, Recipe
import restapi
from typing import Optional
from flask import Flask, render_template, request

from database import db
from models import Note
import views
from util import getenv


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # default collides with Vue.js
        variable_end_string='%%',
    ))


def setup_database(app: Flask):
    with app.app_context():
        db.drop_all()
        db.create_all()
    
        note = Note('Test a b c')
        db.session.add(note)
        db.session.commit()

        recipe = Recipe()
        db.session.add(recipe)
        db.session.commit()

        ing = Ingredient(recipe.id, 'eggs')
        db.session.add(ing)
        db.session.commit()

        ing = Ingredient(recipe.id, 'salt')
        db.session.add(ing)
        db.session.commit()

        print(recipe.ingredient_ids)
        print(ing.recipe.id)

        print('all:', Ingredient.query.all())

        db.session.delete(recipe)
        db.session.commit()

        print('all:', Ingredient.query.all())


def create_app(testing: bool = False, db_uri: Optional[str] = None) -> Flask:
    app = CustomFlask(__name__)

    app.register_blueprint(views.core)
    app.register_blueprint(restapi.api_blueprint, url_prefix='/api/v1')

    SQLALCHEMY_DATABASE_URI = db_uri if db_uri else f"sqlite:///{getenv('DB_FILENAME')}"
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    # app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['TESTING'] = testing
    app.config["SERVER_NAME"] = "localhost:5000"
    app.config["APPLICATION_ROOT"] = "/"
    if testing:
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

    db.init_app(app)

    if not testing:
        init_db = getenv('INIT_DB')
        if init_db and init_db.strip() == '1':
            setup_database(app)

    return app
