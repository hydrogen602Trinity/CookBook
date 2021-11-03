from models import Ingredient, Recipe
import restapi
from typing import Optional
from flask import Flask
from flask_cors import CORS


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

        recipe = Recipe('Scrambled Eggs', 'Remove egg shell from egg. Put liquid part of egg into bowl and beat with fork. Add salt and pour into a hot pan with a little oil. Let cook until somewhat solid, then break into lots of little bits and cook until fully solid', [
            Ingredient('eggs', 2),
            Ingredient('salt', 1/8, 'tsp')
        ])

        db.session.add(recipe)
        db.session.commit()

        recipe2 = Recipe('Boiled Eggs', 'Bring water to a boil. Put eggs into water and let cook in boiling water for some minutes. Idk how many.', [
            Ingredient('eggs', 2)
        ])

        db.session.add(recipe2)
        db.session.commit()

        print(recipe.ingredients)

        print('all:', Ingredient.query.all())


def create_app(testing: bool = False, db_uri: Optional[str] = None) -> Flask:
    app = CustomFlask(__name__)

    app.register_blueprint(views.core)
    app.register_blueprint(restapi.api_blueprint, url_prefix='/api/v1')

    CORS(app)

    SQLALCHEMY_DATABASE_URI = db_uri if db_uri else f"postgresql:///{getenv('DB_FILENAME')}"
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    # app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['TESTING'] = testing
    app.config["SERVER_NAME"] =  "localhost:5000" #'192.168.178.67:5000'  #
    app.config["APPLICATION_ROOT"] = "/"
    if testing:
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

    db.init_app(app)
    # app.logger.info(f'DB: {app.config["SQLALCHEMY_DATABASE_URI"]}')

    if not testing:
        init_db = getenv('INIT_DB')
        if init_db and init_db.strip() == '1':
            setup_database(app)
    
    # app.logger.info(app.url_map)

    return app
