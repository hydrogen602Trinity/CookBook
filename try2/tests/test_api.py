import unittest

from flask import json
from flask_testing import TestCase

from flask_app import create_app
from database import db


class BaseCase(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    TESTING = True

    def create_app(self):
        # pass in test configuration
        return create_app(testing=True, db_uri=self.SQLALCHEMY_DATABASE_URI)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_successful_login(self):
        response = self.client.get('/api/v1/note')

        self.assertEqual(list, type(response.json))
        self.assertEqual(200, response.status_code)