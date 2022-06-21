import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_playground import models
from flask_playground.models import Base
import os
import pytest as pytest
from flask_playground.db import get_db_session
from flask import g, current_app
from flask_playground.app import app


@pytest.fixture(scope='session')
def connection():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'settings.env'))
    app.config['DB_USER'] = config['db']['user']
    app.config['DB_PASS'] = config['db']['pass']
    app.config['DB_HOST'] = config['db']['host']
    app.config['DB_PORT'] = config['db']['port']
    app.config['DB_NAME'] = config['db']['name']
    engine = create_engine(
        f"postgresql://{app.config['DB_USER']}:{app.config['DB_PASS']}"
        f"@{app.config['DB_HOST']}:{app.config['DB_PORT']}/"
        f"{app.config['DB_NAME']}"
    )
    db_session = scoped_session(
                 sessionmaker(
                     autocommit=False,
                     autoflush=False,
                     bind=engine
                 )
             )
    Base.query = db_session.query_property()
    return engine.connect()


@pytest.fixture(scope="session")
def setup_database(connection):
    models.Base.metadata.bind = connection
    models.Base.metadata.create_all()
    yield
    models.Base.metadata.drop_all()


@pytest.fixture
def db_session(setup_database, connection):
    transaction = connection.begin()
    yield scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection)
    )
    transaction.rollback()


def test_write_employees(db_session):
    employees = [
        models.Employee(
            last_names='Burns',
            names='Montgomery',
            usd_monthly_salary=890000.00
        ),
        models.Employee(
            last_names='Simpson',
            names='Homer',
            usd_monthly_salary=890.00
        )
    ]
    # Use of unit of work
    for employee in employees:
        db_session.add(employee)
    db_session.commit()
    assert len(db_session.query(models.Employee).all()) == 2
