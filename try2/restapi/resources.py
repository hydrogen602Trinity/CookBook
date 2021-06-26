from flask.json import jsonify
from flask_restful import Resource, Api, reqparse
from flask import Blueprint, abort
from models import Note, db


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

    def post(self):
        data = note_parser.parse_args()
        if not data['note']:
            return {'error': 'note missing or empty in data'}, 400

        newNote = Note(data['note'])
        db.session.add(newNote)
        db.session.commit()
        return '', 201


api.add_resource(NoteList, '/notes')
api.add_resource(NoteResource, '/note')
