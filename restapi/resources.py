from fractions import Fraction
from typing import Optional
from flask.json import jsonify
from flask_restful import Resource, Api, reqparse
from flask import Blueprint
from flask_login import current_user
from datetime import date
from werkzeug.security import generate_password_hash

from models import Ingredient, Recipe, db, User, Meal
from restapi.auth_util import require_admin, require_auth
from .util import optional_param_check, require_keys_with_set_types, require_truthy_values, handle_nonexistance, add_resource


api_blueprint = Blueprint(
                 __name__.split('.', maxsplit=1)[1],
                 __name__,
                 template_folder='../templates'
                )


api = Api(api_blueprint)


@add_resource(api, '/recipe', '/recipe/<int:recipe_id>')
class RecipeResource(Resource):

    recipe_parser = reqparse.RequestParser()
    recipe_parser.add_argument('name', type=str, help='Recipe name')
    recipe_parser.add_argument('notes', type=str, help='Recipe notes & instructions')
    recipe_parser.add_argument('ingredients', default=[], location='json', type=list)

    updated_recipe_parser = recipe_parser.copy()
    updated_recipe_parser.add_argument('id', type=int, default=None, help="Recipe ID")

    ingredient_requirements = {
        'name': str,
        'num': int,
        'denom': int,
    }

    @require_auth
    @optional_param_check(False, 'recipe_id')
    def post(self, _=None):
        data = require_truthy_values(self.recipe_parser.parse_args(), exceptions=('ingredients',))

        ingredients = []
        for ingredient in data['ingredients']:
            ingredient = require_keys_with_set_types(self.ingredient_requirements, ingredient)
            ingredients.append(Ingredient(ingredient['name'], 
                                          Fraction(ingredient['num'], 
                                                   ingredient['denom']),
                                          ingredient.get('unit') or None))


        newRecipe = Recipe(data['name'], data['notes'], ingredients, current_user)
        db.session.add(newRecipe)
        db.session.commit()
        return '', 201

    @require_auth
    @optional_param_check(False, 'recipe_id')
    def put(self, _=None):
        data = require_truthy_values(self.updated_recipe_parser.parse_args(), exceptions=('ingredients', 'id'))

        ingredients = []
        for ingredient in data['ingredients']:
            ingredient = require_keys_with_set_types(self.ingredient_requirements, ingredient)
            ingredients.append(Ingredient(ingredient['name'], 
                                            Fraction(ingredient['num'], 
                                                    ingredient['denom']),
                                            ingredient.get('unit') or None))
        # or None converts empty str to None

        if data['id'] is None:
            newRecipe = Recipe(data['name'], data['notes'], ingredients, current_user)
            db.session.add(newRecipe)
            db.session.commit()
            return f'{newRecipe.id}', 201

        recipe: Optional[Recipe] = db.session.query(Recipe).filter(Recipe.user_id == current_user.id, Recipe.id == data['id']).one_or_none()

        if recipe:
            recipe.name = data['name']
            recipe.notes = data['notes']
            recipe.ingredients = ingredients
            db.session.commit()
            return f'{recipe.id}', 200
        else:
            return f'No object found with recipe_id={data["id"]}', 404

    @require_auth
    def get(self, recipe_id: Optional[int] = None):
        q = db.session.query(Recipe).filter(Recipe.user_id == current_user.id)
        # sleep(20)  # simulate slow internet 
        if recipe_id:
            recipe = q.filter(Recipe.id == recipe_id).one_or_none()
            handle_nonexistance(recipe)
            return jsonify(recipe.toJson())
        else:
            # current_app.logger.debug('Getting all recipes')
            return jsonify([recipe.toJson() for recipe in q.filter(Recipe.deleted == False).all()])

    @require_auth
    @optional_param_check(True, 'recipe_id')
    def delete(self, recipe_id: Optional[int] = None):
        recipe: Optional[Recipe] = db.session.query(Recipe).filter(Recipe.user_id == current_user.id, Recipe.id == recipe_id).one_or_none()
        if recipe:
            recipe.deleted = True
            db.session.commit()
            return '', 204
        else:
            return f'No object found with recipe_id={recipe_id}', 404


