import os
import tempfile
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from flaskr import create_app
from flaskr.db import get_db, get_engine

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test',
        'DATABASE': db_path,
    })

    with app.app_context():
        project_root = Path(__file__).resolve().parents[1]
        config = Config(str(project_root / 'alembic.ini'))
        # Keep pytest's logging handlers when Alembic loads env.py.
        config.attributes['skip_logging_config'] = True
        with get_engine().begin() as connection:
            config.attributes['connection'] = connection
            command.upgrade(config, 'head')
        get_db().executescript(_data_sql)

    try:
        yield app
    finally:
        app.extensions['sqlalchemy_engine'].dispose()
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
