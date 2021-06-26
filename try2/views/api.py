from flask import jsonify, request
from flask import Blueprint, render_template, abort
from models import Note, db

api = Blueprint(
                 __name__.split('.', maxsplit=1)[1], 
                 __name__,
                 template_folder='../templates'
                )


@api.route('/')
def base():
    return 'api?'


@api.route('/note', methods=['POST', 'GET'])
def notes():
    if request.method == 'GET':
        return jsonify([note.toJson() for note in Note.query.all()])
    else:
        data = request.get_json(force=True, silent=True)
        if not data:
            data = request.form.to_dict()

        if 'note' not in data or not isinstance(data['note'], str) or not data['note']:
            return {'error': 'note key missing, empty or wrong type in data'}, 400
        
        newNote = Note(data['note'])
        db.session.add(newNote)
        db.session.commit()
        return '', 201


@api.route('/note/<int:param>', methods=['DELETE'])
def remove_note(param: int):
    Note.query.get(param)