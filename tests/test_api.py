from datetime import date
from typing import Type
from models import Meal, Recipe, Ingredient, User
from util import curry
from flask_app import create_app as flask_create_app
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
            self.GET_API_NODE = \
                lambda arg: url_for_rest(resource_path, _external=False, **{id_name: arg})
            self.API_NODE = self.GET_API_NODE(None)
        return app

    @method_setter
    def setUp(self):
        db.drop_all()
        db.create_all()

        user = User('Max Mustermann', 'max.mustermann@t-online.de', 'max2021')
        db.session.add(user)
        db.session.commit()

        recipe = Recipe('Scrambled Eggs', 'Break and beat eggs', [], user)
        db.session.add(recipe)
        db.session.commit()

        meal = Meal('meal 1', date(2021, 11, 16), user.id, recipe.id)
        db.session.add(meal)
        db.session.commit()

        if os.getenv('TESTING') == '1':
            self.maxDiff = None

    @method_setter
    def tearDown(self):
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

        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': []}], response.json)


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

        self.assert201(response)

        response = self.client.get(self.API_NODE)

        self.assert200(response)
        self.assertEqual([
            {'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': []},
            {'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside', 'ingredients': [{
                'name': 'eggs',
                'id': 1,
                'num': 2,
                'denom': 1,
                'unit': None
            }]}], response.json)
        
        response = self.client.get(self.GET_API_NODE(2))

        self.assert200(response)
        self.assertEqual({
            'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside', 'ingredients': [{
                'name': 'eggs',
                'id': 1,
                'num': 2,
                'denom': 1,
                'unit': None
            }]}, response.json)

    def test_create2(self):
        data = {
            'name': 'Cooked Eggs',
            'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'name': 'flour',
                'num': 2,
                'denom': 2,
                'unit': 'g'
            }]
        }
        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.get(self.API_NODE)

        self.assert200(response)
        self.assertEqual([
            {'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': []},
            {'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside', 'ingredients': [{
                'name': 'flour',
                'id': 1,
                'num': 1,
                'denom': 1,
                'unit': 'g'
            }]}], response.json)
        
        response = self.client.get(self.GET_API_NODE(2))

        self.assert200(response)
        self.assertEqual({
            'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside', 'ingredients': [{
                'name': 'flour',
                'id': 1,
                'num': 1,
                'denom': 1,
                'unit': 'g'
            }]}, response.json)

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
            }
        ]

        for data in invalid_data:
            response = self.client.post(self.API_NODE, json=data)

            self.assert400(response)

            response = self.client.get(self.API_NODE)

            self.assert200(response)
            self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': []}], response.json)

    def test_delete(self):
        response = self.client.get(self.API_NODE)

        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': []}], response.json)

        response = self.client.delete(self.GET_API_NODE(1))

        self.assert204(response)

        response = self.client.get(self.API_NODE)

        self.assert200(response)
        self.assertEqual([], response.json)

    def test_delete_no_exist(self):
        response = self.client.delete(self.GET_API_NODE(42))
        self.assert404(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': []}], response.json)

    def test_put_no_exist(self):
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
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': []}], response.json)

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
        self.assert201(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([
            {'id': 1, 'name': 'Scrambled Eggs', 'notes': 'Break and beat eggs', 'ingredients': []},
            {'id': 2, 'name': 'Cooked Eggs', 'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'id': 1,
                'name': 'flour',
                'num': 2,
                'denom': 3,
                'unit': 'g'
        }]}
        ], response.json)


    def test_put_1(self):
        response = self.client.put(self.API_NODE, json={
            'id': 1, 
            'name': 'Scrambled Eggs Edited', 
            'notes': 'Break and beat eggs', 
            'ingredients': [{
                'name': 'flour',
                'id': 1,
                'num': 1,
                'denom': 1,
                'unit': 'g'
            }]})
        self.assert200(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([{'id': 1, 'name': 'Scrambled Eggs Edited', 'notes': 'Break and beat eggs', 'ingredients': [{
                'name': 'flour',
                'id': 1,
                'num': 1,
                'denom': 1,
                'unit': 'g'
            }]}], response.json)

        self.assertEqual(db.session.query(Ingredient).filter(Ingredient.recipe_id == 1).count(), 1)

    def test_put_2(self):
        data = {
            'name': 'Cooked Eggs',
            'notes': 'Cook for 4 and and a half for a liquid inside',
            'ingredients': [{
                'name': 'flour',
                'num': 2,
                'denom': 2,
                'unit': 'g'
            }]
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
            }]
        })
        self.assert200(response)

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
            }]
        }, response.json)

        self.assertEqual(db.session.query(Ingredient).filter(Ingredient.recipe_id == 2).count(), 1)


@setup_helper('resources.userresource', 'user_id')
class UserCase(TestCase):
    client: FlaskClient

    def test_get(self):
        response = self.client.get(self.API_NODE)

        self.assert200(response)

        self.assertEqual([
            {'id': 1, 'name': 'Max Mustermann', 'email': 'max.mustermann@t-online.de'}
        ], response.json)

    def test_create(self):
        data = {
            'name': 'Moritz Mustermann',
            'email': 'nein@weissnicht.de',
            'password': 'aaaaaaaaaaaa'
        }
        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([
            {'id': 1, 'name': 'Max Mustermann', 'email': 'max.mustermann@t-online.de'},
            {'id': 2, 'name': 'Moritz Mustermann', 'email': 'nein@weissnicht.de'}
        ], response.json)

        response = self.client.get(self.GET_API_NODE(2))
        self.assert200(response)
        self.assertEqual(
            {'id': 2, 'name': 'Moritz Mustermann', 'email': 'nein@weissnicht.de'}
        , response.json)

    def test_delete(self):
        data = {
            'name': 'Moritz Mustermann',
            'email': 'nein@weissnicht.de',
            'password': 'aaaaaaaaaaaa'
        }
        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.get(self.GET_API_NODE(2))
        self.assert200(response)
        self.assertEqual(
            {'id': 2, 'name': 'Moritz Mustermann', 'email': 'nein@weissnicht.de'}
        , response.json)

        response = self.client.delete(self.GET_API_NODE(2))
        self.assert204(response)

        response = self.client.get(self.GET_API_NODE(2))
        self.assert404(response)


@setup_helper('resources.mealresource', 'meal_id')
class MealCase(TestCase):
    client: FlaskClient

    def test_get(self):
        response = self.client.get(self.API_NODE)

        self.assert200(response)

        self.assertEqual([{
            'id': 1, 
            'label': 'meal 1', 
            'day': '2021-11-16', 
            'user_id': 1, 
            'recipe_id': 1
        }], response.json)

    def test_create(self):
        data = {
            'label': 'meal 1', 
            'day': '2020-01-01', 
            'user_id': 1, 
            'recipe_id': 1
        }
        response = self.client.post(self.API_NODE, json=data)

        self.assert201(response)

        response = self.client.get(self.API_NODE)
        self.assert200(response)
        self.assertEqual([
            {
                'id': 1, 
                'label': 'meal 1', 
                'day': '2021-11-16', 
                'user_id': 1, 
                'recipe_id': 1
            },
            {
                'id': 2,
                'label': 'meal 1', 
                'day': '2020-01-01', 
                'user_id': 1, 
                'recipe_id': 1
            }
        ], response.json)

        response = self.client.get(self.GET_API_NODE(2))
        self.assert200(response)
        self.assertEqual(
            {
                'id': 2,
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
            'user_id': 1, 
            'recipe_id': 1
        }
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


