from typing import Any, List, Optional, Union
from flask.json import jsonify
from flask_restful import Resource, Api, reqparse
from flask import Blueprint, abort
from functools import wraps

from models import Note, db


api_blueprint = Blueprint(
                 __name__.split('.', maxsplit=1)[1], 
                 __name__,
                 template_folder='../templates'
                )


api = Api(api_blueprint)


def optional_param_check(should_exist: bool, arg_list: Union[str, List[str]]):
    if isinstance(arg_list, str):
        arg_list = (arg_list,)
    def decorator(func):
        @wraps(func)
        def wrapper(self, **kwargs):
            for arg in arg_list:
                v = kwargs.get(arg)
                if (should_exist and v is None) or (not should_exist and v is not None):
                    abort(400, {
                        'error': f'The url paramter "{arg}" should { "" if should_exist else "not " }exist in url'})
            return func(self, **kwargs)
        return wrapper
    return decorator


def handle_nonexistance(value: Any):
    if value is None:
        abort(404, {'error': 'entry not found in database'})


class NoteList(Resource):

    def get(self):
        return jsonify([note.toJson() for note in Note.query.all()])


note_parser = reqparse.RequestParser()
note_parser.add_argument('note', type=str, help='The content of the note')


class NoteResource(Resource):

    @optional_param_check(False, 'note_id')
    def post(self, note_id: Optional[int] = None):
        data = note_parser.parse_args()
        if not data['note']:
            abort(400, {'error': 'note missing or empty in data'})

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
