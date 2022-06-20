import unittest
import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_playground import models
import os
import pytest as pytest


@pytest.fixture(scope='session')
def connection():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '..', 'settings.env'))
    DB_USER = config['test_db']['user']
    DB_PASS = config['test_db']['pass']
    DB_HOST = config['test_db']['host']
    DB_PORT = config['test_db']['port']
    DB_NAME = config['test_db']['name']
    engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
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
