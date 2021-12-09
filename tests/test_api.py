from datetime import date
from typing import Type
from models import Meal, Recipe, Ingredient, User, Tag
from shoppinglist import create_shoppinglist, combineIngredients, sortIngredients
from math import ceil
from util import curry
from flask_app import create_app as flask_create_app
from typing import List
from database import db

from flask.testing import FlaskClient
from flask_testing import TestCase
from flask_restful import url_for as url_for_rest
import os

@curry(3)
def setup_helper(resource_path: str, id_name: str, cls: Type[TestCase]):
    cls.SQLALCHEMY_DATABASE_URI = 'postgres'
    cls.TESTING = True

    def method_setter(func):
        setattr(cls, func.__name__, func)
        return func

    @method_setter
    def create_app(self):
        # pass in test configuration
        app = flask_create_app(testing=True, db_name=self.SQLALCHEMY_DATABASE_URI)

        with app.app_context():
            if not isinstance(id_name, list):
                self.GET_API_NODE = \
                    lambda arg: url_for_rest(resource_path, _external=False, **{id_name: arg})
                self.API_NODE = self.GET_API_NODE(None)

            self.LOGIN_NODE = url_for_rest('resources.loginresource', _external=False)
        return app

    @method_setter
    def login(self, user_email: str):
        assert isinstance(user_email, str), \
            f'Expected email as string, but got {type(user_email)}'
        response = self.client.post(self.LOGIN_NODE, 
            json={'email': user_email, 'password': 'unittest'})

        self.assert201(response)

    @method_setter
    def logout(self):
        response = self.client.delete(self.LOGIN_NODE)

        self.assert201(response)

    @method_setter
    def setUp(self):
        db.drop_all()
        db.create_all()

        user = User('Max Mustermann', 'max.mustermann@t-online.de', 'unittest')
        db.session.add(user)
        db.session.commit()

        self.user = user.email

        admin = User('Admin', 'admin@test.de', 'unittest', is_admin=True)
        db.session.add(admin)
        db.session.commit()

        self.admin = admin.email

        recipe = Recipe('Scrambled Eggs', 'Break and beat eggs', [], user)
        db.session.add(recipe)
        db.session.commit()

        meal = Meal('meal 1', date(2021, 11, 16), user.id, recipe.id)
        db.session.add(meal)
        db.session.commit()

        tag = Tag('Spicy')
        db.session.add(tag)
        db.session.commit()

        if os.getenv('TESTING') == '1':
            self.maxDiff = None

    @method_setter
    def tearDown(self):
        self.logout()
        db.session.remove()
        db.drop_all()

    @method_setter
    def assert201(self, response):
        self.assertStatus(response, 201)

    @method_setter
    def assert204(self, response):
        self.assertStatus(response, 204)
    return cls

