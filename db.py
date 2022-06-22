import configparser
import os

from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from flask_playground.models import Base


def _get_engine():
    return create_engine(
        _get_db_string()
    )


def _get_db_string():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'settings.env'))

    db_user = config['db']['user']
    db_pass = config['db']['pass']
    db_host = config['db']['host']
    db_port = config['db']['port']
    db_name = config['db'].get('name', 'postgres')

    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


def get_db_session():
    """
    Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db_session" not in g:
        engine = _get_engine()
        g.db_session = scoped_session(
             sessionmaker(
                 autocommit=False,
                 autoflush=False,
                 bind=engine
             )
         )
        Base.query = g.db_session.query_property()
        Base.metadata.create_all(bind=engine)
    return g.db_session
