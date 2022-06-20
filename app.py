from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash
from flask_playground.models import Employee, User
import jwt
import datetime
import configparser
from functools import wraps
import os
from flask_playground.db import db_session


def create_app():
    app = Flask(__name__)
    CONFIG = configparser.ConfigParser()
    CONFIG.read(os.path.join(os.path.dirname(__file__), 'settings.env'))
    app.config['JWT_SECRET_KEY'] = CONFIG['webserver']['JWT_SECRET_KEY']
    app.config['JWT_ALGORITHM'] = CONFIG['webserver']['JWT_ALGORITHM']
    app.config['DEBUG'] = CONFIG['webserver']['debug']
    return app


app = create_app()


# TODO: Move this to an auth related module
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
               "message": "Authentication Token is missing!",
               "data": None,
               "error": "Unauthorized"
            }, 401
        try:
            data = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(user=data["username"]).first()
            if current_user is None:
                return {
                   "message": "Invalid Authentication token!",
                   "data": None,
                   "error": "Unauthorized"
                }, 401
        except Exception as e:
            return {
               "message": "Something went wrong",
               "data": None,
               "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)
    return decorated


@app.post('/user/new')
def create_user():
    user = request.json.get('user')
    password = request.json.get('password')
    registered_at = datetime.datetime.utcnow()
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(user=user, password=hashed_password, registered_at=registered_at)
    db_session.add(new_user)
    db_session.commit()
    return jsonify({'message': 'registered successfully'})


@app.post('/employee/new')
def new_employee():
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
def get_salaries():
    gt = request.json.get('greater_than', 0)
    employees_query = db.session.query(Employee)
    employees = employees_query.filter(Employee.usd_monthly_salary > gt).all()
    return jsonify({
        'employees': [e.serialize() for e in employees]
    })


@app.post('/login')
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        if not data:
            return {
               "message": "Please provide user details",
               "data": None,
               "error": "Bad request"
            }, 400

        user = db.session.query(User).filter(User.user == username).first()

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
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