@setup_helper('resources.reciperesource', 'recipe_id')
class RecipeCase(TestCase):
    client: FlaskClient

    def test_get(self):
        response = self.client.get(self.API_NODE)
        self.assert401(response)
        self.login(self.user)

        response = self.client.get(self.API_NODE)

        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': [], 
            'recipeTags':[], 'rating': None, 'prepTime': None}], response.json)

        response = self.client.get(self.API_NODE + '?minimum=True')

        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs'}], response.json)


        self.logout()
        self.login(self.admin)
        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([], response.json)

    def test_create(self):
        data = {
            'name': 'Cooked Eggs',
            'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'name': 'eggs',
                'num': 2,
                'denom': 1
            }]
        }

        response = self.client.post(self.API_NODE, json=data)
        self.assert401(response)
        self.login(self.user)

        #self.login(self.user)
        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.get(self.API_NODE)

        self.assert200(response)
        self.assertEqual([
            {'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside', 'ingredients': [{
                'name': 'eggs',
                'id': 1,
                'num': 2,
                'denom': 1,
                'unit': None
            }], 'recipeTags': [], 'rating': None, 'prepTime': None},
            {'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': [], 'recipeTags': [], 'rating': None, 'prepTime': None}
            ], response.json)
        
        response = self.client.get(self.GET_API_NODE(2))

        self.assert200(response)
        self.assertEqual({
            'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside', 'ingredients': [{
                'name': 'eggs',
                'id': 1,
                'num': 2,
                'denom': 1,
                'unit': None
            }], 'recipeTags': [], 'rating': None, 'prepTime': None}, response.json)

    def test_create2(self):
        data = {
            'name': 'Cooked Eggs',
            'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'name': 'flour',
                'num': 2,
                'denom': 2,
                'unit': 'g'
            }],
            'rating': 3,
            'prepTime': 60
        }

        response = self.client.post(self.API_NODE, json=data)
        self.assert401(response)
        self.login(self.user)

        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.get(self.API_NODE)

        self.assert200(response)
        self.assertEqual([
            {'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside', 'ingredients': [{
                'name': 'flour',
                'id': 1,
                'num': 1,
                'denom': 1,
                'unit': 'g'
            }], 'recipeTags': [], 'rating': 3, 'prepTime': 60},
            {'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': [], 'recipeTags': [], 'rating': None, 'prepTime': None}
            ], response.json)
        
        response = self.client.get(self.GET_API_NODE(2))

        self.assert200(response)
        self.assertEqual({
            'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside', 'ingredients': [{
                'name': 'flour',
                'id': 1,
                'num': 1,
                'denom': 1,
                'unit': 'g'
            }], 'recipeTags': [], 'rating': 3, 'prepTime': 60}, response.json)

    def test_create_invalid(self):
        invalid_data = [
            {
                'name': '',
                'notes': 'Cook for 4 and and a half for a liquid inside'
            },
            {
                'name': 'Cooked Eggs',
                'notes': ''
            },
            {
                'notes': 'Cook for 4 and and a half for a liquid inside'
            },
            {
                'name': 'Cooked Eggs'
            },
            {
                'name': 'Cooked Eggs',
                'notes': 'Cook for 4 and and a half for a liquid inside',
                'ingredients': [{
                    'name': 'eggs',
                    'num': 2,
                    'denom': 1
                }],
                'rating': 6
            },
            {
                'name': 'Cooked Eggs',
                'notes': 'Cook for 4 and and a half for a liquid inside',
                'ingredients': [{
                    'name': 'eggs',
                    'num': 2,
                    'denom': 1
                }],
                'rating': 0
            },
            {
                'name': 'Cooked Eggs',
                'notes': 'Cook for 4 and and a half for a liquid inside',
                'ingredients': [{
                    'name': 'eggs',
                    'num': 2,
                    'denom': 1
                }],
                'prepTime': -10
            }
        ]

        self.login(self.user)

        for data in invalid_data:
            response = self.client.post(self.API_NODE, json=data)

            self.assert400(response)

            response = self.client.get(self.API_NODE)

            self.assert200(response)
            self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': [], 
                'recipeTags': [], 'rating': None, 'prepTime': None}], response.json)

    def test_delete(self):
        self.login(self.user)

        response = self.client.get(self.API_NODE)

        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': [], 'recipeTags': [], 'rating': None, 'prepTime': None}], response.json)

        self.logout()
        self.assert401(self.client.delete(self.GET_API_NODE(1)))
        self.login(self.admin)
        self.assert404(self.client.delete(self.GET_API_NODE(1)))
        self.logout()
        self.login(self.user)

        response = self.client.delete(self.GET_API_NODE(1))

        self.assert204(response)

        response = self.client.get(self.API_NODE)

        self.assert200(response)
        self.assertEqual([], response.json)

    def test_delete_no_exist(self):
        self.login(self.user)

        response = self.client.delete(self.GET_API_NODE(42))
        self.assert404(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': [], 'recipeTags': [], 'rating': None, 'prepTime': None}], response.json)

    def test_put_no_exist(self):
        self.login(self.user)

        response = self.client.put(self.API_NODE, json={
            'id': 42,
            'name': 'Cooked Eggs',
            'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'name': 'flour',
                'num': 2,
                'denom': 2,
                'unit': 'g'
        }]})
        self.assert404(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': [], 
            'recipeTags': [], 'rating': None, 'prepTime': None}], response.json)

    def test_put_create(self):
        response = self.client.put(self.API_NODE, json={
            'name': 'Cooked Eggs',
            'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'name': 'flour',
                'num': 2,
                'denom': 3,
                'unit': 'g'
        }]})
        self.assert401(response)

        self.login(self.user)

        response = self.client.put(self.API_NODE, json={
            'name': 'Cooked Eggs',
            'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'name': 'flour',
                'num': 2,
                'denom': 3,
                'unit': 'g'
            }], 'recipeTags': [], 
            'rating': 1,
            'prepTime': 90
        })
        self.assert201(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([
            {'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'id': 1,
                'name': 'flour',
                'num': 2,
                'denom': 3,
                'unit': 'g'
            }], 'recipeTags': [], 'rating': 1, 'prepTime': 90},
            {'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': [], 'recipeTags': [], 'rating': None, 'prepTime': None},
        ], response.json)

    def test_put_1(self):
        self.login(self.user)

        response = self.client.put(self.API_NODE, json={
            'id': 1, 
            'name': 'Scrambled Eggs Edited', 
        })
        self.assert200(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs Edited', 'notes': 'Break and beat eggs', 'ingredients': [], 
            'recipeTags': [], 'rating': None, 'prepTime': None}], response.json)

    def test_put_2(self):
        self.login(self.user)

        data = {
            'name': 'Cooked Eggs',
            'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'name': 'flour',
                'num': 2,
                'denom': 2,
                'unit': 'g'
            }],
            'rating': 4
        }
        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.put(self.API_NODE, json={
            'id': 2,
            'name': 'Cooked Eggs Edited Name',
            'notes': 'Cook for 8 min',
            'ingredients': [{
                'name': 'salt',
                'num': 1,
                'denom': 1,
                'unit': 'g'
            }],
            'rating': 4
        })
        self.assert200(response)

        self.assertEqual(db.session.query(Ingredient).filter(Ingredient.recipe_id == 2).count(), 1)

        response = self.client.get(self.GET_API_NODE(2))
        self.assert200(response)
        self.assertEqual({
            'id': 2,
            'name': 'Cooked Eggs Edited Name',
            'notes': 'Cook for 8 min',
            'ingredients': [{
                'name': 'salt',
                'num': 1,
                'id': 2,
                'denom': 1,
                'unit': 'g'
            }], 'recipeTags': [], 
            'rating': 4, 
            'prepTime': None
        }, response.json)

        self.assertEqual(db.session.query(Ingredient).filter(Ingredient.recipe_id == 2).count(), 1)

