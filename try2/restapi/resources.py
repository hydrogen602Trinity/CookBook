from typing import Optional
from flask.json import jsonify
from flask_restful import Resource, Api, reqparse
from flask import Blueprint, abort
from functools import wraps

from models import Note, db
from .util import optional_param_check, require_truthy_values, handle_nonexistance


api_blueprint = Blueprint(
                 __name__.split('.', maxsplit=1)[1], 
                 __name__,
                 template_folder='../templates'
                )


api = Api(api_blueprint)


class NoteList(Resource):

    def get(self):
        return jsonify([note.toJson() for note in Note.query.all()])


note_parser = reqparse.RequestParser()
note_parser.add_argument('note', type=str, help='The content of the note')


class NoteResource(Resource):

    @optional_param_check(False, 'note_id')
    def post(self, note_id: Optional[int] = None):
        data = require_truthy_values(note_parser.parse_args())

        newNote = Note(data['note'])
        db.session.add(newNote)
        db.session.commit()
        return '', 201

    @optional_param_check(True, 'note_id')
    def get(self, note_id: Optional[int] = None):
        assert note_id
        note = db.session.query(Note).get(note_id)
        handle_nonexistance(note)
        return jsonify(note.toJson())


api.add_resource(NoteList, '/notes')
api.add_resource(NoteResource, '/note', '/note/<int:note_id>')
