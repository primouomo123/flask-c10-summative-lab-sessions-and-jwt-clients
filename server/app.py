#!/usr/bin/env python3

from flask import request, session, jsonify, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request

from config import app, db, api, jwt
from models import User, Expenses, UserSchema, ExpensesSchema

@app.before_request
def check_if_logged_in():
    open_access_list = [
        'signup',
        'login'
    ]

    if (request.endpoint) not in open_access_list and (not verify_jwt_in_request()):
        return make_response(jsonify({'error': '401 Unauthorized'}), 401)

class Signup(Resource):
    def post(self):

        request_json = request.get_json()

        username = request_json.get('username')
        password = request_json.get('password')

        user = User(
            username=username
        )
        user.password_hash = password
        
        try:
            db.session.add(user)
            db.session.commit()
            access_token = create_access_token(identity=str(user.id))
            return make_response(jsonify(token=access_token, user=UserSchema().dump(user)), 200)
        except IntegrityError:
            return make_response(jsonify({'errors': ['422 Unprocessable Entity']}), 422)

class WhoAmI(Resource):
    def get(self):
        user_id = get_jwt_identity()
            
        user = User.query.filter(User.id == user_id).first()
        
        return make_response(jsonify(UserSchema().dump(user)), 200)


class Login(Resource):
    def post(self):

        username = request.json['username']
        password = request.json['password']

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            token = create_access_token(identity=str(user.id))
            return make_response(jsonify(token=token, user=UserSchema().dump(user)), 200)

        return make_response(jsonify({'errors': ['401 Unauthorized']}), 401)

class ExpensesList(Resource):
    def get(self):
        user_id = get_jwt_identity()
        expenses = Expenses.query.filter(Expenses.user_id == user_id).all()
        return make_response(jsonify(ExpensesSchema(many=True).dump(expenses)), 200)
    
    def post(self):
        user_id = get_jwt_identity()
        request_json = request.get_json()
        request_json['user_id'] = user_id

        try:
            expense = ExpensesSchema().load(request_json)
            db.session.add(expense)
            db.session.commit()
            return make_response(jsonify(ExpensesSchema().dump(expense)), 201)
        except Exception as e:
            return make_response(jsonify({'errors': ['422 Unprocessable Entity']}), 422)

class ExpenseDetail(Resource):
    def get(self, id):
        user_id = get_jwt_identity()
        expense = Expenses.query.filter(Expenses.id == id, Expenses.user_id == user_id).first()
        if expense:
            return make_response(jsonify(ExpensesSchema().dump(expense)), 200)
        return make_response(jsonify({'errors': ['404 Not Found']}), 404)

    def patch(self, id):
        user_id = get_jwt_identity()
        expense = Expenses.query.filter(Expenses.id == id, Expenses.user_id == user_id).first()
        if not expense:
            return make_response(jsonify({'errors': ['404 Not Found']}), 404)

        request_json = request.get_json()
        for key, value in request_json.items():
            setattr(expense, key, value)

        try:
            db.session.commit()
            return make_response(jsonify(ExpensesSchema().dump(expense)), 200)
        except Exception as e:
            return make_response(jsonify({'errors': ['422 Unprocessable Entity']}), 422)
    
    def delete(self, id):
        user_id = get_jwt_identity()
        expense = Expenses.query.filter(Expenses.id == id, Expenses.user_id == user_id).first()
        if not expense:
            return make_response(jsonify({'errors': ['404 Not Found']}), 404)

        db.session.delete(expense)
        db.session.commit()
        return make_response(jsonify({}), 204)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(WhoAmI, '/me', endpoint='me')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(ExpensesList, '/expenses', endpoint='expenses')
api.add_resource(ExpenseDetail, '/expenses/<int:id>', endpoint='expense_detail')


if __name__ == '__main__':
    app.run(port=5555, debug=True)