@setup_helper('resources.recipetagmanager', ['recipe_id', 'tag_id'])
class RecipeTagCase(TestCase):
    client: FlaskClient

    def test_put(self):
        self.login(self.user)

        self.GET_API_NODE = \
            lambda arg1, arg2: url_for_rest('resources.recipetagmanager', _external=False, recipe_id=arg1, tag_id=arg2)
        
        self.RECIPE_API_NODE = \
            lambda arg: url_for_rest('resources.reciperesource', _external=False, recipe_id=arg)

        response = self.client.put(self.GET_API_NODE(1, 1))
        self.assert200(response)

        response = self.client.get(self.RECIPE_API_NODE(1))
        self.assert200(response)
        self.assertEqual({'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'recipeTags': [{'id': 1, 'tagType': 'Spicy'}],
            'ingredients': [], 'rating': None, 'prepTime': None}, response.json)
        
        self.TAG_API_NODE = \
            lambda arg: url_for_rest('resources.tagresource', _external=False, tag_id=arg)

        response = self.client.get(self.TAG_API_NODE(None) + '?showAssociates=True')
        self.assert200(response)
        self.assertEqual([{'id': 1, 'tagType': 'Spicy', 'assocUsers': [], 'assocRecipes': [
            {'id': 1, 'name': 'Scrambled Eggs'}]
        }], response.json)


