import configparser
import datetime
import os

import jwt
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash

from flask_playground.auth import token_required
from flask_playground.db import get_db_session
from flask_playground.models import Employee, User


def create_app():
    """" Creates a flask app and configure webserver based on settings.env file """
    app = Flask(__name__)
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'settings.env'))
    app.config['JWT_SECRET_KEY'] = config['webserver']['JWT_SECRET_KEY']
    app.config['JWT_ALGORITHM'] = config['webserver']['JWT_ALGORITHM']
    app.config['DEBUG'] = config['webserver']['debug']
    return app


app = create_app()


def get_user_by_username(username):
    """" Access db to get a user object from its username """
    return get_db_session().query(User.id).filter_by(user=username).first()


def write_user(new_user):
    """" Writes into db the user passed as parameter """
    db_session = get_db_session()
    db_session.add(new_user)
    db_session.commit()


@app.post('/user/new')
def create_user():
    """" Creates a user and store it in db if username doesn't exist and both username and password where provided """
    user = request.json.get('username')
    password = request.json.get('password')
    if not user or not password:
        return {
            "message": "Both user and password are required",
        }, 200
    if get_user_by_username(user):
        return {
           "message": f"User {user} already exists",
        }, 200

    registered_at = datetime.datetime.utcnow()
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(user=user, password=hashed_password, registered_at=registered_at)
    write_user(new_user)
    return jsonify({'message': 'registered successfully'})


@app.post('/employee/new')
def new_employee():
    """" Creates an employee object based on employee names, last names and their USD monthly salary """
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
    """" It requires JWT Auth. Provides a list of salaries greater than greater_than param which defaults to 0 """
    db_session = get_db_session()
    gt = request.json.get('greater_than', 0)
    employees_query = db_session.query(Employee)
    employees = employees_query.filter(Employee.usd_monthly_salary > gt).all()
    return jsonify({
        'employees': [e.serialize() for e in employees]
    })


@app.post('/login')
def login():
    """" This method will return a JWT token when usernames exists in db and their passwords match """
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

        logged_user = User.login(
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
    """" When application context is popped. This function will be called to remove db session """
    db_session = get_db_session()
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
