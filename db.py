from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_playground.models import Base
import configparser
import os


def _get_engine():
    return create_engine(
        _get_db_string()
    )


def _get_db_string():
    CONFIG = configparser.ConfigParser()
    CONFIG.read(os.path.join(os.path.dirname(__file__), 'settings.env'))

    DB_USER = CONFIG['db']['user']
    DB_PASS = CONFIG['db']['pass']
    DB_HOST = CONFIG['db']['host']
    DB_PORT = CONFIG['db']['port']
    DB_NAME = CONFIG['db'].get('name', 'postgres')

    return f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_db_session():
    """
    Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    from flask import g
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
