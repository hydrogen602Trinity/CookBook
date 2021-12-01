from models import Ingredient, Recipe, User
import restapi
from typing import Optional
from flask import Flask
from flask_cors import CORS


from database import db
from login import login_manager, setup
import views
from util import getenv
import csv


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
    

        user1 = User('Max Mustermann', 'max.mustermann@t-online.de', 'postgres')
        db.session.add(user1)
        db.session.commit()

        db.session.add(User('Jonathan Rotter', 'jrotter@trinity.edu', 'postgres', is_admin=True))
        db.session.commit()

        db.session.add(User('Vasti Rios Rios', 'vriosrio@trinity.edu', 'postgres'))
        db.session.commit()

        db.session.add(User('Garrett Isaacs', 'gissacs@trinity.edu', 'postgres'))
        db.session.commit()


        cornbread = Recipe('Cornbread', 'Instructions Go Here', [
            Ingredient('Butter', '1/4', 'cup'), Ingredient('Milk', 1, 'cup'), Ingredient('Eggs', 1), Ingredient('Cornmeal', '5/4', 'cup'),
            Ingredient('Flour', 1, 'cup'), Ingredient('Sugar', '1/2', 'cup'), Ingredient('Baking Powder', 1, 'tbsp'), Ingredient('Salt', 1, 'tsp')
        ], user1, 'Side Dish', 'Basic', 40, 2)

        db.session.add(cornbread)
        db.session.commit()

        blueberryPie = Recipe('Blueberry Pie', 'Instructions Go Here', [
            Ingredient('Flour', '9/4', 'cup'), Ingredient('Salt', 1, 'tsp'), Ingredient('Shortening', '2/3', 'cup'), Ingredient('Sugar', '1/2', 'cup'),
            Ingredient('Cinnamon', '1/2', 'tsp'), Ingredient('Blueberries', 6, 'cup'), Ingredient('Butter', 1, 'tbsp')
        ], user1, 'Dessert', 'Basic', 120, 2)

        db.session.add(blueberryPie)
        db.session.commit()

        frenchToast = Recipe('French Toast', 'Instructions Go Here', [
            Ingredient('Cinnamon', 1, 'tsp'), Ingredient('Nutmeg', '1/4', 'tsp'), Ingredient('Sugar', 2, 'tbsp'), Ingredient('Butter', 4, 'tbsp'),
            Ingredient('Eggs', 4), Ingredient('Vanilla Extract', '1/2', 'tsp'), Ingredient('Bread', 8, 'slices'), Ingredient('Maple Syrup', '1/2', 'cup')
        ], user1, 'Breakfast', 'French', 10, 1)

        db.session.add(frenchToast)
        db.session.commit()

        pretzelSticks = Recipe('Pretzel Sticks', 'Instructions Go Here', [
            Ingredient('Brown Sugar', '1/2', 'cup'), Ingredient('Dry Yeast', 2, 'envelopes'), Ingredient('Vegetable Oil', '11/4', 'cup'),
            Ingredient('Flour', '23/4', 'cup'), Ingredient('Baking Soda', '3/4', 'cup'), Ingredient('Eggs', 1), Ingredient('Salt', 2, 'tsp')
        ], user1, 'Snack', 'Basic', 60, 3)

        db.session.add(pretzelSticks)
        db.session.commit()

        swedishMeatballs = Recipe('Swedish Meatballs', 'Instructions Go Here', [
            Ingredient('Butter', 4, 'tsp'), Ingredient('Onion', '1/2'), Ingredient('Milk', '1/4', 'cup'), Ingredient('Bread', 3, 'slices'),
            Ingredient('Eggs', 1), Ingredient('Ground Beef', '3/4', 'lb'), Ingredient('Ground Pork', '1/2', 'lb'), Ingredient('Salt', 1, 'tsp'),
            Ingredient('Black Pepper', 1, 'tsp'), Ingredient('Nutmed', '1/2', 'tsp'), Ingredient('Ground Cardamom', 1/2, 'tsp'),
            Ingredient('Flour', 3, 'tbsp'), Ingredient('Beef Stock', 2, 'cup'), Ingredient('Sourcream', '1/4', 'cup')
        ], user1, 'Main Dish', 'Swedish', 90, 5)

        db.session.add(swedishMeatballs)
        db.session.commit()

        #print(recipe.ingredients)
        # print('all:', Ingredient.query.all())

        # Create Tags
        spicyTag = Tag('Spicy')
        db.session.add(spicyTag)
        mildTag = Tag('Mild')
        db.session.add(mildTag)
        vegetarianTag = Tag('Vegetarian')
        db.session.add(vegetarianTag)

        db.session.commit()

        # Name = 0
        # Rating = 1
        # Difficulty = 2 , Super Simple, Fairly Easy, Average, Hard, Very Difficult
        # Notes = 3
        # Course Type = 4
        # Prep Time = 5
        # Ingredients = 9 , in double quotes or alone if single ingredient
        with open('data_source/data_recipes.csv') as csvfile:
            line_count = 0
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader:
                if line_count > 0:
                    # print(line_count)
                    line_count += 1
                    name = f"{row[0]}"
                    rating = len(f"{row[1]}")
                    diff_string = f"{row[2]}"
                    difficulty = 0
                    if diff_string == "Super Simple":
                        difficulty = 1
                    elif diff_string == "Fairly Easy":
                        difficulty = 2
                    elif diff_string == "Average":
                        difficulty = 3
                    elif diff_string == "Hard":
                        difficulty = 4
                    else:
                        difficulty = 5
                    notes = f"{row[3]}"
                    courseType = f"{row[4]}"
                    prepTime = 60
                    if f"{row[5]}" != '':
                        prepTime = int(row[5])
                    ingredients_string = f"{row[9]}"
                    ingredients_list = ingredients_string.split(",")
                    ingredients = []
                    for string in ingredients_list:
                        ingredients.append(Ingredient(string, 1))
                        #ingredAndAmts = string.split("-")
                        #if len(ingredAndAmts) >= 3:
                        #    ingredients.append(Ingredient(ingredAndAmts[0], ingredAndAmts[1], ingredAndAmts[2]))
                        #elif len(ingredAndAmts) == 2:
                        #    ingredients.append(Ingredient(ingredAndAmts[0], ingredAndAmts[1]))
                        #else: 
                        #    ingredients.append(Ingredient(ingredAndAmts[0], 1))
                    style = "N/A"
                    # print(name,", ",notes,", ",courseType,", ",style,", ",prepTime,", ",difficulty,", ",rating)
                    newThing = Recipe(name, notes, ingredients, user1, courseType, style, prepTime, difficulty, rating)
                    db.session.add(newThing)
                    db.session.commit()
                else: line_count += 1

        print('all:', Recipe.query.all())

def addTags(app: Flask, recipe_id: int, tagName: str, tagID: Optional[int] = None):
    with app.app_context():
        print("Hello World")


def create_app(testing: bool = False, db_name: Optional[str] = None) -> Flask:
    app = CustomFlask(__name__)

    app.register_blueprint(views.core)
    app.register_blueprint(restapi.api_blueprint, url_prefix='/api/v1')

    # for dev only
    app.secret_key = '8ccfee32156953a4aedc1cfcefdf5aa0124d091d381f4008cc13d33de5bf2c1c'

    CORS(app, supports_credentials=True)

    login_manager.init_app(app)
    setup(app)

    db_name = db_name if db_name else getenv('DB_FILENAME') # +psycopg2
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:postgres@localhost:5432/{db_name}"
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
