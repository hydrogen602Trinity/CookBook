from fractions import Fraction
from typing import Optional
from flask.json import jsonify
from flask_restful import Resource, Api, reqparse
from flask import Blueprint
from flask import current_app

from models import Ingredient, Recipe, db, User
from .util import optional_param_check, require_keys_with_set_types, require_truthy_values, handle_nonexistance, add_resource


api_blueprint = Blueprint(
                 __name__.split('.', maxsplit=1)[1], 
                 __name__,
                 template_folder='../templates'
                )


api = Api(api_blueprint)


# @add_resource(api, '/note', '/note/<int:note_id>')
# class NoteResource(Resource):

#     note_parser = reqparse.RequestParser()
#     note_parser.add_argument('note', type=str, help='The content of the note')

#     @optional_param_check(False, 'note_id')
#     def post(self, _=None):
#         data = require_truthy_values(self.note_parser.parse_args())

#         newNote = Note(data['note'])
#         db.session.add(newNote)
#         db.session.commit()
#         return '', 201

#     def get(self, note_id: Optional[int] = None):
#         if note_id:
#             note = db.session.query(Note).get(note_id)
#             handle_nonexistance(note)
#             return jsonify(note.toJson())
#         else:
#             return jsonify([note.toJson() for note in Note.query.all()])


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

        user = db.session.query(User).filter(User.name == 'Max Mustermann').all()[0]
        newRecipe = Recipe(data['name'], data['notes'], ingredients, user)
        db.session.add(newRecipe)
        db.session.commit()
        return '', 201
    
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
            user = db.session.query(User).filter(User.name == 'Max Mustermann').all()[0]
            newRecipe = Recipe(data['name'], data['notes'], ingredients, user)
            db.session.add(newRecipe)
            db.session.commit()
            return f'{newRecipe.id}', 201
        
        recipe: Optional[Recipe] = db.session.query(Recipe).get(data['id'])
        
        if recipe:
            recipe.name = data['name']
            recipe.notes = data['notes']
            recipe.ingredients = ingredients
            db.session.commit()
            return f'{recipe.id}', 200
        else:
            return f'No object found with recipe_id={data["id"]}', 404

    def get(self, recipe_id: Optional[int] = None):
        # sleep(20)  # simulate slow internet 
        if recipe_id:
            recipe = db.session.query(Recipe).get(recipe_id)
            handle_nonexistance(recipe)
            return jsonify(recipe.toJson())
        else:
            # current_app.logger.debug('Getting all recipes')
            return jsonify([recipe.toJson() for recipe in Recipe.query.filter(Recipe.deleted == False).all()])

    @optional_param_check(True, 'recipe_id')
    def delete(self, recipe_id: Optional[int] = None):
        recipe: Optional[Recipe] = db.session.query(Recipe).get(recipe_id)
        if recipe:
            recipe.deleted = True
            db.session.commit()
            return '', 204
        else:
            return f'No object found with recipe_id={recipe_id}', 404


@add_resource(api, '/user', '/user/<int:user_id>')
class UserResource(Resource):

    user_parser = reqparse.RequestParser()
    user_parser.add_argument('name', type=str, help='User Name')
    user_parser.add_argument('email', type=str, help='User Email')
    user_parser.add_argument('password', type=str, help='User Password')

    user_parser_w_id = user_parser.copy()
    user_parser_w_id.add_argument('id', type=int, default=None, help="User ID")

    @optional_param_check(False, 'user_id')
    def post(self, _=None):
        data = require_truthy_values(self.user_parser.parse_args())

        overlaps = db.session.query(User).filter(User.email == data['email']).count()
        if overlaps > 0:
            return f'Email already exists: email={data["email"]}', 400

        newUser = User(data['name'], data['email'], data['password'])
        db.session.add(newUser)
        db.session.commit()
        return '', 201
    
    @optional_param_check(False, 'user_id')
    def put(self, _=None):
        data = require_truthy_values(self.user_parser_w_id.parse_args(), exceptions=('id'))

        if data['id'] is None:
            overlaps = db.session.query(User).filter(User.email == data['email']).count()
            if overlaps > 0:
                return f'Email already exists: email={data["email"]}', 400
            
            newUser = User(data['name'], data['email'], data['password'])
            db.session.add(newUser)
            db.session.commit()
            return f'{newUser.id}', 201
        
        user: Optional[User] = db.session.query(User).get(data['id'])
        
        if user:
            overlap = data['email'] != user.email and db.session.query(User).filter(User.email == data['email']).count() > 0
            if overlap > 0:
                return f'Email already exists: email={data["email"]}', 400
            user.name = data['name']
            user.email = data['email']
            user.password = data['password']
            db.session.commit()
            return f'{user.id}', 200
        else:
            return f'No object found with user_id={data["id"]}', 404

    def get(self, user_id: Optional[int] = None):
        # sleep(20)  # simulate slow internet 
        if user_id:
            recipe = db.session.query(User).get(user_id)
            handle_nonexistance(recipe)
            return jsonify(recipe.toJson())
        else:
            # current_app.logger.debug('Getting all recipes')
            return jsonify([user.toJson() for user in User.query.all()])

    @optional_param_check(True, 'user_id')
    def delete(self, user_id: Optional[int] = None):
        user: Optional[User] = db.session.query(User).get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return '', 204
        else:
            return f'No object found with user_id={user_id}', 404
