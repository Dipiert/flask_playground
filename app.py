from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash
from flask_playground.models import Employee, User
from flask_playground.auth import token_required
import datetime
import configparser
import jwt
import os
from flask_playground.db import get_db_session


def create_app():
    app = Flask(__name__)
    CONFIG = configparser.ConfigParser()
    CONFIG.read(os.path.join(os.path.dirname(__file__), 'settings.env'))
    app.config['JWT_SECRET_KEY'] = CONFIG['webserver']['JWT_SECRET_KEY']
    app.config['JWT_ALGORITHM'] = CONFIG['webserver']['JWT_ALGORITHM']
    app.config['DEBUG'] = CONFIG['webserver']['debug']
    return app


app = create_app()


def get_user_by_username(username):
    return get_db_session().query(User.id).filter_by(user=username).first()


def write_user(new_user):
    db_session = get_db_session()
    db_session.add(new_user)
    db_session.commit()


@app.post('/user/new')
def create_user():
    user = request.json.get('username')
    if get_user_by_username(user):
        return {
           "message": f"User {user} already exists",
        }, 200
    password = request.json.get('password')
    registered_at = datetime.datetime.utcnow()
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(user=user, password=hashed_password, registered_at=registered_at)
    write_user(new_user)
    return jsonify({'message': 'registered successfully'})


@app.post('/employee/new')
def new_employee():
    db_session = get_db_session()
    names = request.json.get("employee_names")
    last_names = request.json.get("employee_last_names")
    usd_monthly_salary = request.json.get("employee_usd_monthly_salary")
    employee = Employee(last_names=last_names, names=names, usd_monthly_salary=usd_monthly_salary)
    db_session.add(employee)
    db_session.commit()
    return jsonify({
        "message": "Employee successfully created"
    })


@app.get('/salaries')
@token_required
def get_salaries(current_user):
    db_session = get_db_session()
    gt = request.json.get('greater_than', 0)
    employees_query = db_session.query(Employee)
    employees = employees_query.filter(Employee.usd_monthly_salary > gt).all()
    return jsonify({
        'employees': [e.serialize() for e in employees]
    })


@app.post('/login')
def login():
    db_session = get_db_session()
    try:
        data = request.get_json()
        username = data.get('username')
        if not data:
            return {
               "message": "Please provide user details",
               "data": None,
               "error": "Bad request"
            }, 400

        user = db_session.query(User).filter(User.user == username).first()

        logged_user = User().login(
            user,
            data.get('password')
        )
        if logged_user:
            try:
                logged_user.token = jwt.encode(
                    {"username": user.user},
                    app.config["JWT_SECRET_KEY"],
                    algorithm=app.config["JWT_ALGORITHM"]
                )
                return {
                    "message": "Successfully fetched auth token",
                    "data": user.serialize()
                }
            except Exception as e:
                return {
                   "error": "Something went wrong",
                   "message": str(e)
                 }, 500
        return {
           "message": "Error fetching auth token!, invalid email or password",
           "data": None,
           "error": "Unauthorized"
        }, 404
    except Exception as e:
        return {
           "message": "Something went wrong!",
           "error": str(e),
           "data": None
        }, 500


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session = get_db_session()
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
