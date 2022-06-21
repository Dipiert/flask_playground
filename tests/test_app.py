from flask import Flask
import pytest
from flask_playground.app import app as _app
from test_db import connection, setup_database, db_session
import uuid
from unittest import mock
import flask_playground.db


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


def test_users_can_be_created(client, connection):
    response = client.post("/user/new", json={
        'user': 'dam',
        'password': 'dam',
    })
    assert response.status_code, 200


def test_app_factory(app):
    assert isinstance(app, Flask)


def test_user_succesfully_created_when_it_doesnt_exist(client, db_session):
    response = client.post("/user/new", json={
        'user': str(uuid.uuid4())[:35],
        'password': 'x',
    })
    assert 'successfully' in response.json.get('message')


@mock.patch.object(flask_playground.app, 'get_user_by_username')
def test_usernames_are_unique(get_user_by_username, client, db_session):
    get_user_by_username.return_value = True
    response = client.post("/user/new", json={
        'user': 'x',
        'password': 'x',
    })
    assert 'already exists' in response.json.get('message')

# TODO: test that user and pwd fields are mandatory in post json msg