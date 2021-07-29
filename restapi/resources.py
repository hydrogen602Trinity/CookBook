from fractions import Fraction
from typing import Optional
from flask.json import jsonify
from flask_restful import Resource, Api, reqparse
from flask import Blueprint
from time import sleep

from models import Ingredient, Note, Recipe, db
from .util import optional_param_check, require_keys_with_set_types, require_truthy_values, handle_nonexistance, add_resource


api_blueprint = Blueprint(
                 __name__.split('.', maxsplit=1)[1], 
                 __name__,
                 template_folder='../templates'
                )


api = Api(api_blueprint)


@add_resource(api, '/note', '/note/<int:note_id>')
class NoteResource(Resource):

    note_parser = reqparse.RequestParser()
    note_parser.add_argument('note', type=str, help='The content of the note')

    @optional_param_check(False, 'note_id')
    def post(self, _=None):
        data = require_truthy_values(self.note_parser.parse_args())

        newNote = Note(data['note'])
        db.session.add(newNote)
        db.session.commit()
        return '', 201

    def get(self, note_id: Optional[int] = None):
        if note_id:
            note = db.session.query(Note).get(note_id)
            handle_nonexistance(note)
            return jsonify(note.toJson())
        else:
            return jsonify([note.toJson() for note in Note.query.all()])


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

        newRecipe = Recipe(data['name'], data['notes'], ingredients)
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
            newRecipe = Recipe(data['name'], data['notes'], ingredients)
            db.session.add(newRecipe)
            db.session.commit()
            return '', 201
        
        recipe: Optional[Recipe] = db.session.query(Recipe).get(data['id'])
        
        if recipe:
            recipe.name = data['name']
            recipe.notes = data['notes']
            recipe.ingredients = ingredients
            db.session.commit()
            return '', 200
        else:
            return f'No object found with recipe_id={data["id"]}', 404
            

    def get(self, recipe_id: Optional[int] = None):
        # sleep(20)  # simulate slow internet 
        if recipe_id:
            recipe = db.session.query(Recipe).get(recipe_id)
            handle_nonexistance(recipe)
            return jsonify(recipe.toJson())
        else:
            return jsonify([recipe.toJson() for recipe in Recipe.query.filter(Recipe.deleted == 0).all()])

    @optional_param_check(True, 'recipe_id')
    def delete(self, recipe_id: Optional[int] = None):
        recipe: Optional[Recipe] = db.session.query(Recipe).get(recipe_id)
        if recipe:
            recipe.deleted = True
            db.session.commit()
            return '', 204
        else:
            return f'No object found with recipe_id={recipe_id}', 404