@setup_helper('resources.userresource', 'user_id')
class UserCase(TestCase):
    client: FlaskClient

    def test_get(self):
        self.assert401(self.client.get(self.API_NODE))
        self.login(self.user)
        self.assert401(self.client.get(self.API_NODE))  # not admin
        self.logout()
        self.login(self.admin)

        response = self.client.get(self.API_NODE)

        self.assert200(response)

        self.assertEqual([
            {'id': 1, 'name': 'Max Mustermann', 'email': 'max.mustermann@t-online.de', 'userTags': []},
            {'email': 'admin@test.de', 'id': 2, 'name': 'Admin', 'userTags': []}
        ], response.json)

    def test_create(self):
        data = {
            'name': 'Moritz Mustermann',
            'email': 'nein@weissnicht.de',
            'password': 'aaaaaaaaaaaa'
        }

        self.assert401(self.client.post(self.API_NODE, json=data))
        self.login(self.user)
        self.assert401(self.client.post(self.API_NODE, json=data))  # not admin
        self.logout()
        self.login(self.admin)

        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([
            {'id': 1, 'name': 'Max Mustermann', 'email': 'max.mustermann@t-online.de', 'userTags': []},
            {'email': 'admin@test.de', 'id': 2, 'name': 'Admin', 'userTags': []},
            {'id': 3, 'name': 'Moritz Mustermann', 'email': 'nein@weissnicht.de', 'userTags': []}
        ], response.json)

        response = self.client.get(self.GET_API_NODE(3))
        self.assert200(response)
        self.assertEqual(
            {'id': 3, 'name': 'Moritz Mustermann', 'email': 'nein@weissnicht.de', 'userTags': []}
        , response.json)

    def test_delete(self):
        data = {
            'name': 'Moritz Mustermann',
            'email': 'nein@weissnicht.de',
            'password': 'aaaaaaaaaaaa'
        }

        self.login(self.admin)
        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.get(self.GET_API_NODE(3))
        self.assert200(response)
        self.assertEqual(
            {'id': 3, 'name': 'Moritz Mustermann', 'email': 'nein@weissnicht.de', 'userTags': []}
        , response.json)

        self.logout()
        self.assert401(self.client.delete(self.GET_API_NODE(3)))
        self.login(self.user)
        self.assert401(self.client.delete(self.GET_API_NODE(3)))  # not admin
        self.logout()
        self.login(self.admin)

        response = self.client.delete(self.GET_API_NODE(3))
        self.assert204(response)

        response = self.client.get(self.GET_API_NODE(3))
        self.assert404(response)

@setup_helper('resources.usertagmanager', ['user_id', 'tag_id'])
class UserTagCase(TestCase):
    client: FlaskClient

    def test_put(self):
        self.login(self.admin)

        self.GET_API_NODE = \
                lambda arg1, arg2: url_for_rest('resources.usertagmanager', _external=False, user_id=arg1, tag_id=arg2)
        
        self.USER_API_NODE = \
                lambda arg: url_for_rest('resources.userresource', _external=False, user_id=arg)

        response = self.client.put(self.GET_API_NODE(1, 1))
        self.assert200(response)

        response = self.client.get(self.USER_API_NODE(1))
        self.assert200(response)
        self.assertEqual(
            {'id': 1, 'name': 'Max Mustermann', 'email': 'max.mustermann@t-online.de', 'userTags': [{'id': 1, 'tagType': 'Spicy'}]}, response.json)

