from models import Note, Recipe, Ingredient

from flask.testing import FlaskClient
from flask_testing import TestCase
from flask_restful import url_for as url_for_rest

from flask_app import create_app
from database import db
import os


class NoteCase(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    TESTING = True

    client: FlaskClient

    def create_app(self):
        # pass in test configuration
        app = create_app(testing=True, db_uri=self.SQLALCHEMY_DATABASE_URI)

        with app.app_context():
            self.GET_API_NOTE = \
                lambda note_id: url_for_rest('resources.noteresource', _external=False, note_id=note_id)
            self.API_NOTE = self.GET_API_NOTE(None)
        return app

    def setUp(self):
        db.create_all()

        note = Note('Test Note 1')
        db.session.add(note)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_all_notes(self):
        response = self.client.get(self.API_NOTE)

        self.assertEqual(list, type(response.json))
        self.assertEqual([{'id': 1, 'content': 'Test Note 1'}], response.json)
        self.assert200(response)

    def test_add_notes(self):
        data = {'note': 'foobar'}
        response = self.client.post(self.API_NOTE, json=data)

        self.assertStatus(response, 201)
        self.assertFalse(response.json)

        response = self.client.get(self.API_NOTE)

        self.assertEqual(list, type(response.json))
        self.assertEqual([
            {'id': 1, 'content': 'Test Note 1'}, 
            {'id': 2, 'content': 'foobar'}
            ], response.json)
        self.assert200(response)

    def test_add_notes_wrong(self):
        data = {}
        response = self.client.post(self.API_NOTE, json=data)

        self.assert400(response)
        self.assertEqual({'message': {'error': 'field "note" missing or empty in data'}}, response.json)

    def test_add_notes_wrong2(self):
        data = {'note': ''}
        response = self.client.post(self.API_NOTE, json=data)

        self.assert400(response)
        self.assertEqual({'message': {'error': 'field "note" missing or empty in data'}}, response.json)
    
    def test_add_notes_wrong3(self):
        data = {'note': 'abc'}
        response = self.client.post(self.GET_API_NOTE(3), json=data)

        self.assert400(response)
        self.assertEqual({'message': {'error': 'The url paramter "note_id" should not exist in url'}}, response.json)

    def test_get_note(self):
        response = self.client.get(self.GET_API_NOTE(1))

        self.assert200(response)
        self.assertEqual({'id': 1, 'content': 'Test Note 1'}, response.json)

    def test_get_note_wrong2(self):
        response = self.client.get(self.GET_API_NOTE(2))

        self.assert404(response)
        self.assertEqual({'message': {'error': 'entry not found in database'}}, response.json)


class RecipeCase(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    TESTING = True

    client: FlaskClient

    def create_app(self):
        # pass in test configuration
        app = create_app(testing=True, db_uri=self.SQLALCHEMY_DATABASE_URI)

        with app.app_context():
            self.GET_API_NODE = \
                lambda recipe_id: url_for_rest('resources.reciperesource', _external=False, recipe_id=recipe_id)
            self.API_NODE = self.GET_API_NODE(None)
        return app

    def setUp(self):
        db.create_all()

        note = Recipe('Scrambled Eggs', 'Break and beat eggs', [])
        db.session.add(note)
        db.session.commit()

        if os.getenv('TESTING') == '1':
            self.maxDiff = None

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def assert201(self, response):
        self.assertStatus(response, 201)

    def assert204(self, response):
        self.assertStatus(response, 204)

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
