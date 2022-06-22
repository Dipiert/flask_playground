from functools import wraps

import jwt
from flask import request, current_app

from flask_playground.db import get_db_session
from flask_playground.models import User


def token_required(f):
    """ Meant to be used as decorator. Checks that current user can access to a resource (JWT token in header). """
    @wraps(f)
    def decorated(*args, **kwargs):
        db_session = get_db_session()
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
            data = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=[current_app.config['JWT_ALGORITHM']])
            current_user = db_session.query(User).filter_by(user=data["username"]).first()
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
