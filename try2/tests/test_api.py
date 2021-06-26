from models.note import Note

from flask import json, url_for
from flask.testing import FlaskClient
from flask_testing import TestCase
from flask_restful import url_for as url_for_rest

from flask_app import create_app
from database import db


class NoteCase(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    TESTING = True

    client: FlaskClient

    def create_app(self):
        # pass in test configuration
        app = create_app(testing=True, db_uri=self.SQLALCHEMY_DATABASE_URI)

        with app.app_context():
            self.API_NOTES = url_for_rest('resources.notelist', _external=False)
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
        response = self.client.get(self.API_NOTES)

        self.assertEqual(list, type(response.json))
        self.assertEqual([{'id': 1, 'content': 'Test Note 1'}], response.json)
        self.assert200(response)

    def test_add_notes(self):
        data = {'note': 'foobar'}
        response = self.client.post(self.API_NOTE, data=data)

        self.assertStatus(response, 201)
        self.assertFalse(response.json)

        response = self.client.get(self.API_NOTES)

        self.assertEqual(list, type(response.json))
        self.assertEqual([
            {'id': 1, 'content': 'Test Note 1'}, 
            {'id': 2, 'content': 'foobar'}
            ], response.json)
        self.assert200(response)

    def test_add_notes_wrong(self):
        data = {}
        response = self.client.post(self.API_NOTE, data=data)

        self.assert400(response)
        self.assertEqual({'message': {'error': 'field "note" missing or empty in data'}}, response.json)

    def test_add_notes_wrong2(self):
        data = {'note': ''}
        response = self.client.post(self.API_NOTE, data=data)

        self.assert400(response)
        self.assertEqual({'message': {'error': 'field "note" missing or empty in data'}}, response.json)
    
    def test_add_notes_wrong3(self):
        data = {'note': 'abc'}
        response = self.client.post(self.GET_API_NOTE(3), data=data)

        self.assert400(response)
        self.assertEqual({'message': {'error': 'The url paramter "note_id" should not exist in url'}}, response.json)

    def test_get_note(self):
        response = self.client.get(self.GET_API_NOTE(1))

        self.assert200(response)
        self.assertEqual({'id': 1, 'content': 'Test Note 1'}, response.json)

    def test_get_note_wrong(self):
        response = self.client.get(self.API_NOTE)

        self.assert400(response)
        self.assertEqual({'message': {'error': 'The url paramter "note_id" should exist in url'}}, response.json)

    def test_get_note_wrong2(self):
        response = self.client.get(self.GET_API_NOTE(2))

        self.assert404(response)
        self.assertEqual({'message': {'error': 'entry not found in database'}}, response.json)
