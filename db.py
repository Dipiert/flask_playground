from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_playground.models import Base
import configparser
import os

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'settings.env'))

DB_USER = CONFIG['db']['user']
DB_PASS = CONFIG['db']['pass']
DB_HOST = CONFIG['db']['host']
DB_PORT = CONFIG['db']['port']

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
)

db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)
Base.query = db_session.query_property()
Base.metadata.create_all(bind=engine)

