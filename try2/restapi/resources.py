from typing import Optional
from flask.json import jsonify
from flask_restful import Resource, Api, reqparse
from flask import Blueprint, abort
from models import Note, db, note


api_blueprint = Blueprint(
                 __name__.split('.', maxsplit=1)[1], 
                 __name__,
                 template_folder='../templates'
                )


api = Api(api_blueprint)


def optional_param_check(should_exist: bool, **kwargs):
    for k, v in kwargs.items():
        if (should_exist and v is None) or (not should_exist and v is not None):
            abort(400, {
                'error': f'The url paramter "{k}" should { "" if should_exist else "not " }exist in url'})


class NoteList(Resource):

    def get(self):
        return jsonify([note.toJson() for note in Note.query.all()])


note_parser = reqparse.RequestParser()
note_parser.add_argument('note', type=str, help='The content of the note')

class NoteResource(Resource):

    def post(self, note_id: Optional[int] = None):
        optional_param_check(False, note_id=note_id)

        data = note_parser.parse_args()
        if not data['note']:
            abort(400, {'error': 'note missing or empty in data'})

        newNote = Note(data['note'])
        db.session.add(newNote)
        db.session.commit()
        return '', 201


api.add_resource(NoteList, '/notes')
api.add_resource(NoteResource, '/note', '/note/<int:note_id>')
