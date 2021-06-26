from models.note import Note

from flask import json, url_for
from flask.testing import FlaskClient
from flask_testing import TestCase

from flask_app import create_app
from database import db


class BaseCase(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    TESTING = True

    client: FlaskClient

    def create_app(self):
        # pass in test configuration
        app = create_app(testing=True, db_uri=self.SQLALCHEMY_DATABASE_URI)

        with app.app_context():
            self.API_NOTES = url_for('api.notes', _external=False)
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
        response = self.client.get(self.API_NOTES)

        self.assertEqual(list, type(response.json))
        self.assertEqual([{'id': 1, 'content': 'Test Note 1'}], response.json)
        self.assertEqual(200, response.status_code)

    def test_add_notes(self):
        data = {'note': 'foobar'}
        response = self.client.post(self.API_NOTES, data=data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(None, response.json)

        response = self.client.get(self.API_NOTES)

        self.assertEqual(list, type(response.json))
        self.assertEqual([
            {'id': 1, 'content': 'Test Note 1'}, 
            {'id': 2, 'content': 'foobar'}
            ], response.json)
        self.assertEqual(200, response.status_code)

    def test_add_notes_wrong(self):
        data = {}
        response = self.client.post(self.API_NOTES, data=data)

        self.assertEqual(400, response.status_code)
        self.assertEqual({'error': 'note key missing, empty or wrong type in data'}, response.json)

    def test_add_notes_wrong2(self):
        data = {'note': ''}
        response = self.client.post(self.API_NOTES, data=data)

        self.assertEqual(400, response.status_code)
        self.assertEqual({'error': 'note key missing, empty or wrong type in data'}, response.json)
