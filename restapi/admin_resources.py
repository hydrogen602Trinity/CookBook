from typing import Optional
from flask.json import jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash

from models import db, User
from .auth_util import require_admin
from .util import optional_param_check, require_truthy_values, handle_nonexistance, add_resource
from .resources import api


@add_resource(api, '/user', '/user/<int:user_id>')
class UserResource(Resource):

    user_parser = reqparse.RequestParser()
    user_parser.add_argument('name', type=str, help='User Name')
    user_parser.add_argument('email', type=str, help='User Email')
    user_parser.add_argument('password', type=str, help='User Password')

    user_parser_w_id = user_parser.copy()
    user_parser_w_id.add_argument('id', type=int, default=None, help="User ID")

    @require_admin
    @optional_param_check(False, 'user_id')
    def post(self, _=None):
        data = require_truthy_values(self.user_parser.parse_args())

        overlaps = db.session.query(User).filter(User.email == data['email']).count()
        if overlaps > 0:
            return f'Email already exists: email={data["email"]}', 400

        newUser = User(data['name'], data['email'], data['password'])
        db.session.add(newUser)
        db.session.commit()
        return '', 201

    @require_admin
    @optional_param_check(False, 'user_id')
    def put(self, _=None):
        #data = require_truthy_values(self.user_parser_w_id.parse_args(), exceptions=('id'))
        data = self.user_parser_w_id.parse_args()

        if data['id'] is None:
            # creating new user!
            require_truthy_values(data, exceptions='id')
            overlaps = db.session.query(User).filter(User.email == data['email']).count()
            if overlaps > 0:
                return f'Email already exists: email={data["email"]}', 400
            
            newUser = User(data['name'], data['email'], data['password'])
            db.session.add(newUser)
            db.session.commit()
            return f'{newUser.id}', 201

        user: Optional[User] = db.session.query(User).get(data['id'])

        if user:
            if data['email']:
                overlap = data['email'] != user.email and db.session.query(User).filter(User.email == data['email']).count() > 0
                if overlap > 0:
                    return f'Email already exists: email={data["email"]}', 400
                user.email = data['email']

            if data['name']:
                user.name = data['name']

            if data['password']:
                user.password = generate_password_hash(data['password'], method='sha256')

            db.session.commit()
            return f'{user.id}', 200
        else:
            return f'No object found with user_id={data["id"]}', 404

    @require_admin
    def get(self, user_id: Optional[int] = None):
        #sleep(20)  # simulate slow internet 
        if user_id:
            user = db.session.query(User).get(user_id)
            handle_nonexistance(user)
            return jsonify(user.toJson())
        else:
            # current_app.logger.debug('Getting all users')
            return jsonify([user.toJson() for user in User.query.all()])

    @require_admin
    @optional_param_check(True, 'user_id')
    def delete(self, user_id: Optional[int] = None):
        user: Optional[User] = db.session.query(User).get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return '', 204
        else:
            return f'No object found with user_id={user_id}', 404