@add_resource(api, '/account')
class AccountResource(Resource):

    user_parser = reqparse.RequestParser()
    user_parser.add_argument('name', type=str, help='User Name')
    user_parser.add_argument('email', type=str, help='User Email')
    user_parser.add_argument('password', type=str, help='User Password')

    def post(self):
        data = require_truthy_values(self.user_parser.parse_args())

        overlaps = db.session.query(User).filter(User.email == data['email']).count()
        if overlaps > 0:
            return f'Email already exists: email={data["email"]}', 400

        newUser = User(data['name'], data['email'], data['password'])
        db.session.add(newUser)
        db.session.commit()
        return '', 201

    @require_auth
    def put(self):
        data = self.user_parser.parse_args()

        user: User = current_user
        assert user.is_authenticated, 'Illegal State: User should be authenticated by this point'

        if data['email']:
            overlap = data['email'] != user.email and db.session.query(User).filter(User.email == data['email']).count() > 0
            if overlap > 0:
                return f'Email already exists: email={data["email"]}', 400
            user.email = data['email']

        if data['name']:
            user.name = data['name']

        if data['password']:
            user.password = generate_password_hash(data['password'], method='sha256')

        db.session.commit()
        return f'{user.id}', 200

    @require_auth
    def get(self):
        return jsonify(current_user.toJson())

    @require_auth
    def delete(self):
        db.session.delete(current_user)
        db.session.commit()
        return '', 204


@add_resource(api, '/meal', '/meal/<int:meal_id>')
class MealResource(Resource):

    meal_parser = reqparse.RequestParser()
    meal_parser.add_argument('label', type=str, help='Breakfast, Lunch, Dinner, etc.')
    meal_parser.add_argument('day', type=date.fromisoformat, help='Date')
    meal_parser.add_argument('user_id', type=int, help='Creator')
    meal_parser.add_argument('recipe_id', type=int, help='Recipe for the Meal')

    meal_parser_w_id = meal_parser.copy()
    meal_parser_w_id.add_argument('id', type=int, default=None, help="Meal ID")

    @optional_param_check(False, 'meal_id')
    def post(self, _=None):
        data = require_truthy_values(self.meal_parser.parse_args())

        newMeal = Meal(data['label'], data['day'], data['user_id'], data['recipe_id'])
        db.session.add(newMeal)
        db.session.commit()
        return '', 201

    @optional_param_check(False, 'meal_id')
    def put(self, _=None):
        data = require_truthy_values(self.meal_parser_w_id.parse_args(), exceptions=('id'))

        # Insert
        if data['id'] is None:
            newMeal = Meal(data['label'], data['day'], data['user_id'], data['recipe_id'])
            db.session.add(newMeal)
            db.session.commit()
            return f'{newMeal.id}', 201

        meal: Optional[Meal] = db.session.query(Meal).get(data['id'])

        # Update
        if meal:
            meal.label = data['label']
            meal.day = data['day']
            meal.user_id = data['user_id']
            meal.recipe_id = data['recipe_id']
            db.session.commit()
            return f'{meal.id}', 200
        else:
            return f'No object found with meal_id={data["id"]}', 404

    def get(self, meal_id: Optional[int] = None):
        # Search
        if meal_id:
            meal = db.session.query(Meal).get(meal_id)
            handle_nonexistance(meal)
            return jsonify(meal.toJson())
        else:
            return jsonify([meal.toJson() for meal in Meal.query.all()])

    @optional_param_check(True, 'meal_id')
    def delete(self, meal_id: Optional[int] = None):
        meal: Optional[Meal] = db.session.query(Meal).get(meal_id)
        if meal:
            db.session.delete(meal)
            db.session.commit()
            return '', 204
        else:
            return f'No object found with the meal_id={meal_id}', 404
