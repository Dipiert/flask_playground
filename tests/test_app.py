from flask import Flask
import pytest
from flask_playground.app import app as _app
from test_db import connection, setup_database, db_session

@pytest.fixture()
def app():
    _app.config.update({
        "TESTING": True,
    })
    yield _app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_example(client, db_session):

    response = client.post("/user/new", json={
        'user': 'dam',
        'password': 'dam',
    })
    assert response.status_code, 200

# TODO: test that user and pwd fields are mandatory in post json msg