# from flask.json import jsonify
from flask_restful import Resource, reqparse
# from flask import Blueprint
# from flask import current_app
# from datetime import date
# from time import sleep
from werkzeug.security import check_password_hash
from flask_login import login_user, current_user, logout_user


from models import db, User
from .util import optional_param_check, require_keys_with_set_types, require_truthy_values, handle_nonexistance, add_resource
from .resources import api


@add_resource(api, '/login')
class LoginResource(Resource):

    user_parser = reqparse.RequestParser()
    user_parser.add_argument('email', type=str, help='User Email')
    user_parser.add_argument('password', type=str, help='User Password')

    def get(self):
        return current_user.name if current_user.is_authenticated else 'None'

    def post(self):
        print('login?')
        data = require_truthy_values(self.user_parser.parse_args())

        user = db.session.query(User).filter(User.email == data['email']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return '', 404
        
        login_user(user)
        print('login!', current_user.name)
        return '', 201
    
    def delete(self):
        # logout cause why not
        if current_user.is_authenticated:
            logout_user()

        return '', 201