@setup_helper('resources.mealresource', 'meal_id')
class MealCase(TestCase):
    client: FlaskClient

    def test_get(self):
        response = self.client.get(self.API_NODE)
        self.assert401(response)

        self.login(self.admin)
        response = self.client.get(self.API_NODE)
        self.assert200(response)

        self.assertEqual([], response.json)
        self.logout()

        self.login(self.user)
        response = self.client.get(self.API_NODE)
        self.assert200(response)

        self.assertEqual([{
            'id': 1, 
            'label': 'meal 1', 
            'day': '2021-11-16', 
            'user_id': 1, 
            'recipe_id': 1
        }], response.json)
    
    def test_put(self):
        data = {
            'id': 1, 
            'label': 'meal 5', 
            'day': '2021-11-16', 
            'user_id': 1, 
            'recipe_id': 1
        }

        response = self.client.put(self.API_NODE, json=data)
        self.assert401(response)

        self.login(self.user)


        response = self.client.put(self.API_NODE, json=data)
        self.assert200(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)

        self.assertEqual([{
            'id': 1, 
            'label': 'meal 5', 
            'day': '2021-11-16', 
            'user_id': 1, 
            'recipe_id': 1
        }], response.json)

        data = [{
            'id': 1, 
            'label': 'meal 10', 
            'day': '2021-11-16', 
            'user_id': 1, 
            'recipe_id': 1
        },
        {
            'label': 'meal 7', 
            'day': '2021-11-17', 
            'user_id': 1, 
            'recipe_id': 1
        }]

        response = self.client.put(self.API_NODE, json=data)
        self.assert200(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)

        self.assertEqual([{
            'id': 1, 
            'label': 'meal 10', 
            'day': '2021-11-16', 
            'user_id': 1, 
            'recipe_id': 1
        },
        {
            'id': 2, 
            'label': 'meal 7', 
            'day': '2021-11-17', 
            'user_id': 1, 
            'recipe_id': 1
        }], response.json)

    def test_create(self):
        data = {
            'label': 'meal 1', 
            'day': '2020-01-01', 
            'recipe_id': 1
        }

        response = self.client.post(self.API_NODE, json=data)
        self.assert401(response)

        self.login(self.admin)
        d = data.copy()
        d['label'] = 'admin'
        response = self.client.post(self.API_NODE, json=d)
        self.assert201(response)

        self.logout()

        self.login(self.user)

        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        newID = int(response.get_data().decode().strip().replace('"',''))

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([
            {
                'id': newID,
                'label': 'meal 1', 
                'day': '2020-01-01', 
                'user_id': 1, 
                'recipe_id': 1
            },
            {
                'id': 1, 
                'label': 'meal 1', 
                'day': '2021-11-16', 
                'user_id': 1, 
                'recipe_id': 1
            }
        ], response.json)

        response = self.client.get(self.GET_API_NODE(newID))
        self.assert200(response)
        self.assertEqual(
            {
                'id': newID,
                'label': 'meal 1', 
                'day': '2020-01-01', 
                'user_id': 1, 
                'recipe_id': 1
            }
        , response.json)

    def test_delete(self):
        data = {
            'label': 'meal 10', 
            'day': '2020-09-30', 
            'recipe_id': 1
        }

        response = self.client.delete(self.GET_API_NODE(2))
        self.assert401(response)

        self.login(self.admin)
        response = self.client.delete(self.GET_API_NODE(2))
        self.assert404(response)
        self.logout()

        self.login(self.user)

        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.get(self.GET_API_NODE(2))
        self.assert200(response)
        self.assertEqual({
                'id': 2,
                'label': 'meal 10', 
                'day': '2020-09-30', 
                'user_id': 1, 
                'recipe_id': 1
            }, response.json)

        response = self.client.delete(self.GET_API_NODE(2))
        self.assert204(response)

        response = self.client.get(self.GET_API_NODE(2))
        self.assert404(response)

@setup_helper('resources.mealresource', 'meal_id')
class ShoppingTest(TestCase):
    client: FlaskClient
    
    def test_createList(self):

        meal2 = Meal('meal 2', date(2021, 11, 16), 1, 1)
        meal3 = Meal('meal 3', date(2021, 11, 16), 1, 2)
        
        #ingredients = create_shoppinglist([meal2, meal3])

        #self.assertEqual(ingredients, [])